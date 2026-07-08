from google import genai
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Generate AI response
def get_ai_response(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text