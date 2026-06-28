import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = os.getenv('PROJECT_NAME')

def ocr_summarize(image_bytes, categories):
    # 1. Initialize Vertex AI
    vertexai.init(project=PROJECT_NAME, location="us-central1")

    # 2. Load Gemini 2.5 Flash Lite (optimized for image processing)
    model = GenerativeModel("gemini-2.5-flash")

    image_part = Part.from_data(
        data=image_bytes,
        mime_type="image/jpeg"
    )

    

    # 3. Create the multimodal prompt
    prompt = f"""
    Examine this receipt image. 
    Extract the expense category, total spent amount, currency, and date of purchase.
    Try to fit the expense in one of the following categories: {categories}, but if it fails,
    categorize it as "Others".
    Return the data strictly in JSON format with the headers date (in ISO 8601 format), category, currency (in ISO 4217 format), amount.
    No text elements outside of the curly brackets.
    """

    # 5. Generate the interpretation in one step
    response = model.generate_content([prompt, image_part])

    return response.text


