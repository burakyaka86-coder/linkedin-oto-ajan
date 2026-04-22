import os
import requests
import feedparser
from google import genai

# Çevre Değişkenlerinden API Şifrelerini Çek
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Hedef Şirket Sayfasının ID'si
COMPANY_ID = "106153442" 

# Haber kaynağı (Küresel ve GitHub sunucularını engellemeyen bir teknoloji RSS'i)
RSS_URL = "https://www.webtekno.com/rss.xml" 

def get_latest_news():
    """RSS kaynağından en son haberi çeker"""
    try:
        feed = feedparser.parse(RSS_URL)
        if feed.entries:
            latest = feed.entries[0]
            return latest.title, latest.description, latest.link
    except Exception as e:
        print(f"RSS Çekme Hatası: {e}")
    return None, None, None

def generate_linkedin_post(title, summary):
    """Gemini ile haberi vizyoner bir LinkedIn gönderisine dönüştürür"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = f"""
        Sen endüstriyel bakım, üretim yönetimi ve Yapay Zeka entegrasyonu (Endüstri 4.0) alanında uzman, vizyoner bir profesyonelsin. 
        Aşağıdaki teknoloji haberini oku ve yönettiğin şirket sayfası için profesyonel, vizyoner ve dikkat çekici bir LinkedIn gönderi metnine dönüştür. 
        Metin Türkçe olsun, okuyucuyu dijital dönüşüm ve inovasyon üzerine düşündürsün ve sonuna 3-4 adet alakalı hashtag ekle.
        
        Haber Başlığı: {title}
        Haber Özeti: {summary}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Hatası: {e}")
        return "Yapay zeka metni oluşturamadı."

def share_on_company_page(org_id, text, link):
    """Metni ve haberi şirket sayfası adına LinkedIn'de paylaşır"""
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    payload = {
        "author": f"urn:li:organization:{org_id}",
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
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print("Harika! Gönderi şirket sayfasında başarıyla paylaşıldı.")
    else:
        print("LİNKEDİN PAYLAŞIM HATASI!!! Lütfen aşağıdaki detayı kontrol et:")
        print(response.text)

if __name__ == "__main__":
    print("Otonom Ajan uyanıyor...")
    
    news_title, news_desc, news_link = get_latest_news()
    
    if news_title:
        print(f"Haber bulundu: {news_title}")
        post_text = generate_linkedin_post(news_title, news_desc)
        
        if post_text and post_text != "Yapay zeka metni oluşturamadı.":
            print("Gemini metni hazırladı, LinkedIn şirket sayfasına gönderiliyor...")
            share_on_company_page(COMPANY_ID, post_text, news_link)
        else:
            print("Metin oluşturulamadığı için paylaşım iptal edildi.")
    else:
        print("Yeni haber bulunamadı veya RSS kaynağına ulaşılamadı.")
