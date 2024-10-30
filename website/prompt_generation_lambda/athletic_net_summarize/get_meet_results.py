import selenium.webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium
import logging
import re

from .get_meet_location import get_meet_location
from .get_meet_date import get_meet_date
from .get_meet_name import get_meet_name
from .create_xc_results_dict import create_xc_results_dict
from .create_tf_results_dict import create_tf_results_dict


def get_meet_results(
    # Selenium Webdriver object
    driver: selenium.webdriver.Chrome,
    # URL containing the full meet results
    url: str,
    # Location override, if you want a more generic name (eg. Manhattan -> New York)
    location_override: str = None,
):
    """
    This function takes in a Selenium WebDriver instance and a URL and returns a dictionary of meet results.

    The meet results dictionary contains the following keys:
    - meet_location: The location of the meet
    - meet_date: The date of the meet
    - results: A dictionary containing the results of the meet
        - Each key in the results dictionary is an event name
            - Entries within the event's values will be individual performances
    """
    return_dict = {}
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//table[@class='ng-star-inserted']")
            )
        )
    except selenium.common.exceptions.TimeoutException:
        logging.info(
            f"Timed out waiting for team results table to load for {url}. This may simply indicate that there are no team results."
        )

    if location_override:
        return_dict["meet_location"] = location_override
    else:
        return_dict["meet_location"] = get_meet_location(driver)
    return_dict["meet_date"] = get_meet_date(driver)
    return_dict["meet_name"] = get_meet_name(driver)

    if re.search(r"CrossCountry", url):
        # Find the element with class="mt-2 ng-star-inserted" using find_element_by_css_selector
        elements = driver.find_elements(
            By.CSS_SELECTOR, "*.col-sm-6.mb-3.mb-sm-0.ng-star-inserted"
        )
        return_dict.update(create_xc_results_dict(elements))
        return return_dict
    elif re.search(r"Track", url):
        # Find the element with class="mt-2 ng-star-inserted" using find_element_by_css_selector
        elements = driver.find_elements(
            By.CSS_SELECTOR, "*.col-lg-6.mb-3.mb-sm-0.ng-star-inserted"
        )
        return_dict.update(create_tf_results_dict(elements))
        return return_dict
