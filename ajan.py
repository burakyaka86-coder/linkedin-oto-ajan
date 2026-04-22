import os
import requests
import g4f
from duckduckgo_search import DDGS
import urllib.parse

MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/q2bn0ph88q1qxu841sv9dhau8aql51gc"

def internette_arastirma_yap():
    try:
        with DDGS() as ddgs:
            results = ddgs.news("Endüstri 4.0 yapay zeka üretim yönetimi", region="tr-tr", timelimit="d")
            for r in results:
                return r['title'], r['body'], r['url']
    except Exception as e:
        print(f"Araştırma hatası: {e}")
    return None, None, None

def vizyoner_yorum_olustur(baslik, ozet):
    prompt = f"""
    Sen 'Companies That Value Employees' yöneticisisin. 
    Aşağıdaki haberi vizyoner bir dille analiz et. 
    Format: Giriş, Endüstri 4.0 Analizi, Kapanış Mesajı ve 3 Hashtag.
    Haber: {baslik} - {ozet}
    """
    try:
        response = g4f.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
        return response.strip()
    except:
        return None

def ucretsiz_resim_uret(baslik):
    # Habere uygun bir resim prompt'u oluşturup ücretsiz servisten link alıyoruz
    prompt = f"Industrial Industry 4.0, Artificial Intelligence, factory of the future, high tech, professional digital art, {baslik}"
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42&model=flux"
    return image_url

if __name__ == "__main__":
    baslik, ozet, link = internette_arastirma_yap()
    if baslik:
        yorum = vizyoner_yorum_olustur(baslik, ozet)
        resim_linki = ucretsiz_resim_uret(baslik)
        
        if yorum:
            # Make.com'a artık metinle birlikte üretilen resmin linkini de gönderiyoruz
            payload = {
                "metin": yorum,
                "link": link,
                "resim": resim_linki
            }
            requests.post(MAKE_WEBHOOK_URL, json=payload)
            print("Metin ve ücretsiz görsel Make.com'a fırlatıldı!")
