import logging


def group_results_by_team(
    results: dict,
    event_type: str,
):
    """
    This function will take a dict of results and group them by team.

    Args:
        results (dict): A dict of event results, where each event contains an individual results key and optionally contains a team results key.
        The individual results key should be a list of dicts, where each dict represents a single result.
        Each individual results dict should have the following keys:
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
        }

    Returns:
        dict: A dictionary where the keys are the teams and the values are lists of results for that team.
        Example:
            {
                'team1': [
                    {
                        "placement": str,
                        "percentile": int,
                        "grade": str,
                        "name": str,
                        "mark": str,
                        "gender": str,
                        "race_name": str,
                        "is_personal_best": str,
                        "is_season_best": str,
                    },
                    ...
                ]
                'team2': [
                    {...}
                ]
            }
    """
    team_grouped_results = {}
    for result in results:
        if "individual_results" in results[result]:
            for individual_result in results[result]["individual_results"]:
                if individual_result is None:
                    continue
                team = individual_result.pop("school")
                if team not in team_grouped_results:
                    team_grouped_results[team] = {}
                if "individual_results" not in team_grouped_results[team]:
                    team_grouped_results[team]["individual_results"] = []
                if "team_results" not in team_grouped_results[team]:
                    team_grouped_results[team]["team_results"] = []
                team_grouped_results[team]["individual_results"].append(
                    individual_result
                )
        # Cross-country specific team results logic
        if event_type == "cross-country" and "team_results" in results[result]:
            logging.info("Processing cross-country team results...")
            previous_team_result = None
            for team_result_iterator, team_result in enumerate(
                results[result]["team_results"]
            ):
                team = team_result.get("school_name")

                # If not first, include better rival team
                try:
                    team_result["better_rival_result"] = results[result][
                        "team_results"
                    ][team_result_iterator - 1]
                except IndexError:
                    pass  # Top-ranked teams will have none before them

                # If not last, include worse rival team
                try:
                    team_result["worse_rival_result"] = results[result]["team_results"][
                        team_result_iterator + 1
                    ]
                except IndexError:
                    pass  # Bottom-ranked teams will have none after them

                team_grouped_results[team]["team_results"].append(team_result)

    # Sort each team's results by the percentile of the result
    for team in team_grouped_results:
        team_grouped_results[team]["individual_results"].sort(
            key=lambda x: x["percentile"],
            reverse=True,
        )
        if team_grouped_results[team].get("team_results"):
            team_grouped_results[team]["team_results"].sort(
                key=lambda x: x["percentile"],
                reverse=True,
            )
    return team_grouped_results
