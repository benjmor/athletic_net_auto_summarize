# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
# You will also need to set an OpenAI API Key environment variable, like 'export OPENAI_API_KEY=12345123451235' or '$env:OPENAI_API_KEY=123451234512345' on PowerShell
import datetime
import logging
from get_parser import get_parser
from get_school_results_for_year_and_sport import get_school_results_for_year_and_sport
from generate_chat_gpt_article import generate_chat_gpt_article

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    parser = get_parser()
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
    location_override = args.location_override
    number_of_teams_override = args.number_of_teams_override
    results, school_name = get_school_results_for_year_and_sport(
        school_id=school_id,
        year=year,
        sport_name=sport_name,
        meet_id=meet_id,
        location_override=location_override,
        number_of_teams_override=number_of_teams_override,
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
