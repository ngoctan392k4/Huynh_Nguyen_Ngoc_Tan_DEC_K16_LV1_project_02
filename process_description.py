import json
import re
import os
from tqdm import tqdm

input_folder = "output_raw"
output_folder = "output"


def clean_description_and_extract_images(description):
    images_in_description = []

    # Find all image links in the description
    img_links = re.findall(r'<img[^>]*src="([^"]+)"', description)
    images_in_description.extend(img_links)

    # replace <br /> with \n
    description = re.sub(r'<br />', '\n', description, flags=re.IGNORECASE)

    # Replace <p> và </p> with \n
    description = re.sub(r'</p>|<p>', '\n\n', description, flags=re.IGNORECASE)

    # Replace <li> with "- ", </li> with \n
    description = re.sub(r'<li>', '- ', description, flags=re.IGNORECASE)
    description = re.sub(r'</li>', '\n', description, flags=re.IGNORECASE)

    # Remove all remaining html tag
    description = re.sub(r'<[^>]+>', '', description)

    # remove unnecessary blank lines
    description = re.sub(r'\n\s*\n', '\n', description)
    description = description.strip()

    return description, images_in_description

if __name__ == "__main__":
    # Get all json file
    file_list = [f for f in os.listdir(input_folder) if f.endswith(".json")]


    for filename in tqdm(file_list):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # Load data
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Process each product
        for product in data:
            desc = product.get("description", "")
            cleaned_desc, new_images = clean_description_and_extract_images(desc)

            # Update description
            product["description"] = cleaned_desc

            # Add images from description to existing images
            if new_images:
                product["images"].extend(new_images)
                product["images"] = list(dict.fromkeys(product["images"]))  # Remove duplicate

        # Write to another file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print("DONE")
