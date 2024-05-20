def get_meet_date(driver):
    return "January 1, 1970"  # TODO
    try:
        driver.find_element_by_xpath("//div[@class='meet-date']")
        return True
    except:
        return False
