import os
import requests
import g4f
from duckduckgo_search import DDGS
import urllib.parse

# Make.com Webhook URL (Linkin sonunda boşluk olmadığından emin ol)
MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/q2bn0ph88q1qxu841sv9dhau8aql51gc"

def internette_arastirma_yap():
    print("İnternette araştırılıyor...")
    try:
        with DDGS() as ddgs:
            # Endüstri 4.0 ve Yapay Zeka odaklı güncel haberleri arar
            results = ddgs.news("Endüstri 4.0 yapay zeka üretim yönetimi", region="tr-tr", timelimit="d")
            for r in results:
                return r['title'], r['body'], r['url']
    except Exception as e:
        print(f"Araştırma hatası: {e}")
    return None, None, None

def vizyoner_yorum_olustur(baslik, ozet):
    print("Vizyoner analiz oluşturuluyor...")
    prompt = f"""
    Sen 'Companies That Value Employees' yöneticisi Burak Yaka'sın. 
    Aşağıdaki gelişmeyi dijital dönüşüm ve Endüstri 4.0 perspektifinden analiz et. 
    Profesyonel, vizyoner ve çarpıcı bir dil kullan. 
    Analizini 3 hashtag ile bitir.
    Haber: {baslik} - {ozet}
    """
    try:
        response = g4f.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
        return response.strip()
    except Exception as e:
        print(f"Metin oluşturma hatası: {e}")
        return None

def ucretsiz_resim_uret(baslik):
    print("Ücretsiz görsel üretiliyor...")
    # Make.com'un resim olarak algılaması için prompt sonuna .jpg ekliyoruz
    prompt = f"Industrial Industry 4.0, Artificial Intelligence, high-tech factory, professional digital art, {baslik}"
    encoded_prompt = urllib.parse.quote(prompt)
    # nologo ve format zorlaması ile doğrudan resim dosyası döndürülür
    return f"https://pollinations.ai/p/{encoded_prompt}.jpg?width=1024&height=1024&seed=42&model=flux&nologo=true"

if __name__ == "__main__":
    baslik, ozet, link = internette_arastirma_yap()
    if baslik:
        yorum = vizyoner_yorum_olustur(baslik, ozet)
        resim_linki = ucretsiz_resim_uret(baslik)
        
        if yorum:
            payload = {
                "baslik": baslik,
                "metin": yorum,
                "resim": resim_linki,
                "kaynak_link": link
            }
            
            clean_url = MAKE_WEBHOOK_URL.strip()
            print(f"Veri fırlatılıyor: {clean_url}")
            
            try:
                # 10 saniye timeout ekleyerek sistemin asılı kalmasını önlüyoruz
                response = requests.post(clean_url, json=payload, timeout=15)
                print(f"Make.com Yanıt Kodu: {response.status_code}")
                print(f"Make.com Mesajı: {response.text}")
                
                if response.status_code == 200:
                    print("!!! BAŞARILI: Veri Make.com'a ulaştı ve kabul edildi. !!!")
                else:
                    print(f"Hata: Make.com {response.status_code} hatası verdi. Bağlantıları kontrol et.")
            except Exception as e:
                print(f"Gönderim hatası: {e}")
    else:
        print("Bugün yeni bir haber bulunamadı.")
