import argparse
import boto3
import logging
import os
from athletic_net_summarize import main

"""
This is the main routine for the Athletic.net Summary Lambda. It will query Athletic.net for the meet results and then
create a PROMPT that can be passed to an LLM to generate a summary of a school's results at the tournament.

Unlike previous versions, this version will NOT ever directly send LLM prompts to an LLM. That behavior now occurs synchronously at user-request time.
"""

# Set log level
logging.basicConfig(level=logging.INFO)

DATA_BUCKET = "athletic-net-summaries-data-bucket"


def handler(event, context):
    running_outside_of_lambda = os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None
    print(event)
    # Send ol' Benjamin an email to let him know that people are using the service
    try:
        boto3.client("sns").publish(
            TopicArn=os.environ["SNS_TOPIC_ARN"],
            Message=f"Running Athletic.net summary for {event['tournament']}; requested school is {event['school']}",
        )
    except Exception:
        logging.error("Error publishing to SNS")

    # Generate a Tabroom summary
    meet_id = event["meet_id"]
    percentile_minimum = event.get("percentile_minimum", 25)
    response = main.main(
        school_id=school_id,
        data_bucket=os.getenv("DATA_BUCKET_NAME", DATA_BUCKET),
        meet_id=meet_id,
        percentile_minimum=percentile_minimum,
        sport_name=event["sport_name"],
    )

    # Save the result outputs
    # If we're not in Lambda, assume we're in Windows
    if running_outside_of_lambda:
        # Make the directories as needed
        for school_name in response.keys():
            os.makedirs(f"{meet_id}/{school_name}", exist_ok=True)
            if "llm_prompt" in response[school_name]:
                with open(f"{meet_id}/{school_name}/llm_prompt.txt", "w") as f:
                    f.write(response[school_name]["llm_prompt"])
    else:
        # Save the tournament results to S3
        s3_client = boto3.client("s3")
        bucket_name = os.environ["DATA_BUCKET_NAME"]
        for school_name in response.keys():
            if "llm_prompt" in response[school_name]:
                s3_client.put_object(
                    Body=response[school_name]["llm_prompt"],
                    Bucket=bucket_name,
                    Key=f"{meet_id}/{school_name}/llm_prompt.txt",
                )
            # TODO - Add numbered list prompts
            if "numbered_list_prompt" in response[school_name]:
                s3_client.put_object(
                    Body=response[school_name]["numbered_list_prompt"],
                    Bucket=bucket_name,
                    Key=f"{meet_id}/{school_name}/numbered_list_prompt.txt",
                )
        try:
            # Delete the placeholder to signal to the Lambda that execution is complete
            s3_client.delete_object(
                Bucket=bucket_name, Key=f"{meet_id}/placeholder.txt"
            )
        except Exception:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--meet-id",
        help="Meet ID (typically a 6-digit number) of the meet you want to generate results for.",
        required=False,  # TODO - require again
        default="523486",
    )
    parser.add_argument(
        "-s",
        "--school-id",
        help="School ID (typically a 2-6-digit number) of the meet you want to generate results for.",
        required=False,  # TODO - require again
        default="807",
    )
    args = parser.parse_args()
    meet_id = args.meet_id
    school_id = args.school_id
    event = {
        "meet_id": meet_id,
        "school_id": school_id,
        "sport_name": "track-and-field-outdoor",
        # "percentile_minimum": 0,
    }
    handler(event, {})
