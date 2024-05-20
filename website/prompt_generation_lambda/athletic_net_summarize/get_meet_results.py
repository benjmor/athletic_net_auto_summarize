import selenium.webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium
import logging
import re

from .get_meet_location import get_meet_location
from .get_meet_date import get_meet_date
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
    This function takes in a Selenium WebDriver instance and a URL and returns a dictionary of meet results for all schools attending the meet.
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
        meet_location = location_override
    else:
        meet_location = get_meet_location(driver, url)
    return_dict["meet_location"] = meet_location
    return_dict["meet_date"] = get_meet_date(driver)

    if re.search(r"CrossCountry", url):
        # Find the element with class="mt-2 ng-star-inserted" using find_element_by_css_selector
        elements = driver.find_elements(
            By.CSS_SELECTOR, "*.col-sm-6.mb-3.mb-sm-0.ng-star-inserted"
        )
        return create_xc_results_dict(elements)
    elif re.search(r"Track", url):
        # Find the element with class="mt-2 ng-star-inserted" using find_element_by_css_selector
        elements = driver.find_elements(
            By.CSS_SELECTOR, "*.col-lg-6.mb-3.mb-sm-0.ng-star-inserted"
        )
        return create_tf_results_dict(elements)