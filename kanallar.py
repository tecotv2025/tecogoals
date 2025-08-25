from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import requests
import os

# Yayın dosyaları
kanallar = {
    1: "yayin1.m3u8", 2: "yayinb2.m3u8", 3: "yayinb3.m3u8",
    4: "yayinb4.m3u8", 5: "yayinb5.m3u8", 6: "yayinbm1.m3u8",
    7: "yayinbm2.m3u8", 8: "yayinss.m3u8", 9: "yayinss2.m3u8",
    10: "yayinssp2.m3u8", 11: "yayint1.m3u8", 12: "yayint2.m3u8",
    13: "yayint3.m3u8", 14: "yayinsmarts.m3u8", 15: "yayinsms2.m3u8",
    16: "yayintrtspor.m3u8", 17: "yayintrtspor2.m3u8", 18: "yayinas.m3u8",
    19: "yayinatv.m3u8", 20: "yayintv8.m3u8", 21: "yayintv85.m3u8",
    22: "yayinnbatv.m3u8", 23: "yayinex1.m3u8", 24: "yayinex2.m3u8",
    25: "yayinex3.m3u8", 26: "yayinex4.m3u8", 27: "yayinex5.m3u8",
    28: "yayinex6.m3u8", 29: "yayinex7.m3u8", 30: "yayinex8.m3u8",
    31: "yayinzirve.m3u8"
}

def get_final_url_selenium(url):
    """Selenium ile kısa URL’nin yönlendirdiği son adresi bulur"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)
        final_url = driver.current_url
    except Exception as e:
        print(f"Selenium hatası: {e}")
        final_url = None
    finally:
        if driver:
            driver.quit()
    return final_url

def get_final_url_requests(url):
    """Requests ile yönlendirmeleri takip ederek son URL’yi bulur"""
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.url
    except requests.RequestException as e:
        print(f"Yönlendirme hatası: {e}")
        return None

def find_baseurl(page_url):
    """Sayfadan baseurl bilgisini çeker"""
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        match = re.search(r'const\s+baseurl\s*=\s*"([^"]+)"', response.text)
        if match:
            return match.group(1)
        return None
    except requests.RequestException as e:
        print(f"Base URL hatası: {e}")
        return None

def create_php_files(base_url):
    """Base URL ile tüm yayınlar için PHP yönlendirme dosyaları oluşturur"""
    os.makedirs("php_kanallar", exist_ok=True)
    for num, dosya in kanallar.items():
        stream_url = base_url + dosya
        php_content = f"""<?php
header("Location: {stream_url}");
exit;
?>"""
        with open(f"php_kanallar/yayin{num}.php", "w", encoding="utf-8") as f:
            f.write(php_content)
    print(f"{len(kanallar)} adet yönlendirme PHP dosyası 'php_kanallar' klasörüne kaydedildi.")

if __name__ == "__main__":
    short_url = "https://t.co/aOAO1eIsqE"

    print("Kısa URL’den ana adres bulunuyor...")
    site_url = get_final_url_selenium(short_url)
    print("Site ana adresi:", site_url)

    if site_url:
        channel_path = "channel.html?id=yayinzirve"
        if not site_url.endswith('/'):
            site_url += '/'
        full_url = site_url + channel_path
        print("Tam URL:", full_url)

        print("Son kanal URL'si bulunuyor...")
        final_channel_url = get_final_url_requests(full_url)
        print("Son kanal URL'si:", final_channel_url)

        if final_channel_url:
            base_url = find_baseurl(final_channel_url)
            if base_url:
                print("Base URL bulundu:", base_url)
                print("PHP yönlendirme dosyaları oluşturuluyor...")
                create_php_files(base_url)
            else:
                print("Base URL bulunamadı.")
        else:
            print("Kanal URL'si bulunamadı.")
    else:
        print("Selenium ile site URL’si alınamadı.")
