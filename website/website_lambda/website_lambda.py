import json
import boto3
import os
import logging
import re
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError
from botocore.config import Config


"""
This is the main Lambda handler for the website.
"""

logging.basicConfig(level=logging.DEBUG)
REGION = "us-east-1"


class Claude3Wrapper:
    """Encapsulates Claude 3 model invocations using the Amazon Bedrock Runtime client."""

    def __init__(self, client=None):
        """
        :param client: A low-level client representing Amazon Bedrock Runtime.
                       Describes the API operations for running inference using Bedrock models.
                       Default: None
        """
        self.client = client

    # snippet-start:[python.example_code.bedrock-runtime.InvokeAnthropicClaude3Text]
    def invoke_claude_3_with_text(self, prompt):
        """
        Invokes Anthropic Claude 3 Haiku to run an inference using the input
        provided in the request body.

        :param prompt: The prompt that you want Claude 3 to complete.
        :return: Inference response from the model.
        """

        # Initialize the Amazon Bedrock runtime client
        client = self.client or boto3.client(
            service_name="bedrock-runtime",
            region_name=REGION,
        )

        # Invoke Claude 3 with the text prompt
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        try:
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 4096,
                        "messages": [
                            {
                                "role": "user",
                                "content": [{"type": "text", "text": prompt}],
                            }
                        ],
                    }
                ),
            )

            # Process and print the response
            result = json.loads(response.get("body").read())
            input_tokens = result["usage"]["input_tokens"]
            output_tokens = result["usage"]["output_tokens"]
            output_list = result.get("content", [])

            logging.debug("Invocation details:")
            logging.debug(f"- The input length is {input_tokens} tokens.")
            logging.debug(f"- The output length is {output_tokens} tokens.")

            logging.debug(f"- The model returned {len(output_list)} response(s):")
            result_string = ""
            for output in output_list:
                logging.debug(output["text"])
                result_string = result_string + "\n" + output["text"]

            return result_string

        except ClientError as err:
            logging.error(
                "Couldn't invoke Claude 3 Haiku. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    # snippet-end:[python.example_code.bedrock-runtime.InvokeAnthropicClaude3Text]


def send_prompt_to_llm_and_save_to_s3(
    prompt,
    s3_client,
    bucket_name,
    key,
    numbered_list_prompt_path,
):
    """
    This function will take a prompt, pass it to Claude3, save it to S3, then
    """
    config = Config(retries={"max_attempts": 3, "mode": "adaptive"})
    claude_client = Claude3Wrapper(
        boto3.client(
            service_name="bedrock-runtime",
            region_name=REGION,
            config=config,
        )
    )
    print(f"Starting Claude call with prompt: {json.dumps(prompt)}")
    full_response = claude_client.invoke_claude_3_with_text(prompt)
    logging.debug(f"Full response: {full_response}")
    # try:
    #     numbered_prompt = (
    #         s3_client.get_object(
    #             Bucket=bucket_name,
    #             Key=numbered_list_prompt_path,
    #         )["Body"]
    #         .read()
    #         .decode("utf-8")
    #     )
    #     bedrock_numbered_list_response = claude_client.invoke_claude_3_with_text(
    #         numbered_prompt
    #     )
    #     full_response = (
    #         full_response
    #         + "\n### Event-by-Event Results"
    #         + bedrock_numbered_list_response
    #     )
    # except Exception as ex:
    #     print(f"Error getting numbered list prompt: {ex}")
    #     pass
    s3_client.put_object(
        Body=full_response,
        Bucket=bucket_name,
        Key=key,
    )
    return full_response


def get_school_name(school_id):
    """
    This function will return the school name from the request body.
    """
    # TODO - Make it better!
    return school_id


def lambda_handler(event, context):
    print(event)
    cors_headers = {
        "Access-Control-Allow-Origin": "*",  # Required for CORS support to work
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    }
    if event.get("body", None) is None:
        return {"statusCode": 400, "headers": cors_headers, "body": "No body"}

    # Do some data validation -- ensure that the number is 5 digits and the school name is 50 characters or less
    s3_client = boto3.client("s3")
    parsed_body = json.loads(event["body"])
    parsed_body["read_only"] = os.getenv("READ_ONLY", True)
    meet_id = parsed_body["meet_id"]
    school_id = str(parsed_body["school_id"]).strip()
    school_name = get_school_name(
        school_id
    )  # TODO - get the school name from its ID, or pull it from a DDB I maintain
    file_path_to_find_or_create = f"{meet_id}/{school_name}/results.txt"
    raw_llm_submission = f"{meet_id}/{school_name}/llm_prompt.txt"
    api_response_key = f"{meet_id}/api_response.json"
    numbered_list_prompt_path = f"{meet_id}/{school_name}/numbered_list_prompt.txt"
    bucket_name = os.getenv("DATA_BUCKET_NAME", "athletic-net-summaries-data-bucket")
    numbered_list_prompt_content = None

    # Check if the requested results already exist -- return them if they do
    if len(school_name) > 0:  # explicitly skip empty names -- they are trouble.
        try:
            llm_content = (
                s3_client.get_object(
                    Bucket=bucket_name,
                    Key=raw_llm_submission,
                )["Body"]
                .read()
                .decode("utf-8")
            )
        except Exception:
            llm_content = None
        try:
            numbered_list_prompt_content = (
                s3_client.get_object(
                    Bucket=bucket_name,
                    Key=numbered_list_prompt_path,
                )["Body"]
                .read()
                .decode("utf-8")
            )
        except Exception:
            numbered_list_prompt_content = None
        if llm_content is not None:
            try:
                file_content = (
                    s3_client.get_object(
                        Bucket=bucket_name,
                        Key=file_path_to_find_or_create,
                    )["Body"]
                    .read()
                    .decode(encoding="utf-8", errors="replace")
                ).replace("\uFFFD", "--")
            except Exception as ex:
                try:
                    logging.debug(f"Sending this content to Claude: {llm_content}")
                    file_content = send_prompt_to_llm_and_save_to_s3(
                        prompt=llm_content,
                        s3_client=s3_client,
                        bucket_name=bucket_name,
                        key=file_path_to_find_or_create,
                        numbered_list_prompt_path=numbered_list_prompt_path,
                    )
                except Exception as ex:
                    logging.error(repr(ex))
                    file_content = "Prompt was not passed to the LLM; you can send the below prompt manually."
            return {
                "isBase64Encoded": False,
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps(
                    {
                        "file_content": file_content
                        + "\n\nMore information about upcoming track meets can be found at [www.athletic.net](www.athletic.net), or by reaching out to the school's coach.",
                        "llm_content": llm_content,
                        "numbered_list_prompt_content": numbered_list_prompt_content,
                    }
                ),
            }

    all_objects = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=meet_id,
    )
    # If there are no files at all, then skip this section and kick off a results generation
    if all_objects["KeyCount"] > 0:
        # See if a placeholder file exists -- used to prevent duplicate runs
        # placeholder.txt is a good proxy of whether a Lambda is [currently running or failed ungracefully] OR [never ran or completed successfully]
        try:
            placeholder_attributes = s3_client.get_object_attributes(
                Bucket=bucket_name,
                Key=f"{meet_id}/placeholder.txt",
                ObjectAttributes=["ObjectSize"],
            )
        except Exception as ex:
            logging.error(f"Error while looking up placeholder: {repr(ex)}")
            placeholder_attributes = None

        # Get a list of all the schools in the tournament so that the user knows what they can choose from
        # This logic just says "find all the subkeys within this tournament's key"
        # But make sure to exclude the `temp_results` folder
        school_set = set()
        for obj in all_objects["Contents"]:
            # Don't include files in the root of the tournament
            if len(obj["Key"].split("/")) > 2 and not re.search(
                r"temp_results", obj["Key"]
            ):
                school_set.add(obj["Key"].split("/")[1])

        # Get data to display the school list if there are schools present
        logging.warning(f"school_set is {school_set}")
        if len(school_set) > 0:
            school_data = "\n\n".join(sorted(list(school_set)))
        # Otherwise, display a message indicating the status
        else:
            # Placeholder is present but no school results ready -- have the user wait for results
            print(f"This is the placeholder_attributes: {placeholder_attributes}")
            if placeholder_attributes is not None and (
                (placeholder_attributes["LastModified"] + timedelta(hours=1))
                > datetime.now(tz=timezone.utc)
            ):
                school_data = "Still generating results! Check back soon!\nConsider opening a GitHub issue at https://github.com/benjmor/athletic_net_auto_summarize/issues if this message persists."
            # no school results are present AND (the placeholder file is missing or outdated) -- data should be regenerated.
            else:
                school_data = "No schools found; will attempt to regenerate. Check back in about an hour."
                s3_client.put_object(
                    Body="Placeholder during generation.",
                    Bucket=bucket_name,
                    Key=f"{meet_id}/placeholder.txt",
                )
                lambda_client = boto3.client("lambda")
                lambda_client.invoke(
                    FunctionName=os.environ["ATHLETIC_NET_SUMMARY_LAMBDA_NAME"],
                    InvocationType="Event",
                    Payload=json.dumps(parsed_body),
                )
            return {
                "isBase64Encoded": False,
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps(
                    {
                        "file_content": school_data,
                        "llm_content": "N/A",
                        "numbered_list_prompt_content": "N/A",
                    }
                ),
            }
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps(
                {
                    "file_content": (
                        "Meet exists, but school does not. "
                        + "Check that your school name matches the official name. "
                        + f"Schools with results:\n\n{school_data}"
                    ),
                    "llm_content": "N/A",
                    "numbered_list_prompt_content": numbered_list_prompt_content,
                }
            ),
        }

    # Put a placeholder file in the S3 bucket and then trigger the Lambda to generate the LLM prompts and results
    s3_client.put_object(
        Body="Placeholder during generation.",
        Bucket=bucket_name,
        Key=f"{meet_id}/placeholder.txt",
    )
    lambda_client = boto3.client("lambda")
    lambda_client.invoke(
        FunctionName=os.environ["ATHLETIC_NET_SUMMARY_LAMBDA_NAME"],
        InvocationType="Event",
        Payload=json.dumps(parsed_body),
    )
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": cors_headers,
        "body": json.dumps(
            {
                "file_content": "Results not yet generated, will attempt to generate them. Check back in about 15 minutes."
                + "\n\nNote: Huge meets (eg. Penn Relays) are not supported through this web interface. Create an Issue [here](https://github.com/benjmor/athletic_net_auto_summarize/issues) if you want results from a specific large meet.",
                "llm_content": "N/A",
                "numbered_list_prompt_content": numbered_list_prompt_content,
            }
        ),
    }


if __name__ == "__main__":
    print(
        lambda_handler(
            {
                "body": json.dumps(
                    {
                        "meet_id": "523486",
                        "school_id": "807",
                        "read_only": "True",
                    }
                )
            },
            {},
        )
    )
