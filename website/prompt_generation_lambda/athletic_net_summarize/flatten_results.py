import logging


def flatten_results(results):
    """
    Takes in a dict of results and flattens it to a list of strings matching the headers defined at the top of the function
    """
    logging.info("Flattening results data...")
    output = []
    TEAM_RESULT_HEADER_KEYS = [
        "race_name",
        "rank_among_scoring_teams",
        "points",
    ]
    INDIVIDUAL_RESULT_HEADER_KEYS = [
        "name",
        "gender",
        "race_name",
        "placement",
        "percentile",
        "grade",
        "mark",
        "is_personal_best",
        "is_season_best",
    ]
    if "team_results" in results:
        output.append("|".join(TEAM_RESULT_HEADER_KEYS))
    for team_result in results.get("team_results", []):
        # TODO - fix XC handling -- look at TF handling below
        team_data = f"{team_result['event_name']}|{team_result['team_result']['rank_of_scoring_teams']}|{team_result['team_result']['school_name']}|{team_result['team_result']['points']}"
        output.append(team_data)
        for rival_result in ["worse_rival_result", "better_rival_result"]:
            if rival_result in team_result:
                rival_data = f"{team_result['event_name']}|{team_result[rival_result]['rank']}|{team_result[rival_result]['school_name']}|{team_result[rival_result]['points']}|{rival_result.replace('_result', '')}"
                output.append(rival_data)
    if "individual_results" in results:
        output.append("|".join(INDIVIDUAL_RESULT_HEADER_KEYS))
    for individual_result in results.get("individual_results", []):
        individual_data_string = ""
        for header_key in INDIVIDUAL_RESULT_HEADER_KEYS:
            if individual_data_string == "":
                individual_data_string = individual_result.get(header_key, "")
                continue
            individual_data_string = "|".join(
                [individual_data_string, str(individual_result.get(header_key, ""))]
            )
        output.append(individual_data_string)
    return output
