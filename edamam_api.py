import requests
from dotenv import load_dotenv
import os


load_dotenv()


EDAMAM_API_ENDPOINT = "https://api.edamam.com/api/food-database/v2/parser"
APP_ID = os.getenv("APP_ID")   # Replace with your App ID from Edamam
APP_KEY = os.getenv("APP_KEY") # Replace with your App Key from Edamam

def get_groceries_from_edamam(query):
    """
    Fetch a list of groceries based on user query using the Edamam API.
    
    Args:
    - query (str): The user's search term.

    Returns:
    - List[str]: A list of grocery names.
    """
    parameters = {
        "ingr": query,
        "app_id": APP_ID,
        "app_key": APP_KEY
    }
    response = requests.get(EDAMAM_API_ENDPOINT, params=parameters)
    response_data = response.json()
    #print(response_data)

    # Extracting the grocery names from the response
    groceries = [item['food']['label'] for item in response_data['hints']]
    
    return groceries
