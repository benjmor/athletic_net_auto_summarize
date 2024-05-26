import logging
import os
from .generate_llm_prompt import generate_llm_prompt
from .flatten_results import flatten_results


def generate_llm_article(
    results,
    school_name,
    sport_name_proper,
    meet_name,
    meet_location,
    meet_date,
    meet_id,
    custom_url=None,
    quote_dict=None,
):
    llm_payload = generate_llm_prompt(
        sport_name_proper=sport_name_proper,
        school_name=school_name,
        custom_url=custom_url,
        quote_dict=quote_dict,
        meet_name=meet_name,
        meet_location=meet_location,
        meet_date=meet_date,
        meet_id=meet_id,
    ) + flatten_results(results)
    final_llm_payload = "\r\n".join(llm_payload)
    logging.info(f"Submitting this payload to the LLM:\n {final_llm_payload}")
    # TODO - Send to LLM and return the result
