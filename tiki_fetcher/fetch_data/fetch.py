import requests
import logging
import time
from .config import load_config

config = load_config()
log_cfg = config.get("LOGGING", {})

logging.basicConfig(
    level=getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO),
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_cfg["log_file"], encoding='utf-8'),
        logging.StreamHandler() if log_cfg.get("to_console", False) else logging.NullHandler()
    ]
)

def fetch_data(product_id):
    max_tries = config["MAX_TRIES"] # if catch errors, try again until attempt = max_tries
    timeout = config["TIMEOUT"]
    sleep_time = config["SLEEP_BEFORE_RETRIES"]
    headers = config["HEADERS"]
    api_url = config["API_URL"].format(product_id=product_id)

    for attempt in range(max_tries):
        try:
            # Ensure that we request API like a real person
            response = requests.get(api_url, headers=headers, timeout=timeout)

            if response.status_code == 200:
                data = response.json()

                # If images do not exist return empty
                images = data.get("images")
                if images and isinstance (images, list):
                    images_url = [img.get("base_url") for img in images if img.get("base_url")]
                else:
                    images_url = []

                return {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "url_key": data.get("url_key"),
                    "price": data.get("price"),
                    "description": data.get("description"),
                    "images": images_url
                }

            else:
                if response.status_code == 404:
                    return {
                        "status": "404_error",
                        "product_id": product_id,
                        "code": response.status_code
                    }
                else:
                    if attempt == max_tries - 1:
                        return {
                            "status": "http_error",
                            "product_id": product_id,
                            "code": response.status_code
                        }
                    else:
                        time.sleep(sleep_time)
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt+1} with product id {product_id}: {e}")
            if attempt == max_tries - 1:
                return {
                    "status": "timeout_error",
                    "product_id": product_id
                }
            else:
                time.sleep(sleep_time)