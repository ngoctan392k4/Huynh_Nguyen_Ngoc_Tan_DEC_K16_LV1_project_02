import csv
import logging
import os
import json

# save product in the current batch into the .json file
def save_batch_data(data, batch_num):
    os.makedirs("data", exist_ok=True)
    with open(f"data/products_batch_{batch_num}.json", "w", encoding="utf-8") as wf:
        json.dump(data, wf, ensure_ascii=False, indent=2)
    logging.info(f"Have saved {len(data)} products in batch {batch_num} into data/products_batch_{batch_num}.json")

# save all product ids that receive http error
def save_http_error(data):
    os.makedirs("data/error", exist_ok=True)
    check_not_exist = not os.path.exists("data/error/http_error.csv")
    with open("data/error/http_error.csv", "a", encoding="utf-8", newline="") as wf:
        writer = csv.writer(wf)
        if check_not_exist:
            writer.writerow(["product_id", "code"])
        for pd_id, code in data:
            writer.writerow([pd_id, code])
    logging.info(f"Have saved {len(data)} HTTP errors into data/error/http_error.csv")

# save all product ids that receive 404 not found error
def save_404_error(data):
    os.makedirs("data/error", exist_ok=True)
    check_not_exist = not os.path.exists("data/error/error_404_code.csv")
    with open("data/error/error_404_code.csv", "a", encoding="utf-8", newline="") as wf:
        writer = csv.writer(wf)
        if check_not_exist:
            writer.writerow(["product_id", "code"])
        for pd_id, code in data:
            writer.writerow([pd_id, code])
    logging.info(f"Have saved {len(data)} \"404\" errors into data/error/error_404_code.csv")

# save all product ids that receive timeout error => fetch again later
def save_timeout_error(data):
    os.makedirs("data/error", exist_ok=True)
    check_not_exist = not os.path.exists("data/error/timeout_error.csv")
    with open("data/error/timeout_error.csv", "a", encoding="utf-8", newline="") as wf:
        writer = csv.writer(wf)
        if check_not_exist:
            writer.writerow(["product_id"])
        for pd_id in data:
            writer.writerow([pd_id])
    logging.info(f"Have saved {len(data)} timeout errors into data/error/timeout_error.csv")


# save checkpoint - prevent unexpected error like server die, network error,....
def save_checkpoint(checkpoint_batch):
    os.makedirs("data/checkpoint", exist_ok=True)
    with open("data/checkpoint/checkpoint.txt", "w", encoding="utf-8") as wf:
        wf.write(str(checkpoint_batch))