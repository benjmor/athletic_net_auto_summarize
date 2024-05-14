import argparse


def get_parser():
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
    parser.add_argument(
        "-l",
        "--location-override",
        help="Location override (string) of the meet you want to generate an article for. If not provided, will attempt to pull from website or use a default value",
    )
    parser.add_argument(
        "-n",
        "--number-of-teams-override",
        help="Number of teams override (int) of the meet you want to generate an article for. If not provided, will attempt to pull from website or use a default value",
    )
    return parser
