import os
import requests
import feedparser
import google.generativeai as genai

LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Endüstri, Teknoloji ve Yapay Zeka haberleri için örnek bir RSS kaynağı
RSS_URL = "https://www.donanimhaber.com/rss/teknoloji" 

def get_linkedin_urn():
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("sub")
    print("URN Alınamadı:", response.text)
    return None

def get_latest_news():
    feed = feedparser.parse(RSS_URL)
    if feed.entries:
        latest = feed.entries[0]
        return latest.title, latest.description, latest.link
    return None, None, None

def generate_linkedin_post(title, summary):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash') 
    
    prompt = f"""
    Sen endüstriyel bakım, üretim yönetimi ve Yapay Zeka entegrasyonu (Endüstri 4.0) alanında uzman, vizyoner bir profesyonelsin. 
    Aşağıdaki haberi oku ve kendi LinkedIn ağın için profesyonel, vizyoner ve dikkat çekici bir gönderi metnine dönüştür. 
    Metin Türkçe olsun, okuyucuyu dijital dönüşüm üzerine düşündürsün ve sonuna 3-4 adet alakalı hashtag ekle.
    
    Haber Başlığı: {title}
    Haber Özeti: {summary}
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def share_on_linkedin(urn, text, link):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    payload = {
        "author": f"urn:li:person:{urn}",
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
        print("Başarıyla Paylaşıldı!")
    else:
        print("Paylaşım Hatası:", response.text)

if __name__ == "__main__":
    print("Ajan uyanıyor...")
    my_urn = get_linkedin_urn()
    if my_urn:
        news_title, news_desc, news_link = get_latest_news()
        if news_title:
            print(f"Haber bulundu: {news_title}")
            post_text = generate_linkedin_post(news_title, news_desc)
            share_on_linkedin(my_urn, post_text, news_link)
        else:
            print("Yeni haber bulunamadı.")
