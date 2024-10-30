from selenium.webdriver.common.by import By


def get_meet_location(driver):
    """
    This function returns the location of the meet, as listed on the website.
    """
    header = driver.find_element(By.CLASS_NAME, "p-1")  # p-md-2")
    venue = header.find_element(By.TAG_NAME, "meet-venue-link")
    return venue.text
