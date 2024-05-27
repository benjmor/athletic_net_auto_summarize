from selenium.webdriver.common.by import By


def get_meet_name(driver):
    """
    This function returns the name of the meet, as listed on the website.
    """
    header = driver.find_element(By.CLASS_NAME, "p-1")  # p-md-2")
    name = header.find_element(By.TAG_NAME, "h2")
    return name.text
