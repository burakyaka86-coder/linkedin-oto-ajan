import os
import requests
import g4f
from duckduckgo_search import DDGS
import time

# LinkedIn Token ve Şirket ID (Gemini API'ye gerek yok, g4f kullanıyoruz)
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
COMPANY_ID = "106153442"

def internette_arastirma_yap(sorgu="Endüstri 4.0 ve Yapay Zeka güncel gelişmeler 2026"):
    """DuckDuckGo üzerinden internette gerçek zamanlı araştırma yapar"""
    print(f"İnternette araştırılıyor: {sorgu}")
    haberler = []
    try:
        with DDGS() as ddgs:
            # En son haberleri (son 24 saat/hafta) getirir
            results = ddgs.news(sorgu, region="tr-tr", safesearch="off", timelimit="w")
            for r in results:
                haberler.append({
                    "baslik": r['title'],
                    "ozet": r['body'],
                    "link": r['url']
                })
                if len(haberler) >= 1: break # En güncel 1 tanesini alması yeterli
    except Exception as e:
        print(f"Araştırma hatası: {e}")
    return haberler[0] if haberler else None

def vizyoner_yorum_olustur(haber_baslik, haber_ozet):
    """Bulunan gelişmeyi GPT-4 altyapısıyla profesyonelce yorumlar"""
    prompt = f"""
    Sen endüstriyel bakım, üretim yönetimi ve Yapay Zeka (Endüstri 4.0) alanında dünya çapında vizyona sahip bir uzmansın. 
    Aşağıdaki güncel gelişmeyi internetten buldum. Bu gelişmeyi analiz et ve LinkedIn şirket sayfan için 
    takipçilerini dijital dönüşüme teşvik edecek, agresif, zeki ve vizyoner bir metne dönüştür. 
    
    HABER BAŞLIĞI: {haber_baslik}
    HABER DETAYI: {haber_ozet}
    
    Yazım dili Türkçe olsun. Profesyonel bir üslup kullan. Sonuna 3-4 adet stratejik hashtag ekle.
    """
    
    for attempt in range(3):
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
            )
            if response and len(response) > 50:
                return response.strip()
        except:
            print("YZ meşgul, 10 saniye sonra tekrar denenecek...")
            time.sleep(10)
    return None

def linkedin_paylas(text, link):
    """Şirket sayfasında paylaşım yapar"""
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "author": f"urn:li:organization:{COMPANY_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "ARTICLE",
                "media": [{"status": "READY", "originalUrl": link}]
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 201:
        print("BAŞARILI: İnternetten araştırılan güncel konu paylaşıldı.")
    else:
        print(f"Hata: {res.text}")

if __name__ == "__main__":
    print("Araştırmacı Ajan uyanıyor...")
    
    # Arama terimini istediğin gibi özelleştirebilirsin
    guncel_gelisme = internette_arastirma_yap("Endüstri 4.0 üretim yönetimi yapay zeka inovasyon")
    
    if guncel_gelisme:
        print(f"Bulunan konu: {guncel_gelisme['baslik']}")
        yorum = vizyoner_yorum_olustur(guncel_gelisme['baslik'], guncel_gelisme['ozet'])
        
        if yorum:
            print("Yorum hazır, LinkedIn'e gönderiliyor...")
            linkedin_paylas(yorum, guncel_gelisme['link'])
        else:
            print("Yorum oluşturulamadı.")
    else:
        print("İnternette güncel bir gelişme bulunamadı.")
