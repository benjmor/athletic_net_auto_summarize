# AthleticSummary.net

Generates a human-readable summary of Athletic.net athletics results using Generative AI.

Supports both Track and Cross-Country meets.

# Usage

This solution now runs as a website! Just provide your school ID (number from the URL when you look at the team page) and the website will pull results from the latest meet with results.

Optionally, you can provide a specific meet ID (again, pull it from the meet URL) and the website will generate a report for that meet.

Review the output, edit as needed, and post on your website, social media, school newspaper, or just send it to grandma and grandpa.

# Development and Architecture

The website can be invoked in one of two ways:

1. Provide a meet ID and school name. This will query the summarizer's results DB to check if that meet has already been summarized and grab info from it. If it has results, 
2. [Future state] Provide just a school ID. This will look for the latest result for that school on Athletic.net and generate results for it. (Note to developer: this will require specifying TF or XC).