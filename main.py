import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from pyairtable import Api
import openai

# Load the environment variables from the .env file
load_dotenv()
# Assuming you have an Airtable API key and base ID
api_key = os.getenv('AIRTABLE_API_KEY')
base_id = os.getenv('AIRTABLE_BASE')


client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# Create an instance of the Airtable class
api = Api(api_key)

table = api.table(base_id, 'people')
descrip = api.table(base_id, 'descs')

# Get all records from the table
records = table.all()

# Iterate through each record


def summarize_object_with_chatgpt(obj):
    # Convert the object to a JSON string
    obj_str = json.dumps(obj, ensure_ascii=False)

    try:
        # Generate a summary using the OpenAI ChatGPT API in turbo mode
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Adjust the model if necessary
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate a compelling summary for why someone should date this person. Make it one paragraph: {obj_str}"}
            ],
            temperature=0.7,
            max_tokens=150,  # Adjust based on how long you expect the summary to be
            stop=None
        )

        response2 = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Adjust the model if necessary
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate a holistic description for who the ideal partner for this person would be. Include specifics. Make it one paragraph: {obj_str}"}
            ],
            temperature=0.7,
            max_tokens=150,  # Adjust based on how long you expect the summary to be
            stop=None
        )

        # Extract and return the summary text
        # Ensure the response structure is navigated correctly based on the API's response format
        return (response.choices[0].message.content.strip(), response2.choices[0].message.content.strip())
    except Exception as e:
        return f"An error occurred: {str(e)}"


for record in records:
    # Access the fields of the record
    fields = record['fields']

    print(fields["name"])

    # Convert fields to a string
    fields_str = json.dumps(fields)

    # Use OpenAI to generate a summary
    summary = summarize_object_with_chatgpt(fields)

    descrip.create({

        "people": [record['id']],
        "desc": summary[0],
        "want": summary[1],
        "Name": fields["name"]

    })

    # Print the summary
    print(summary)
