import logging


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
