import pandas as pd
from bs4 import BeautifulSoup
import requests
import logging
import pymongo
from flask import Flask, render_template

# Configure the logger to save logs to a file
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Remove the existing logger
logger = logging.getLogger()
logger.handlers = []

# Add a new handler to save logs to both console and file
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

# Function to extract Product Title
def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": "productTitle"}).text.strip()
    except AttributeError:
        title = ""
    return title

# Function to extract Product Price
def get_price(soup):
    try:
        price = soup.find("span", attrs={"class": "a-price"}).find("span", attrs={"class":"a-offscreen"}).text.strip()
        return price
    except AttributeError:
        return ""

# Function to get the Rating
def get_rating(soup):
    try:
        rating = soup.find("i", attrs={"class": "a-icon-star"}).text.strip()
        return rating
    except AttributeError:
        return ""

# Function to get the Review
def get_review(soup):
    try:
        review = soup.find("span", attrs={"id": "acrCustomerReviewText"}).text.strip()
        return review
    except AttributeError:
        return ""

def scrape_amazon(url):
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    webpage = requests.get(url, headers=HEADER)
    soup = BeautifulSoup(webpage.content, "html.parser")
    logging.info("Scraping webpage: %s", url)

    links = soup.find_all("a", attrs={"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
    del links[:1]
    logging.debug("Found %d product links", len(links))

    links_list = []

    for link in links:
        links_list.append(link.get("href"))

    container = {"Title": [], "Price": [], "Ratings": [], "Reviews": []}

    for link in links_list:
        products_link = link if link.startswith("https://") else "https://www.amazon.de" + link
        new_webpage = requests.get(products_link, headers=HEADER)
        new_soup = BeautifulSoup(new_webpage.content, "html.parser")

        container["Title"].append(get_title(new_soup))
        container["Price"].append(get_price(new_soup))
        container["Ratings"].append(get_rating(new_soup))
        container["Reviews"].append(get_review(new_soup))
        logging.info("Scraped product: %s", container["Title"][-1])

    if container["Title"]:  # Check if container is not empty
        amazon_df = pd.DataFrame.from_dict(container)
        amazon_df.to_csv("amazon_data.csv", header=True, index=False)

        # MongoDB Integration
        client = pymongo.MongoClient("mongodb+srv://rslan2033:pwskills@cluster0.vcwjdqv.mongodb.net/Amazon_scrapper?retryWrites=true&w=majority")
        db = client["Amazon_scrapper"]
        coll = db["scrapper_amazon_project"]
        coll.insert_one(container)

    return container

@app.route('/')
def index():
    # Load CSV data into DataFrame
    amazon_df = pd.read_csv("amazon_data.csv")
    # Convert DataFrame to HTML table
    table_html = amazon_df.to_html(index=False)
    return render_template('index.html', table=table_html)

if __name__ == "__main__":
    url = "https://www.amazon.de/s?k=playstation+5&crid=2AAXQU3GXNXKC&sprefix=play%2Caps%2C84&ref=nb_sb_ss_ts-doa-p_1_4"
    logger.info("Starting scraping process")
    data = scrape_amazon(url)
    logger.info("Scraping process completed")
    app.run(debug=True)
