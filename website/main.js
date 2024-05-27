function submitForm() {
    // Update to Loading...
    document.getElementById('responseContainer').innerText = "\nLoading...this may take up to 25 seconds for new summary requests...to keep you engaged, here is a joke:\nIs your refrigerator running? Then you'd better go catch it!"
    // Get form data
    const meetId = document.getElementById('meetId').value;
    const schoolId = document.getElementById('schoolId').value;

    // Validate tournament number format
    if (!/^\d{6}$/.test(meetId) || (meetId == "00000")) {  
        alert('Please enter a valid 6-digit number for the Meet ID.');
        return;
    }
    if (!/^\d{3,6}$/.test(schoolId) || (schoolId == "00000")) {
        alert('Please enter a valid 3-to-6-digit number for the School ID.');
        return;
    }

    // Create a JSON object with the form data
    const formData = {
        meet: meetId,
        school: schoolId
    };

    // Perform a POST request to the API Gateway endpoint to send the request
    // Had to manually update after deploying the API GW
    fetch('https://kkl9wqaqpk.execute-api.us-east-1.amazonaws.com/prod/submit_meet', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        // Display the response
        file_content = data['file_content']
        llm_content = data['llm_content'].replace(/\n/g, "\n\n"); // more newlines!
        numbered_list_prompt_content = data['numbered_list_prompt_content']
        display_md = "<md-block>" + "## Meet Summary:\n" + file_content + 
                     "\n## Prompt passed to Claude:\n" + llm_content + "\n" + 
                     "\n## Line-by-Line prompt passed to Claude:\n" + numbered_list_prompt_content + "</md-block>";
        document.getElementById('responseContainer').innerHTML = display_md;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('responseContainer').innerText = 'Error occurred. Please try again later, as this may have been due to high server demand.';
    });
}