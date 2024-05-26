def group_results_by_team(results):
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
        if "individual_results" not in results[result]:
            continue
        for individual_result in results[result]["individual_results"]:
            team = individual_result.pop("school")
            if team not in team_grouped_results:
                team_grouped_results[team] = []
            team_grouped_results[team].append(individual_result)
    return team_grouped_results
