import json
import os
import requests

API_USERNAME = os.environ.get("API_USERNAME")
API_PASSWORD = os.environ.get("API_PASSWORD")
API_URL = os.environ.get("API_URL")


def fetch_movies_data(page_num):
    try:
        response = requests.get(
            API_URL,
            params={"page": page_num},
            data={"id": API_USERNAME, "secret": API_PASSWORD},
        )

        if not response:
            print("Retrying....")
            fetch_movies_data(page_num)

        json_format = response.json()

        return json_format
    except Exception as Err:
        fetch_movies_data(page_num)
