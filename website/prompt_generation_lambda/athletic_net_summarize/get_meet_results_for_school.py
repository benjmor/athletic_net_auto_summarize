from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium
import logging

from get_meet_location import get_meet_location
from get_number_of_competing_teams import get_number_of_competing_teams


def get_meet_results_for_school(
    driver, url, school_name, meet_date, location_override, number_of_teams_override
):
    meet_results_for_school = {}
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
    if number_of_teams_override:
        number_of_teams = number_of_teams_override
    else:
        number_of_teams = get_number_of_competing_teams(driver, url)
    meet_results_for_school["number_of_total_teams"] = number_of_teams
    meet_results_for_school["meet_location"] = meet_location
    meet_results_for_school["meet_date"] = meet_date

    # Find the element with class="mt-2 ng-star-inserted" using find_element_by_css_selector
    elements = driver.find_elements(
        By.CSS_SELECTOR, "*.col-sm-6.mb-3.mb-sm-0.ng-star-inserted"
    )

    gender_list = [
        "Mens",
        "Womens",
    ]  # Athletic.net puts mens on the left, womens on the right
    gender_index = 0
    for element in elements:
        # You can now interact with or retrieve information from the selected element
        gender = gender_list[gender_index]
        races = element.find_elements(By.CSS_SELECTOR, "*.mt-2.ng-star-inserted")
        for race in races:
            race_name = race.find_element(By.TAG_NAME, "h5").text
            meet_results_for_school[f"{gender}|{race_name}"] = {}
            meet_results_for_school[f"{gender}|{race_name}"]["individual_results"] = []
            team_scores = race.find_element(By.TAG_NAME, "table")
            logging.info(f"Parsing results for {gender} {race_name}")
            individual_results = race.find_element(
                By.CSS_SELECTOR, "*.table-responsive"
            )
            team_score_list = team_scores.find_elements(By.TAG_NAME, "tr")
            total_scoring_teams = len(team_score_list)
            team_score_index = 0
            for team_score in team_score_list:
                parsed_team_score = team_score.find_elements(By.TAG_NAME, "td")
                if parsed_team_score[1].text == school_name:
                    team_rank = parsed_team_score[0].text.replace(".", "")
                    logging.info(
                        f"{school_name} ranked {team_rank} in the {gender} {race_name} race. {school_name} scored {parsed_team_score[2].text} points."
                    )
                    meet_results_for_school[f"{gender}|{race_name}"]["team_result"] = {
                        "rank_of_scoring_teams": f"{team_rank}/{total_scoring_teams}",
                        "points": parsed_team_score[2].text,
                    }
                    meet_results_for_school[f"{gender}|{race_name}"]["team_result"][
                        "school_name"
                    ] = school_name
                    # Include 'rival' results -- the teams 1 ahead and 1 behind the target school
                    if team_score_index > 0:
                        parsed_better_team_score = team_score_list[
                            team_score_index - 1
                        ].find_elements(By.TAG_NAME, "td")
                        meet_results_for_school[f"{gender}|{race_name}"][
                            "better_rival_result"
                        ] = {
                            "rank": f"{parsed_better_team_score[0].text.replace('.', '')}/{total_scoring_teams}",
                            "school_name": parsed_better_team_score[1].text,
                            "points": parsed_better_team_score[2].text,
                        }
                    if team_score_index < len(team_score_list) - 1:
                        parsed_worse_team_score = team_score_list[
                            team_score_index + 1
                        ].find_elements(By.TAG_NAME, "td")
                        meet_results_for_school[f"{gender}|{race_name}"][
                            "worse_rival_result"
                        ] = {
                            "rank": f"{parsed_worse_team_score[0].text.replace('.', '')}/{total_scoring_teams}",
                            "school_name": parsed_worse_team_score[1].text,
                            "points": parsed_worse_team_score[2].text,
                        }
                    break
                team_score_index = team_score_index + 1
            individual_results_list = individual_results.find_elements(
                By.TAG_NAME, "tr"
            )
            total_runners = len(individual_results_list)
            for individual_result in individual_results_list:
                parsed_individual_result = individual_result.find_elements(
                    By.TAG_NAME, "td"
                )
                if parsed_individual_result[6].text == school_name:
                    placement_string = f"{parsed_individual_result[0].text.replace('.', '')}/{total_runners}"
                    percentile = 100 - int(
                        100
                        * int(parsed_individual_result[0].text.replace(".", ""))
                        / total_runners
                    )
                    meet_results_for_school[f"{gender}|{race_name}"][
                        "individual_results"
                    ].append(
                        {
                            "placement": placement_string,
                            "percentile": percentile,
                            "grade": parsed_individual_result[1].text,
                            "name": parsed_individual_result[2].text,
                            "time": parsed_individual_result[4].text,
                            "school": parsed_individual_result[6].text,
                            "gender": gender,
                            "race_name": race_name,
                            # "is_personal_best": bool(check_pb())
                            # "is_season_best": bool(check_sb())
                        }
                    )
        gender_index = gender_index + 1
    return meet_results_for_school
