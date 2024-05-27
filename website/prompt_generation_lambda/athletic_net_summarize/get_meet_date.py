from selenium.webdriver.common.by import By


def get_meet_date(driver):
    """
    This function returns the date of the meet, as listed on the website.
    """
    header = driver.find_element(By.CLASS_NAME, "p-1")  # p-md-2")
    date = header.find_element(By.CLASS_NAME, "d-none")  # d-sm-inline-block")
    return date.text
