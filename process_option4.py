import json
import re
import os
import requests
import tempfile
from urllib.parse import urlparse, urljoin
from firebase_config import setup_firebase, upload_to_firebase
from image_processing import process_image
import cv2

TARGET_COLOR = "#EBF3F3"
SKIP_IMAGE_URLS = [
    "additional-information-image",
    "alternate-methord-image",
    "confusion-points-image",
    "hinglish-image",
    "hint-text-image",
    "important-point-image",
    "in_news",
    "key-point-image",
    "mistake-point-image",
    "lms_creative_elements",
]

def normalize_url(url):
    if url.startswith("//"):
        return "https:" + url
    elif not url.startswith(("http:", "https:")):
        return "https://" + url
    return url

def should_skip_url(url):
    return any(skip_url in url for skip_url in SKIP_IMAGE_URLS)

def download_image(url, temp_dir):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        file_name = os.path.basename(urlparse(url).path)
        file_path = os.path.join(temp_dir, file_name)
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return file_path
    except requests.exceptions.RequestException as e:
        return None

def extract_image_urls(content):
    img_pattern = r'<img\s+[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>'
    return re.findall(img_pattern, content, re.IGNORECASE)

def process_option4(file_path, progress_callback, status_callback):
    try:
        bucket = setup_firebase()
    except Exception as e:
        status_callback.emit(f"Error setting up Firebase: {str(e)}")
        return False

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    updated = False
    total_items = len(data)
    
    for i, item in enumerate(data):
        if isinstance(item, str):
            image_urls = extract_image_urls(item)
            total_urls = len(image_urls)
            for j, old_url in enumerate(image_urls):
                normalized_url = normalize_url(old_url)
                if should_skip_url(normalized_url):
                    status_callback.emit(f"Skipping URL: {normalized_url}")
                    continue

                status_callback.emit(f"Processing image {j+1}/{total_urls} in item {i+1}/{total_items}")
                with tempfile.TemporaryDirectory() as temp_dir:
                    local_path = download_image(normalized_url, temp_dir)
                    if local_path:
                        try:
                            img = cv2.imread(local_path)
                            if img is None:
                                status_callback.emit(f"Error: Could not read the image at {local_path}")
                                continue

                            processed_img = process_image(img, TARGET_COLOR)
                            processed_path = os.path.join(temp_dir, f"processed_{os.path.basename(local_path)}")
                            cv2.imwrite(processed_path, processed_img)

                            file_name = os.path.basename(processed_path)
                            remote_path = f"migrated_images/{file_name}"
                            firebase_url = upload_to_firebase(bucket, processed_path, remote_path)

                            data[i] = data[i].replace(old_url, firebase_url)
                            updated = True
                            status_callback.emit(f"Processed and uploaded: {old_url} -> {firebase_url}")
                        except Exception as e:
                            status_callback.emit(f"Error processing {local_path}: {str(e)}")
                    else:
                        status_callback.emit(f"Failed to download: {normalized_url}")

                progress = int((i * total_urls + j + 1) / (total_items * total_urls) * 100)
                progress_callback.emit(progress)

    if updated:
        output_file = os.path.join(os.path.dirname(file_path), f"updated_{os.path.basename(file_path)}")
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        status_callback.emit(f"Updated file saved as: {output_file}")
        return True
    else:
        status_callback.emit("No changes were made to the file.")
        return False