import json

with open('config.json') as f:
    config = json.load(f)

betfair_api_key = config['betfair']['api_key']

# Initialize the Betfair API client
bf = betfair.Betfair(api_key=betfair_api_key)

# Establish the connection and verify its success
try:
    bf.login()
    print("Successfully connected to Betfair.com.au")
except Exception as e:
    print("Failed to connect to Betfair.com.au:", e)

# Proceed with other Data Acquisition Module tasks...
