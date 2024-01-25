import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
import json
import os
from datetime import datetime

# Directory paths for saving JSON and image files
json_folder_path = "./generated/json/"
images_folder_path = "./generated/images/"
# URL to scrape
url = "https://www.camelcodes.net/books/"


def create_folder_if_not_exists(folder_path):
    """Create a folder if it does not exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def save_json_file(scraped_data):
    """Save the scraped data to a JSON file."""
    with open(os.path.join(json_folder_path, 'data.json'), 'w') as json_file:
        json.dump(scraped_data, json_file, indent=4)
        print("Data saved to JSON file data.json")


def fetch_and_resize_image(image_url):
    """Fetch an image from a URL, resize it, and save it locally."""
    response = requests.get(image_url)
    image_data = response.content
    image = Image.open(BytesIO(image_data))
    image.thumbnail((400, 300))

    file_name = os.path.basename(image_url)
    file_path = os.path.join(images_folder_path, file_name)
    image.save(file_path, format="jpeg")
    return file_name


def main():
    """Main function to scrape book data and save it."""
    start_time = time.time()

    # Create necessary folders
    create_folder_if_not_exists(json_folder_path)
    create_folder_if_not_exists(images_folder_path)

    # Fetch HTML content from the URL
    print(f'Downloading html page: {url} ...')
    response = requests.get(url)
    html = response.content

    # Parse HTML using BeautifulSoup
    print('Parsing HTML file ...')
    soup = BeautifulSoup(html, 'html.parser')
    books = soup.find_all('div', class_='kg-product-card-container')

    # List to store scraped book data
    scraped_data = []

    # Iterate over each book and extract data
    for book in books:
        title_tag = book.find('h4', class_='kg-product-card-title')
        title = title_tag.text.strip() if title_tag else 'No Title'

        rating_stars = book.find_all('span', class_='kg-product-card-rating-star')
        rating_stars_active = book.find_all('span', class_='kg-product-card-rating-active')
        rating = f"{len(rating_stars_active)}/{len(rating_stars)}"

        description_tag = book.find('div', class_='kg-product-card-description')
        description = description_tag.text.strip() if description_tag else 'No Description'

        image_tag = book.find('img', class_='kg-product-card-image')
        original_image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''

        buy_link_tag = book.find('a', class_='kg-product-card-button', href=True)
        buy_link = buy_link_tag['href'] if buy_link_tag else ''

        print(f'Fetching and resizing image {os.path.basename(original_image_url)} ...')
        thumbnail = fetch_and_resize_image(original_image_url)

        # Append book data to the list
        scraped_data.append({
            'title': title,
            'rating': rating,
            'description': description,
            'original_image_url': original_image_url,
            'thumbnail_image': thumbnail,
            'buy_link': buy_link,
            'last_update_date': datetime.now().isoformat()
        })

    # Save scraped data to JSON
    print('Writing JSON file ...')
    save_json_file(scraped_data)

    # Calculate and print elapsed time
    elapsed_time = time.time() - start_time
    print(f"Took: {elapsed_time:.2f} seconds")


if __name__ == '__main__':
    print('Booting up...')
    main()
