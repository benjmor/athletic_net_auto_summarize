def generate_numbered_list_prompt(
    headers,
):
    return f"""Create a numbered list of the following athletics meet event results, so that each event is a new number in the list, and each event contains results from all athletes in that event.

Don't create separate line-items for different types of results within the same event. For example, the Varsity 100m and Frosh-Soph 100m should both appear on the same numbered line, as plain-English sentences.

ONLY INCLUDE RESULTS FROM THE RESULTS DATA. DO NOT INCLUDE ANY RESULTS THAT DO NOT APPEAR IN RESULT_DATA.

<example>
1. **Event Name**: AthleteName (3rd place of 20 entries) finished with a time of 5:20 and AthleteName6 placed 5th.

2. **Event Name2**: AthleteName2 won 1st place and AthleteName5 took 3rd place. AthleteName3 (8th place) and AthleteName4 (10th place) made semifinals.

3. **Event Name3**: AthleteName3 and AthleteName4 made finals and finished 2nd out of 16 teams, after placing 4th in prelims. In the field of 32 athletes, AthleteName3 earned 6th speaker and AthleteName4 was 7th speaker.
</example>

<result_data>
{"|".join(headers)}
"""
