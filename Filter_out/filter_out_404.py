import json

files = ['output_raw/error/http_error.json', 'output_raw/error/http_error_2.json', 'output_raw/error/http_error_3.json']

product_ids_404 = []

for filename in files:
    with open(filename, 'r') as f:
        data = json.load(f)

        ids_404 = [item[0] for item in data if item[1] == 404]
        product_ids_404.extend(ids_404)

for pid in product_ids_404:
    print(pid)

with open('output/product_ids_404.txt', 'w') as f:
    for pid in product_ids_404:
        f.write(f"{pid}\n")

print(f"{len(product_ids_404)} IDs with 404: Not found error have been saved in output/product_ids_404.txt")