import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .get_meet_results import get_meet_results


def get_meet_results_wrapper(
    sport_name,
    meet_id,
    location_override=None,
    number_of_teams_override=None,
):
    event_results_dict = {}
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # chrome_options.binary_location = CHROME_PATH

    # Start a new browser session
    browser = webdriver.Chrome(options=chrome_options)
    results_browser = webdriver.Chrome(options=chrome_options)

    # Get name for URL
    if sport_name == "cross-country":
        sport_name_proper_nospace = "CrossCountry"
    else:
        sport_name_proper_nospace = "TrackAndField"

    event_results_dict = get_meet_results(
        driver=results_browser,
        url=f"https://www.athletic.net/{sport_name_proper_nospace}/meet/{meet_id}/results/all",
        location_override=location_override,
    )
    # Close the browser session
    browser.quit()
    return event_results_dict
