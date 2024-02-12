import csv
from bs4 import BeautifulSoup
import requests
import pandas as pd



# Function to extract Product Title
def get_title(soup):
    try:
        #Outer Tag Object
        title = soup.find("span" , attrs={"id":"productTitle"})

        # Inner NavigatableString Object
        title_value = title.text

        #Title as a string value
        title_string = title_value.strip()
    except AttributeError:
        title_string = ""

    return title_string

#Function to extract Product Price
def get_price(soup):
    try:
        # Extract the preis
        price = soup.find("span", attrs={"class": "a-price aok-align-center reinventPricePriceToPayMargin priceToPay"}).string.strip()
        return price
    except AttributeError:
        price = ""




# Function to get the Rating
def get_rating(soup):
    try:
        rating = new_soup.find("i",attrs={"class": "a-icon a-icon-star a-star-4-5 cm-cr-review-stars-spacing-big"}).string.strip()
        return rating
    except AttributeError:
        rating =""



def get_review(soup):
    try:
        review= new_soup.find("span", attrs={"id": "acrCustomerReviewText"}).text.strip()
        return review


    except AttributeError:
        review=""



# Start the Scraping
if __name__ =="__main__":

    #The webpage URL
    url = "https://www.amazon.de/s?k=playstation+5&crid=2AAXQU3GXNXKC&sprefix=play%2Caps%2C84&ref=nb_sb_ss_ts-doa-p_1_4"

    # adding the user Agent
    HEADER = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})

    # HTTP Request
    webpage = requests.get(url, headers=HEADER)

    #Finding the main Soup
    soup = BeautifulSoup(webpage.content , "html.parser")

    #Fetch links as List of Tag Objects
    links = soup.find_all("a", attrs={"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})

    #deleting the first to adds
    del(links[:1])

    #Store the links
    links_list =[]

    #Loop for extracting the whole links
    for link in links:
        links_list.append(link.get("href"))

    #Bulding a Container to store the Data as Dict.
    container = {"Title":[] , "Price":[] , "Ratings":[] , "Reviews":[]}

    #Loop for extracting Details from links_list
    for link in links_list:
        products_link = link if link.startswith("https://") else "https://www.amazon.de" + link

        new_webpage = requests.get(products_link , headers=HEADER)
        new_soup = BeautifulSoup(new_webpage.content , "html.parser")

        #Function Calls to display all necessary product information
        container["Title"].append(get_title(new_soup))
        container["Price"].append(get_price(new_soup))
        container["Ratings"].append(get_rating(new_soup))
        container["Reviews"].append(get_review(new_soup))

    amazon_df = pd.DataFrame.from_dict(container)
    amazon_df.to_csv("amazon_data.csv", header=True, index=False)



