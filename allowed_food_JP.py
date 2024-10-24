from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pork import pork_names, non_pork
import re


def contains_pork(foods):
    # Convert ingredients to lower case
    foods_lower = [food.lower() for food in foods]

    # Check for pork ingredients
    for food in foods_lower:
        if any(pork in food for pork in pork_names):
            # Ensure it is not a non-pork alternative
            if not any(non_pork_item in food for non_pork_item in non_pork):
                return True
    return False

def scrape_foodsJP():
    # Path to your ChromeDriver executable

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensures Chrome runs in headless mode.
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model.
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems.

    # Heroku paths for ChromeDriver and Chrome binary
    chrome_bin_path = '/app/.apt/usr/bin/google-chrome'
    chrome_driver_path = '/app/.chromedriver/bin/chromedriver'

    # Set binary location
    chrome_options.binary_location = chrome_bin_path
    # Set up the ChromeDriver service
    service = Service(chrome_driver_path)

    # Set up the Selenium WebDriver with the correct path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Fetch the web page
    driver.get("https://usf.campusdish.com/LocationsAndMenus/Tampa/JuniperDining")

    # Wait for the page to fully load. Adjust time if necessary.
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-testid='product-card-description']")))

    # Get the page source
    page_to_scrape = driver.page_source

    # Parse the web page with Beautiful Soup
    soup = BeautifulSoup(page_to_scrape, "html.parser")

    # Find all restaurants
    ids = ["10993", "13890", "10997", "10996", "13889", "10995"]
    restaurants = []
    for element_id in ids:
        element = soup.find("div", id=element_id)
        if element:
            restaurants.append(element)

    foods_by_restaurant = []

    for restaurant in restaurants:
        # Extract restaurant name
        restaurant_name_tag = restaurant.find("h2", class_="sc-hHOBiw flydZD StationHeaderTitle")

        if restaurant_name_tag:
            restaurant_name = restaurant_name_tag.get_text().strip()
        else:
            restaurant_name = "Unknown"

        # Extract foods for this restaurant
        # food_items = restaurant.find_all("p", class_="sc-uVWWZ injihV ItemContent")
        food_items = restaurant.find_all("p", class_=lambda x: x and "ItemContent" in x)

        foods = [food.get_text().strip().lower() for food in food_items]

        # Check if the foods contain pork
        foods_with_pork_info = []
        for food in foods:
            contains_pork_flag = contains_pork([food])
            foods_with_pork_info.append({
                "food": food,
                "contains_pork": contains_pork_flag
            })

        foods_by_restaurant.append({
            "restaurant": restaurant_name,
            "foods": foods_with_pork_info
        })

    # Close the browser
    driver.quit()


    return foods_by_restaurant

