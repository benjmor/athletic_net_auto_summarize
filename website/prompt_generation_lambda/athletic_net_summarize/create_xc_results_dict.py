import logging
import selenium
from selenium.webdriver.common.by import By
from typing import List
from selenium.webdriver.remote.webelement import WebElement


def create_xc_results_dict(
    event_elements: List[WebElement],
):
    """
    This takes a webdriver pointed to races and returns a dict with the following structure:
    {
        "gender|race_name": {
            "individual_results": [
                {
                    "placement": str,
                    "percentile": int,
                    "grade": str,
                    "name": str,
                    "mark": str,
                    "school_name": str,
                    "gender": str,
                    "race_name": str,
                },
                ...
            ],
            "team_results": [
                {
                    "school_name": str,
                    "rank_of_scoring_teams": str, # This is the team rank relative to the rest of the teams in the race (only counting teams with 5+ runners), including a denominator with total teams
                    "points": "points",
                },
                ...
            ]
        },
        ...
    }
    """
    xc_results_dict = {}
    gender_list = [
        "Mens",
        "Womens",
    ]  # Athletic.net puts mens on the left, womens on the right. This may break at some point.
    gender_index = 0
    for element in event_elements:
        # You can now interact with or retrieve information from the selected element
        gender = gender_list[gender_index]
        races = element.find_elements(By.CSS_SELECTOR, "*.mt-2.ng-star-inserted")
        for race in races:
            race_name = race.find_element(By.TAG_NAME, "h5").text
            xc_results_dict[f"{gender}|{race_name}"] = {}
            xc_results_dict[f"{gender}|{race_name}"]["individual_results"] = []
            xc_results_dict[f"{gender}|{race_name}"]["team_results"] = []
            team_scores = race.find_element(By.TAG_NAME, "table")
            logging.info(f"Parsing results for {gender} {race_name}")
            # Team Scoring Logic
            team_score_list = team_scores.find_elements(By.TAG_NAME, "tr")
            total_scoring_teams = len(team_score_list)
            for team_score in team_score_list:
                parsed_team_score = team_score.find_elements(By.TAG_NAME, "td")
                school_name = parsed_team_score[1].text
                team_rank = parsed_team_score[0].text.replace(".", "")
                logging.debug(
                    f"{school_name} ranked {team_rank} in the {gender} {race_name} race. {school_name} scored {parsed_team_score[2].text} points."
                )
                xc_results_dict[f"{gender}|{race_name}"]["team_results"].append(
                    {
                        "rank_of_scoring_teams": f"{team_rank}/{total_scoring_teams}",
                        "points": parsed_team_score[2].text,
                        "school_name": school_name,
                        "percentile": 100
                        - int(100 * int(team_rank) / total_scoring_teams),
                        "event_name": f"{gender}|{race_name}",
                    }
                )

            # Individual Scoring Logic
            individual_results = race.find_element(
                By.CSS_SELECTOR, "*.table-responsive"
            )
            individual_results_list = individual_results.find_elements(
                By.TAG_NAME, "tr"
            )
            total_runners = len(individual_results_list)
            for individual_result in individual_results_list:
                parsed_individual_result = individual_result.find_elements(
                    By.TAG_NAME, "td"
                )
                placement_string = f"{parsed_individual_result[0].text.replace('.', '')}/{total_runners}"
                try:
                    individual_placement = int(
                        parsed_individual_result[0].text.replace(".", "")
                    )
                except ValueError:
                    individual_placement = 0
                percentile = 100 - int(100 * individual_placement / total_runners)
                xc_results_dict[f"{gender}|{race_name}"]["individual_results"].append(
                    {
                        "placement": placement_string,
                        "percentile": percentile,
                        "grade": parsed_individual_result[1].text,
                        "name": parsed_individual_result[2].text,
                        "mark": parsed_individual_result[4].text,
                        "school": parsed_individual_result[6].text,
                        "gender": gender,
                        "race_name": race_name,
                        "is_personal_best": "unknown",  # bool(check_pb())
                        "is_season_best": "unknown",  # bool(check_sb())
                    }
                )
        # Iterate after completing each gender
        gender_index = gender_index + 1

    return xc_results_dict
