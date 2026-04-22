import os
import requests
import g4f
from duckduckgo_search import DDGS
import urllib.parse

# Linki buraya yapıştırırken başında veya sonunda boşluk kalmadığından emin ol
MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/q2bn0ph88q1qxu841sv9dhau8aql51gc"

def internette_arastirma_yap():
    print("İnternette araştırılıyor...")
    try:
        with DDGS() as ddgs:
            results = ddgs.news("Endüstri 4.0 yapay zeka üretim yönetimi", region="tr-tr", timelimit="d")
            for r in results:
                return r['title'], r['body'], r['url']
    except Exception as e:
        print(f"Araştırma hatası: {e}")
    return None, None, None

def vizyoner_yorum_olustur(baslik, ozet):
    prompt = f"Sen 'Companies That Value Employees' yöneticisisin. Bu gelişmeyi vizyoner bir dille Türkçe analiz et ve 3 hashtag ekle: {baslik} - {ozet}"
    try:
        response = g4f.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
        return response.strip()
    except:
        return None

def ucretsiz_resim_uret(baslik):
    prompt = f"Industrial Industry 4.0, Artificial Intelligence, modern factory, {baslik}"
    encoded_prompt = urllib.parse.quote(prompt)
    return f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42&model=flux"

if __name__ == "__main__":
    baslik, ozet, link = internette_arastirma_yap()
    if baslik:
        yorum = vizyoner_yorum_olustur(baslik, ozet)
        resim_linki = ucretsiz_resim_uret(baslik)
        
        if yorum:
            payload = {
                "baslik": baslik,
                "metin": yorum,
                "resim": resim_linki
            }
            
            # .strip() ile linkteki gizli boşlukları temizliyoruz
            clean_url = MAKE_WEBHOOK_URL.strip()
            
            print(f"Veri gönderiliyor: {clean_url}")
            try:
                response = requests.post(clean_url, json=payload, timeout=10)
                print(f"Make.com Yanıt Kodu: {response.status_code}")
                print(f"Make.com Mesajı: {response.text}")
                
                if response.status_code == 200:
                    print("!!! BAŞARILI: Veri Make.com'a ulaştı. !!!")
                else:
                    print("Hata: Make.com veriyi kabul etmedi.")
            except Exception as e:
                print(f"Gönderim sırasında teknik hata oluştu: {e}")
