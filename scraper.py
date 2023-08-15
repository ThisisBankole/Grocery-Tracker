import csv
import requests
from bs4 import BeautifulSoup

def scrape_single_page():
    url = "https://uk.openfoodfacts.org/cgi/search.pl?search_terms=&search_simple=1&action=process"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('div', class_='list_product_content')

    product_names = [product.text.strip() for product in products]

    with open('grocery_items.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Product Name'])  # Header
        for product in product_names:
            writer.writerow([product])

    print("CSV creation complete!")

# Run the function
scrape_single_page()
