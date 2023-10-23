# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
# You will also need to set an OpenAI API Key environment variable, like 'export OPENAI_API_KEY=12345123451235' or '$env:OPENAI_API_KEY=123451234512345' on PowerShell
import openai
import argparse
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs
import logging
import selenium
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

logging.basicConfig(level=logging.INFO)


def get_number_of_competing_teams(driver, url):
    return 50


def get_meet_location(driver, url):
    return "Sacramento"


def get_meet_results_for_school(driver, url, school_name, meet_date):
    meet_results_for_school = {}
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//table[@class='ng-star-inserted']")
        )
    )

    number_of_teams = get_number_of_competing_teams(driver, url)
    meet_location = get_meet_location(driver, url)
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
                    meet_results_for_school[f"{gender}|{race_name}"]["team_result"]["school_name"] = school_name
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


def get_school_results_for_year_and_sport(school_id, year, sport_name, meet_id=None):
    team_results_dict = {}
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # chrome_options.binary_location = CHROME_PATH

    # Start a new browser session
    browser = webdriver.Chrome(options=chrome_options)
    results_browser = webdriver.Chrome(options=chrome_options)

    # Navigate to the page with the list of meets
    base_url = f"https://www.athletic.net/team/{school_id}/{sport_name}/{year}"
    browser.get(base_url)

    school_name = (
        browser.find_element(By.CLASS_NAME, "container.ng-star-inserted")
        .find_element(By.TAG_NAME, "a")
        .text
    )
    calendar_items = browser.find_elements(By.CSS_SELECTOR, "div.cal-item")
    for item in calendar_items:
        try:
            meet_link = item.find_element(By.CSS_SELECTOR, "a.fa-list-ol")
        except Exception:
            logging.info(f"No meet link found for calendar item: {item.text}")
            continue
        if meet_link:
            if meet_id and not re.search(meet_id, meet_link.get_attribute("href")):
                logging.info("Skipping meet due to meet ID filter")
                continue
            date = item.find_element(By.CSS_SELECTOR, "small.date").text
            meet_name = item.find_element(By.CSS_SELECTOR, "span.title").text
            meet_url = meet_link.get_attribute("href")
            logging.info(
                f"Date: {date}\nMeet Name: {meet_name}\nMeet Link: {meet_url}\n"
            )
            team_results_dict[meet_name] = get_meet_results_for_school(
                driver=results_browser,
                url=f"{meet_url}/results/all",
                school_name=school_name,
                meet_date=date,
            )
    # Close the browser session
    browser.quit()
    return team_results_dict, school_name


def generate_chat_gpt_prompt(
    sport_name_proper,
    school_name,
    meet_date,
    meet_name,
    meet_location,
    meet_id,
    custom_url=None,
    quote_dict=None,
):
    logging.info(f"Generating ChatGPT prompt for {meet_name}")
    if custom_url:
        follow_up_url = custom_url
    elif meet_id:
        sport_name_proper_no_spaces = sport_name_proper.replace(" ", "")
        follow_up_url = f"https://www.athletic.net/{sport_name_proper_no_spaces}/meet/{meet_id}/results/all"
    else:
        follow_up_url = "https://www.athletic.net"
    chat_gpt_basic_prompt = f"""
The following data represents results of a high school {sport_name_proper} meet called {meet_name} held at {meet_location}, on {meet_date}.

Write a 3 paragraph summary for the {school_name} High School newspaper summarizing the meet. Use as many student names of {school_name} students as reasonable.

Include individuals' times and ranks if they are in the 80th percentile or higher. However, don't include raw percentile information in the output, just times and ranks.

When referencing results, you should include the total number of athletes in each event, but only once per event.

At the end, indicate that additional information including full results can be found at {follow_up_url}.
    """
    cross_country_addendum = f"""
The data includes team and individual results. In team results, more points represents a worse finish. The top 5 runners in each race score points for the team. 5 runners are required to field a scoring team.

The team data includes information about schools that did one rank better or worse than {school_name}, listed as better_rival and worse_rival. You can reference these schools to illustrate how {school_name} did in the meet.
    """
    if sport_name == "cross-country":
        chat_gpt_payload = [chat_gpt_basic_prompt, cross_country_addendum]

    return chat_gpt_payload


def flatten_results(results):
    """
    Takes in a dict of results and flattens it to a list of strings
    """
    logging.info("Flattening results data...")
    output = []
    TEAM_RESULT_HEADER = "race_name|rank_among_scoring_teams|points"
    INDIVIDUAL_RESULT_HEADER = "race_name|placement|percentile|grade|name|time|school"
    for result in results.keys():
        if not isinstance(results[result], dict):
            continue
        if "team_result" in results[result]:
            output.append(TEAM_RESULT_HEADER)
            team_data = f"{result}|{results[result]['team_result']['rank_of_scoring_teams']}|{results[result]['team_result']['school_name']}|{results[result]['team_result']['points']}"
            output.append(team_data)
            for rival_result in ["worse_rival_result", "better_rival_result"]:
                if rival_result in results[result]:
                    rival_data = f"{result}|{results[result][rival_result]['rank']}|{results[result][rival_result]['school_name']}|{results[result][rival_result]['points']}|{rival_result.replace('_result', '')}"
                    output.append(rival_data)
        if (
            "individual_results" in results[result]
            and results[result]["individual_results"]
        ):
            output.append(INDIVIDUAL_RESULT_HEADER)
            for individual_result in results[result]["individual_results"]:
                individual_data = f"{result}|{individual_result['placement']}|{individual_result['percentile']}|{individual_result['grade']}|{individual_result['name']}|{individual_result['time']}|{individual_result['school']}"
                output.append(individual_data)
    return output


def generate_chat_gpt_article(
    results,
    school_name,
    sport_name_proper,
    meet_name,
    meet_location,
    meet_date,
    meet_id,
    custom_url=None,
    quote_dict=None,
):
    chat_gpt_payload = generate_chat_gpt_prompt(
        sport_name_proper=sport_name_proper,
        school_name=school_name,
        custom_url=custom_url,
        quote_dict=quote_dict,
        meet_name=meet_name,
        meet_location=meet_location,
        meet_date=meet_date,
        meet_id=meet_id,
    ) + flatten_results(results)
    final_gpt_payload = "\r\n".join(chat_gpt_payload)
    logging.info(f"Submitting this payload to ChatGPT:\n {final_gpt_payload}")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    openai.api_key_path = os.path.join(script_dir, "openAiAuthKey.txt")
    body_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": final_gpt_payload},
        ],
    )["choices"][0]["message"]["content"]
    headline_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "Generate a headline for the article. The response should be just a single headline",
            },
            {"role": "user", "content": final_gpt_payload},
        ],
    )["choices"][0]["message"]["content"]
    summary_folder = f"{meet_name}_summaries"
    os.makedirs(summary_folder, exist_ok=True)
    with open(
        os.path.join(script_dir, summary_folder, f"{school_name}_summary.txt"), "w"
    ) as f:
        logging.info(f"Writing output to {school_name}_summary.txt...")
        f.write(headline_response + "\r\n" + body_response)
    # generate_website.main(input_directory=f"{data['name']}_summaries")


if __name__ == "__main__":
    # Create an argument parser to take a tournament ID
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--school-id",
        help="School ID (number) of the school you want to generate an article for.",
        # required=True,
    )
    parser.add_argument(
        "-y",
        "--year",
        help="Year for the season you want to generate an article for.",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--sport-name",
        help="Sport name (string) of the sport you want to generate an article for.",
        default="cross-country",
    )
    parser.add_argument(
        "-m",
        "--meet-id",
        help="Meet ID (string) of the meet you want to generate an article for.",
    )
    args = parser.parse_args()
    school_id = args.school_id
    meet_id = args.meet_id
    sport_name = args.sport_name
    if sport_name not in [
        "cross-country",
        "track-and-field-indoor",
        "track-and-field-outdoor",
    ]:
        raise ValueError(f"Invalid sport name {sport_name}")
    # Get name as used in URLs
    if sport_name == "cross-country":
        sport_name_proper = "Cross Country"
    else:
        sport_name_proper = "Track And Field"
    year = args.year
    if year is None:
        year = datetime.datetime.now().year
    results, school_name = get_school_results_for_year_and_sport(
        school_id=school_id, year=year, sport_name=sport_name, meet_id=meet_id
    )
    for result in results.keys():
        meet_location = results[result]["meet_location"]
        meet_date = results[result]["meet_date"]
        generate_chat_gpt_article(
            results=results[result],
            sport_name_proper=sport_name_proper,
            school_name=school_name,
            meet_name=result,
            meet_location=meet_location,
            meet_date=meet_date,
            meet_id=meet_id,
        )
