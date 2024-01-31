import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from concurrent.futures import ThreadPoolExecutor
import re

def sanitize_folder_name(folder_name):
    # Windowsで使用できない文字をアンダースコアに置き換える
    return re.sub(r'[<>:"/\\|?*]', '_', folder_name)

def download_image(image_url, target_folder):
    try:
        img_data = requests.get(image_url).content
        filename = os.path.join(target_folder, image_url.split('/')[-1])
        with open(filename, 'wb') as file:
            file.write(img_data)
            print(f"Downloaded {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {image_url}: {e}")

def download_images(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find('title')
        if title_tag and title_tag.text.strip():
            folder_name = sanitize_folder_name(title_tag.text.strip())
        else:
            folder_name = "untitled"

        target_folder = os.path.join("downloaded_images", folder_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        img_tags = soup.find_all('img')
        image_urls = [urljoin(url, img.get('src')) for img in img_tags if img.get('src')]

        with ThreadPoolExecutor(max_workers=5) as executor:
            for img_url in image_urls:
                if img_url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    executor.submit(download_image, img_url, target_folder)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading images from {url}: {e}")

def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

file_path = "URL.txt"
urls = read_urls_from_file(file_path)
for url in urls:
    download_images(url)
