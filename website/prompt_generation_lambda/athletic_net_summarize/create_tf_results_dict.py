import logging
import selenium
from typing import List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


def create_tf_results_dict(
    event_elements: List[WebElement],
):
    # TODO - This is getting a lot of parsing wrong. Find out why.
    # It is probably related to the enumerate() usage
    """
    This takes a webdriver pointed to races and returns a dict with the following structure (note that team results are handled separately from event results in track):
    {
        "gender|event_name": {
            "individual_results": [
                {
                    "placement": str,
                    "percentile": int,
                    "grade": str,
                    "name": str,
                    "mark": str,
                    "school": str,
                    "gender": str,
                    "race_name": str,
                    "is_personal_best": str,
                    "is_season_best": str,
                },
                ...
            ]
        },
        ...
    }
    """

    tf_results_dict = {}
    gender_list = [
        "Mens",
        "Womens",
    ]  # Athletic.net puts mens on the left, womens on the right. This may break at some point.
    gender_index = 0
    # Event Elements should contain 2 lists of elements, one for each gender
    for element in event_elements:
        # You can now interact with or retrieve information from the selected element
        gender = gender_list[gender_index]
        event_names = element.find_elements(By.TAG_NAME, "h4")
        event_results = element.find_elements(By.TAG_NAME, "tbody")
        for index, event in enumerate(event_names):
            race_name = event.text
            tf_results_dict[f"{gender}|{race_name}"] = {}
            tf_results_dict[f"{gender}|{race_name}"]["individual_results"] = []
            logging.info(f"Parsing results for {gender} {race_name}")
            # Individual Scoring Logic
            individual_results = event_results[index]
            individual_results_list = individual_results.find_elements(
                By.TAG_NAME, "tr"
            )
            total_participants = len(individual_results_list)
            for individual_result in individual_results_list:
                parsed_individual_result = individual_result.find_elements(
                    By.TAG_NAME, "td"
                )
                # Skip DNS and DNF
                try:
                    if (
                        parsed_individual_result[4].text == "DNS"
                        or parsed_individual_result[4].text == "DNF"
                    ):
                        continue
                except IndexError:
                    continue
                placement_string = f"{parsed_individual_result[0].text.replace('.', '')}/{total_participants}"
                try:
                    percentile = 100 - int(
                        100
                        * int(parsed_individual_result[0].text.replace(".", ""))
                        / total_participants
                    )
                except ValueError:
                    percentile = 0
                try:
                    tf_results_dict[f"{gender}|{race_name}"][
                        "individual_results"
                    ].append(
                        {
                            "placement": placement_string,
                            "percentile": percentile,
                            "grade": parsed_individual_result[1].text,
                            "name": parsed_individual_result[2].text,
                            "mark": parsed_individual_result[4].text,
                            "school": parsed_individual_result[5].text,
                            "gender": gender,
                            "race_name": race_name,
                            "is_personal_best": str(
                                bool(parsed_individual_result[4].text[-2:] == "PR")
                            ),
                            "is_season_best": str(
                                bool(parsed_individual_result[4].text[-2:] == "PR")
                                or bool(parsed_individual_result[4].text[-2:] == "SR")
                            ),
                        }
                    )
                except:
                    logging.info(f"Failed to parse {parsed_individual_result}")
        # Iterate after completing each gender
        gender_index = gender_index + 1

    return tf_results_dict
