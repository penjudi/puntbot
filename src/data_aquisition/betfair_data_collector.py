import requests
import json
import pandas as pd

# Betfair API credentials
username = "penjud"
password = "%2s8ThBv&u5#s$Wg"

# Function to make API requests and handle responses
def make_api_request(endpoint, params=None):
    # Set API URL and headers
    api_url = "https://api.betfair.com/ex/race/betfair/v1/" + endpoint
    headers = {"X-Application-Id": "YOUR_APP_ID", "X-Authentication": username + ":" + password}

    # Make API request
    response = requests.get(api_url, params=params, headers=headers)

    # Check response status code
    if response.status_code != 200:
        raise Exception("API request failed:", response.status_code)

    # Parse JSON response
    response_data = json.loads(response.text)

    return response_data

# Function to extract historical race data for a specified date range
def extract_historical_race_data():
    # Get today's date
    from datetime import date
    today = date.today()

    # Calculate date 5 years ago
    five_years_ago = today - pd.DateOffset(years=5)

    # Set date range parameters
    params = {
        "dateFrom": five_years_ago.strftime("%Y-%m-%d"),
        "dateTo": today.strftime("%Y-%m-%d")
    }

    # Initialize empty DataFrame
    historical_data = pd.DataFrame()

    # Make API request to retrieve race events
    race_events_response = make_api_request("raceEventByDateRange", params=params)

    # Iterate through each race event
    for race_event in race_events_response["results"]:
        # Get race details and extract relevant data
        race_details_response = make_api_request("raceDetails", params={"raceId": race_event["raceId"]})
        race_data = extract_race_data(race_details_response)

        # Append race data to DataFrame
        historical_data = historical_data.append(race_data, ignore_index=True)

    return historical_data

# Function to extract relevant data from a race details response
def extract_race_data(race_details_response):
    race_data = {
        "raceId": race_details_response["raceId"],
        "raceTime": race_details_response["raceTime"],
        "raceType": race_details_response["raceType"],
        "venue": race_details_response["venue"],
        "distance": race_details_response["distance"],
        "runners": []
    }

    # Iterate through each runner in the race
    for runner in race_details_response["runners"]:
        runner_data = {
            "runnerId": runner["runnerId"],
            "horseName": runner["horseName"],
            "jockey": runner["jockeyName"],
            "trainer": runner["trainerName"],
            "odds": runner["startingOdds"]
        }

        race_data["runners"].append(runner_data)

    return race_data

if __name__ == "__main__":
    # Extract historical race data
    historical_data = extract_historical_race_data()

    # Save historical race data to a CSV file
    historical_data.to_csv("historical_race_data.csv", index=False)

    # Save historical race data to a CSV file
    historical_data.to_csv("historical_race_data.csv", index=False)
