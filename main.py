"""Scrapes product data from Richer Sounds website and exports as .csv, run in cli for Rich to work"""

from bs4 import BeautifulSoup
import requests
from rich.progress import track
from rich.console import Console
import pandas as pd
import time
import random

console = Console()

# list of urls, variable uses range for pagination
source_urls = [f'https://www.richersounds.com/headphones/headphones/all-headphones.html?headphone_type=568&p={i}'for i in range(1, 8)]

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
}


def get_product_links(urls):
    """Args: list of product page urls (source_urls), Returns: list of product links"""
    product_links = []
    for page in urls:
        r = requests.get(page, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        product_links.extend([i.find('a')['href'] for i in soup.find_all('li', class_='item product product-item')])
    return product_links


def extract(links):
    """Args: List of product links, Returns: dict object containing product data, prints rich console output"""
    product_data = []
    for count, product in enumerate(track(links, total=len(links)), start=1):

        r = requests.get(product, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        try:
            title = soup.find('h1', class_='page-title').text.strip()
        except AttributeError:
            title = 'no title'
        try:
            description = soup.find('div', class_='product attribute category_description').text.strip()
        except AttributeError:
            description = 'no description'
        try:
            price = soup.find('span', class_='price').text.strip().replace('£', '')
        except AttributeError:
            price = None
        try:
            review_rating = soup.find('span', class_='bvseo-bestRating').text.strip()
        except AttributeError:
            review_rating = 'No Rating'
        try:
            review_count = soup.find('span', class_='bvseo-reviewCount').text.strip()
        except AttributeError:
            review_count = 'No Review'
        try:
            availability = soup.find('span', class_='availability').text.strip().lower()
        except AttributeError:
            availability = 'No Value'

        products = {
            'title': title,
            'description': description,
            'price': price,
            'review_rating': review_rating,
            'review_count': review_count,
            'availability': availability
        }
        product_data.append(products)

        console.print(f" Saving: {title} - {count} of {len(links)}")
        time.sleep(random.randint(1, 6))  # random sleep on request
    return product_data


def load(data):
    """Args: product data (list of dict's) Outputs .csv to local project dir"""
    df = pd.DataFrame(data)
    df.to_csv('richer_sounds.csv', index=False)

def main():
    links = get_product_links(source_urls)
    data = extract(links)
    load(data)


if __name__ == '__main__':
    main()
