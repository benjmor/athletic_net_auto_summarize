# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
# You will also need to set an OpenAI API Key environment variable, like 'export OPENAI_API_KEY=12345123451235' or '$env:OPENAI_API_KEY=123451234512345' on PowerShell
import datetime
import logging
from .get_parser import get_parser
from .get_meet_results_wrapper import get_meet_results_wrapper
from .generate_llm_article import generate_llm_article
from .group_results_by_team import group_results_by_team
from .generate_numbered_list_prompt import generate_numbered_list_prompt

logging.basicConfig(level=logging.INFO)


def main(
    school_id,
    data_bucket,
    meet_id,
    sport_name,
    percentile_minimum,
    school_name=None,
):
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
    event_results = get_meet_results_wrapper(
        sport_name=sport_name,
        meet_id=meet_id,
    )
    meet_name = event_results.get("meet_name")
    meet_location = event_results.get("meet_location")
    meet_date = event_results.get("meet_date")
    team_grouped_results = group_results_by_team(
        results=event_results,
        event_type=sport_name,
    )
    llm_prompts_by_school = {}
    for school in team_grouped_results.keys():
        llm_prompts_by_school[school] = {}
        llm_prompts_by_school[school]["llm_prompt"] = generate_llm_article(
            results=team_grouped_results[school],
            sport_name_proper=sport_name_proper,
            school_name=school,
            meet_name=meet_name,
            meet_location=meet_location,
            meet_date=meet_date,
            meet_id=meet_id,
        )
        # TODO - Get this added
        # llm_prompts_by_school[school]["numbered_list_prompt"] = generate_numbered_list_prompt(
        #     results=team_grouped_results[school],
        #     sport_name_proper=sport_name_proper,
        #     school_name=school,
        #     meet_name=meet_name,
        #     meet_location=meet_location,
        #     meet_date=meet_date,
        #     meet_id=meet_id,
        # )
    return llm_prompts_by_school


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    school_id = args.school_id
    meet_id = args.meet_id
    sport_name = args.sport_name
    main(
        school_id,
        meet_id,
        sport_name,
    )
