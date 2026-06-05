import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = os.getenv('PROJECT_NAME')

def ocr_summarize(image_bytes):
    # 1. Initialize Vertex AI
    # Project ID: receipt-interepreter-497814
    vertexai.init(project=PROJECT_NAME, location="us-central1")

    # 2. Load Gemini 2.5 Flash Lite (optimized for image processing)
    model = GenerativeModel("gemini-2.5-flash")

    '''with open(image_path, "rb") as f:
        image_bytes = f.read()'''

    image_part = Part.from_data(
        data=image_bytes,
        mime_type="image/jpeg"
    )

    # 4. Create the multimodal prompt
    #I should add a expenditure categorization after (the user will provide the categories,
    #and gemini will try to fit the expense inside one of them)
    prompt = """
    Examine this receipt image. 
    Extract the total spent amount, currency, and date of purchase.
    Return the data strictly in JSON format with the headers date, currency, amount.
    """

    # 5. Generate the interpretation in one step
    response = model.generate_content([prompt, image_part])

    print(response.text)


