# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
# You will also need to set an OpenAI API Key environment variable, like 'export OPENAI_API_KEY=12345123451235' or '$env:OPENAI_API_KEY=123451234512345' on PowerShell
import datetime
import logging
from .get_parser import get_parser
from .get_meet_results_wrapper import get_meet_results_wrapper
from .generate_llm_article import generate_llm_article

logging.basicConfig(level=logging.INFO)


def main(
    school_id,
    data_bucket,
    meet_id,
    sport_name,
    percentile_minimum,
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
    results = get_meet_results_wrapper(
        sport_name=sport_name,
        meet_id=meet_id,
    )
    for result in results.keys():
        meet_location = results[result]["meet_location"]
        meet_date = results[result]["meet_date"]
        generate_llm_article(
            results=results[result],
            sport_name_proper=sport_name_proper,
            meet_name=result,
            meet_location=meet_location,
            meet_date=meet_date,
            meet_id=meet_id,
        )


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
