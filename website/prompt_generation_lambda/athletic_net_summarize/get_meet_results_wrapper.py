import logging
import os
import re
from tempfile import mkdtemp
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
    # If we're not in Lambda, assume we're in Windows
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None:
        chrome_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        driver_location = None  # Use default
        service = webdriver.ChromeService()
        chrome_options.binary_location = chrome_location
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # If we are in Lambda, assume we're in Linux
    else:
        chrome_location = "/opt/chrome/chrome"
        driver_location = "/opt/chromedriver"
        service = webdriver.ChromeService(driver_location)
        chrome_options.binary_location = chrome_location
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280x1696")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.add_argument(f"--data-path={mkdtemp()}")
        chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--remote-debugging-port=9222")

    # Start a new browser session
    results_browser = webdriver.Chrome(
        options=chrome_options,
        service=service,
    )

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
    results_browser.quit()
    return event_results_dict
