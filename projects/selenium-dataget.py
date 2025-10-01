"""Script to scrape servant data from a wiki page."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from typing import List
import time
# ----------------------------------------------------------------- #


# ---------------------------------------->>  CONSTANTS START <<-----
WIKI_URL: str = "WIKI URL GOES HERE"
WIKI_TABLE_CLASS: str = "wikitable sortable jquery-tablesorter"
PAGE_WAIT_TIME: int = 20



# ----------------------------------------------------->> FUNCTION DEFINITIONS START <<-----
def initialise_driver(headless: bool) -> webdriver.Chrome:
    """
    Initialize the Chrome driver with options.

    Args:
        headless (bool): Whether to run Chrome in headless mode.

    Returns:
        webdriver.Chrome: A Chrome WebDriver instance.
    """
    options = Options()
    options.headless = headless
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(3)
    return driver


def rid_popup(driver: webdriver.Chrome) -> None:
    """
    Attempts to close popups if they appear on the page.

    Args:
        driver (webdriver.Chrome): The active WebDriver instance.
    """
    try:
        popup = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, '_2o0')]"))
        )
        popup.click()
        print("Popup closed (first type).")
    except Exception:
        try:
            consent = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.NAME, "data-tracking-opt-in-accept"))
            )
            consent.click()
            print("Popup closed (second type).")
        except Exception:
            print("No popup found.")


def get_servants(driver: webdriver.Chrome) -> List[dict]:
    """
    Scrapes the servant names and rarities from the wiki page.

    Args:
        driver (webdriver.Chrome): The active WebDriver instance.

    Returns:
        List[dict]: List of servants with their name and rarity.
    """
    servant_list = []

    table = WebDriverWait(driver, PAGE_WAIT_TIME).until(
        EC.presence_of_element_located((By.CLASS_NAME, WIKI_TABLE_CLASS))
    ).find_element(By.TAG_NAME, "tbody")

    table_rows = table.find_elements(By.TAG_NAME, "tr")

    for index, row in enumerate(table_rows):
        try:
            first_td = row.find_element(By.TAG_NAME, "td")
            servant_link = first_td.find_element(By.CSS_SELECTOR, "a[title]")
            servant_name = servant_link.get_attribute("title")

            rarity_cell = row.find_elements(By.TAG_NAME, "td")[2]
            star_amount = rarity_cell.text
            rarity = len(star_amount.replace(" ", ""))

            servant_info = {
                "name": servant_name,
                "rarity": rarity,
                "index": index
            }
            servant_list.append(servant_info)

            print(f"{servant_name} | Rarity: {rarity} stars | Row {index}")

        except Exception as e:
            print(f"Skipping row {index}: {e}")

    return servant_list


def main() -> None:
    """Main function to run the script."""
    driver = initialise_driver(headless=False)

    try:
        driver.get(WIKI_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        rid_popup(driver)
        servants = get_servants(driver)
        print(f"\nTotal servants scraped: {len(servants)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
