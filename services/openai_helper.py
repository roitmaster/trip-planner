from openai import OpenAI
import json
from dotenv import load_dotenv
load_dotenv()


# Helper function to interact with ChatGPT 
def get_chatgpt_response(prompt):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content.strip()
    if content.startswith('```json'):
        content = '\n'.join(response.choices[0].message.content.strip().split('\n')[1:-1])
    return json.loads(content)
