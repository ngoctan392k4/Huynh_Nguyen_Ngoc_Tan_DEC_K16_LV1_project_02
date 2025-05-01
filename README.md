# PROJECT 2: Download data of 200000 products of Tiki though API by using Python
# Overview
## Problems
- Using Python code, download information of 200.000 products of Tiki and save them as .json files. Each file has information of about 1000 products. The information to be retrieved includes: id, name, url_key, price, description, images url. Require standardizing the content in "description" and finding a way to shorten the time to retrieve data.
- List product_id: https://1drv.ms/u/s!AukvlU4z92FZgp4xIlzQ4giHVa5Lpw?e=qDXctn
- API get product detail: https://api.tiki.vn/product-detail/api/v1/products/138083218

## Folders structure
- **.venv folder** contains virtual environment including library to run this project
- **output_raw folder** contains raw data from API including the data of each products and the product id which cannot fetch due to 404 error or timeout error or other http errors
- **output_raw_2 folder** contains raw data from API including the data of each products from 404 error or timeout error or other http errors files (check again)
- **output folder** contains all product data after normalizing the description including: finding all image urls in the description, replacing ```<br />``` with "\n", replacing ```<p>``` and ```</p>``` with "\n", replacing ```<li>``` with "- " and ```</li>``` with "\n", removing all remaining html tag

## Collect_products.py structure:
- ```fetch_data()``` function: used to fetch data and return required information of each product ID
- ```collect_data()``` function: collect 1000 data per batch, then save product data, save errors, save check point
- ```batch_reader()``` function: reader input csv file such that one batch contains 1000 products (from the checkpoint batch)
- ```save_checkpoint()``` function: save checkpoint to continue fetching data if unexpected errors happens like network,...
- ```load_checkpoint()``` function: read the checkpoint to continue
- ```save.....error()``` function: save errors including: http, 404, timeout
- ```save_batch_product()``` function: save products per batch

# Process
First, run ```collect_data.py``` to fetch data for all products through id_product.csv. <br />
Second, run ```collect_data.py``` with http error, 404 error, timeout error to ensure that we get all data of valid IDs <br />
Third, run ```process_description.py``` to normalize the html tags and extract image sources in the description and add them to the images field

# Performance
## The first data collection
Completed in 5164.72 seconds <br />
198942 products are collected  <br />
1058 product ids contain 404: Not Found error <br />
0 product ids contains HTTP error (except for 404) <br />
0 product ids contains timeout error

## The second data collection with error files
### Fetching data with 404 error file
Completed in 21.66 seconds <br />
0 products are collected  <br />
1058 product ids contain 404: Not Found error <br />
0 product ids contains HTTP error (except for 404) <br />
0 product ids contains timeout error

### Fetching data with HTTP error file
Since there is no HTTP errors, so we do not need to fetch data again
### Fetching data with timeout error file
Since there is no timeout errors, so we do not need to fetch data again

## Processing description
Completed in 20.78 seconds

## Summary
The total amount of time: approximately 5207s, which is roughly 87 minutes (1 hour and 27 minutes)

# Result
198942 products are collected  <br />
1058 product ids contain 404: Not Found error <br />
0 product ids contains HTTP error (except for 404) <br />
0 product ids contains timeout error