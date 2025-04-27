# PROJECT 2: Download data of 200000 products of Tiki by using Python and API
# Overview
## Problems
- Using Python code, download information of 200.000 products of Tiki and save them as .json files. Each file has information of about 1000 products. The information to be retrieved includes: id, name, url_key, price, description, images url. Require standardizing the content in "description" and finding a way to shorten the time to retrieve data.
- List product_id: https://1drv.ms/u/s!AukvlU4z92FZgp4xIlzQ4giHVa5Lpw?e=qDXctn
- API get product detail: https://api.tiki.vn/product-detail/api/v1/products/138083218

## Folders structure
- **.venv folder** contains virtual environment including library to run this project
- **output_raw folder** contains raw data from API including the data of each products and the product id which cannot fetch due to 404 error or timeout error
- **output folder** contains all product data after normalizing the description including: finding all image links in the description, replacing ```<br />``` with "\n", replacing ```<p>``` and ```</p>``` with "\n", replacing ```<li>``` with "- " and ```</li>``` with "\n", removing all remaining html tag

# Process
First, run ```collect_data.py``` to fetch data for all products through id_product.csv. <br />
Second, run ```process_description.py``` to normalize the html tags and extract image sources in the description and add them to the images field

# Performance
## The first data collection
Have saved 942 products into output_raw/product_part199.json  <br />
Have saved 1001 HTTP errors into output_raw/error/http_error.json <br />
Have saved 57 TIMEOUT errors into output_raw/error/timeout_error.csv <br />

Completed in 4976.48 seconds 

## The second data collection
Have saved 57 HTTP errors into output_raw/error/http_error_2.json <br />
Have saved 0 TIMEOUT errors into output_raw/error/timeout_error_2.csv <br />

Completed in 19.21 seconds

## Processing description
Completed in 30-40 seconds

## Summary
The total amount of time: approximately 5035s, which is roughly 83-84 minutes (1 hour and 24 minutes)

# Result 
198942 products are collected  <br />
1058 product ids contain 404: Not Found error
