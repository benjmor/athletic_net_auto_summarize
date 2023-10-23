# Athletic.net auto-summarizer

This script will generate a human-readable summary of Athletic.net athletics results using ChatGPT.

As of October 2023, this has only been tested on cross-country meets. Track support coming soon!

# Usage

To run this script, you will need Python 3.7+, an OpenAI API key, and an Internet connection.

0. Download this repository, or just the `athleticnet_summarize.py` file. Change directories so you are in the same directory as the script.
1. Find your school's Athletic.net school ID. This is visible in the URL if you navigate to your team page on the athletic.net website.
2. Find the meet ID (usually 6 digits) you want to generate a report for. This can be found in the URL if you click on a meet listed in the team calendar section.
3. Pass these values to the script using the following syntax (you may need to use `python3` in some instances):
```bash
python athleticnet_summarize.py -i <YOUR_SCHOOL_ID> -m <YOUR_MEET_ID>
```
4. The script will generate a meet summary in plain text in a subfolder of your current directory. Review the output, edit as needed, and post on your website, social media, school newspaper, or just send it to grandma and grandpa.


# Cost

The cost of this solution comes from the fees charged by OpenAI for ChatGPT usage.

The cost varies a little bit based on how large your results set is.

In general, you can conservatively estimate that it costs around **3 cents** to generate a report for a single meet for a school.