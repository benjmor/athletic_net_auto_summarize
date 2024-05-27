import logging
import selenium
from typing import List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


def parse_individual_result(
    individual_result,
    total_participants: int,
    # Gender of the event
    gender: str,
    # Name of the race
    race_name: str,
    is_relay: bool,
):
    """
    This function will process a Selenium webdriver individual result for an event and return a dict summarizing the performance
    """
    parsed_individual_result = individual_result.find_elements(By.TAG_NAME, "td")
    # Skip DNS, DNF, and DQs -- stored in the 4th piece for regular events, 11th for relays
    try:
        if (
            parsed_individual_result[4].text == "DNS"
            or parsed_individual_result[4].text == "DNF"
            or parsed_individual_result[4].text == "DQ"
        ):
            return None
        if is_relay and (
            parsed_individual_result[11].text == "DNS"
            or parsed_individual_result[11].text == "DNF"
            or parsed_individual_result[11].text == "DQ"
        ):
            return None
    except Exception:
        logging.error("Error checking for DNS, DNF, or DQ results")
        return None
    placement_string = (
        f"{parsed_individual_result[0].text.replace('.', '')}/{total_participants}"
    )
    try:
        percentile = 100 - int(
            100
            * int(parsed_individual_result[0].text.replace(".", ""))
            / total_participants
        )
    except ValueError:
        percentile = 0

    if is_relay:
        relay_names = []
        for relay_table_element in parsed_individual_result.find_elements(
            By.TAG_NAME, "tr"
        ):
            relay_names.append(
                relay_table_element.find_element(By.TAG_NAME, "a").text,
            )
        entry_name = "Relay Team: " + relay_names.join(", ")
        grade = "N/A"
        # Relays append a letter designation for A/B teams, needs to be removed.
        school_name = parsed_individual_result[5].text.split(" - ")[0]
    else:
        entry_name = parsed_individual_result[2].text
        grade = parsed_individual_result[1].text
        school_name = parsed_individual_result[5].text

    return {
        "placement": placement_string,
        "percentile": percentile,
        "grade": grade,
        "name": entry_name,
        "mark": parsed_individual_result[4].text.replace("SR", "").replace("PR", ""),
        "school": school_name,
        "gender": gender,
        "race_name": race_name,
        "is_personal_best": str(bool(parsed_individual_result[4].text[-2:] == "PR")),
        "is_season_best": str(
            bool(parsed_individual_result[4].text[-2:] == "PR")
            or bool(parsed_individual_result[4].text[-2:] == "SR")
        ),
    }


def create_tf_results_dict(
    event_elements: List[WebElement],
):
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
        event_results = element.find_elements(
            By.CSS_SELECTOR,
            "tbody[shared-result-relay-summary], tbody[shared-individual-result-summary]",
        )
        for index, event in enumerate(event_names):
            race_name = event.text
            tf_results_dict[f"{gender}|{race_name}"] = {}
            tf_results_dict[f"{gender}|{race_name}"]["individual_results"] = []
            logging.info(f"Parsing results for {gender} {race_name}")
            # Individual Scoring Logic
            individual_results = event_results[index]
            # Relay events have a table within a table.
            # TODO - This needs to be thought through more thoroughly
            is_relay = bool(
                individual_results.find_element(
                    By.TAG_NAME,
                    "tr",
                ).find_elements(
                    By.TAG_NAME,
                    "tr",
                )
            )
            if is_relay:
                # Select rows from the outer table, not the inner table
                individual_results_list = individual_results.find_elements(
                    By.CSS_SELECTOR,
                    'tr[container="body"]',
                )
            else:
                individual_results_list = individual_results.find_elements(
                    By.TAG_NAME, "tr"
                )
            total_participants = len(individual_results_list)
            # Relay event results display a table with the results

            for individual_result in individual_results_list:
                try:
                    tf_results_dict[f"{gender}|{race_name}"][
                        "individual_results"
                    ].append(
                        parse_individual_result(
                            individual_result=individual_result,
                            total_participants=total_participants,
                            gender=gender,
                            race_name=race_name,
                            is_relay=is_relay,
                        )
                    )
                except Exception:
                    # For now, just skip over unprocessable content
                    continue
        # Iterate after completing each gender
        gender_index = gender_index + 1

    return tf_results_dict
