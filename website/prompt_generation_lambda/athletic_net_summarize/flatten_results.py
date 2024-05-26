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
    for result in results:
        if not isinstance(result, dict):
            continue
        # TODO - This needs some work to meet the new model
        if "team_result" in results[result]:
            output.append("|".join(TEAM_RESULT_HEADER_KEYS))
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
            output.append("|".join(INDIVIDUAL_RESULT_HEADER_KEYS))
            individual_data_string = ""
            for header_key in INDIVIDUAL_RESULT_HEADER_KEYS:
                if header_key not in result:
                    individual_data_string = "|".join(individual_data_string, "")
                individual_data_string = "|".join(
                    individual_data_string, {result[header_key]}
                )
            output.append(individual_data_string)
    return output
