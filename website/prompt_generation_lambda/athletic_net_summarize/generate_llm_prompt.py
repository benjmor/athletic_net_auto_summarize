import logging


def generate_llm_prompt(
    sport_name_proper,
    meet_date,
    meet_name,
    meet_location,
    meet_id,
    school_name,
    percentile_minimum=50,
    custom_url=None,
    quote_dict=None,
):
    logging.info(f"Generating LLM prompt for {meet_name}")
    if custom_url:
        follow_up_url = custom_url
    elif meet_id:
        sport_name_proper_no_spaces = sport_name_proper.replace(" ", "")
        follow_up_url = f"https://www.athletic.net/{sport_name_proper_no_spaces}/meet/{meet_id}/results/all"
    else:
        follow_up_url = "https://www.athletic.net"
    meet_location = meet_location.replace(" US", "")
    llm_basic_prompt = f"""
The following data represents results of a high school {sport_name_proper.lower()} meet called {meet_name} held at {meet_location}, on {meet_date}.

Write a 3 paragraph summary for the {school_name} High School newspaper summarizing the meet. Use as many student names of {school_name} students as reasonable. When referencing a student for the first time, say what grade they are in.

Always include individuals' marks (times/distances) and ranks when referencing a result. However, don't include raw percentile information in the output, just times and ranks.

Call out personal bests and season bests if a student achieves them.

When referencing results, you should use the placement field to include the total number of athletes in each event (eg. placement 1/30 means 1st of 30 competitors), but only once per event.

At the end, indicate that additional information including full results can be found at {follow_up_url}.
    """
    cross_country_addendum = f"""
The data includes team and individual results. In team results, more points represents a worse finish. The top 5 runners in each race score points for the team. 5 runners are required to field a scoring team.

The team data includes information about schools that did one rank better or worse than {school_name}, listed as better_rival and worse_rival. You can reference these schools to illustrate how {school_name} did in the meet.
    """
    track_addendum = f"""
All field (eg. shot put, discus, jumps, and pole vault) marks are measured in feet.
   """
    if sport_name_proper == "Cross Country":
        llm_payload = [llm_basic_prompt, cross_country_addendum]
    elif sport_name_proper == "Track & Field":
        llm_payload = [llm_basic_prompt, track_addendum]
    else:
        llm_payload = [llm_basic_prompt]

    return llm_payload
