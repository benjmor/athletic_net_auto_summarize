import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from get_meet_results_for_school import get_meet_results_for_school


def get_school_results_for_year_and_sport(
    school_id,
    year,
    sport_name,
    meet_id=None,
    location_override=None,
    number_of_teams_override=None,
):
    team_results_dict = {}
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # chrome_options.binary_location = CHROME_PATH

    # Start a new browser session
    browser = webdriver.Chrome(options=chrome_options)
    results_browser = webdriver.Chrome(options=chrome_options)

    # Navigate to the page with the list of meets
    base_url = f"https://www.athletic.net/team/{school_id}/{sport_name}/{year}"
    browser.get(base_url)

    school_name = (
        browser.find_element(By.CLASS_NAME, "container.ng-star-inserted")
        .find_element(By.TAG_NAME, "a")
        .text
    )
    calendar_items = browser.find_elements(By.CSS_SELECTOR, "div.cal-item")
    if not calendar_items:
        logging.info("No calendar items found")
        return team_results_dict, school_name
    for item in calendar_items:
        try:
            meet_link = item.find_element(By.CSS_SELECTOR, "a.fa-list-ol")
        except Exception:
            logging.info(f"No meet link found for calendar item: {item.text}")
            continue
        if meet_link:
            if meet_id and not re.search(meet_id, meet_link.get_attribute("href")):
                logging.info("Skipping meet due to meet ID filter")
                continue
            date = item.find_element(By.CSS_SELECTOR, "small.date").text
            meet_name = item.find_element(By.CSS_SELECTOR, "span.title").text
            meet_url = meet_link.get_attribute("href")
            logging.info(
                f"Date: {date}\nMeet Name: {meet_name}\nMeet Link: {meet_url}\n"
            )
            team_results_dict[meet_name] = get_meet_results_for_school(
                driver=results_browser,
                url=f"{meet_url}/results/all",
                school_name=school_name,
                meet_date=date,
                location_override=location_override,
                number_of_teams_override=number_of_teams_override,
            )
    # Close the browser session
    browser.quit()
    return team_results_dict, school_name
