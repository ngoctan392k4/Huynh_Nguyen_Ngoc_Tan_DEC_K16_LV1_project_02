import json
import csv

files = ['output_raw/error/http_error.json', 'output_raw/error/http_error_2.json', 'output_raw/error/http_error_3.json']
product_ids_not404 = []

for filename in files:
    with open(filename, 'r') as f:
        data = json.load(f)

        ids_not404 = [item[0] for item in data if item[1] != 404]
        product_ids_not404.extend(ids_not404)

with open('Filter_out/pd_id_not_404.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['product_id'])
    for pd_id in product_ids_not404:
        writer.writerow([pd_id])

print("Have saved into Filter_out/pd_id_not_404.csv")