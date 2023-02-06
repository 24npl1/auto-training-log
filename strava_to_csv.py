import requests
import json
from pandas.io.json import json_normalize
import pandas as pd
import time
from datetime import datetime, timedelta

# Make Strava auth API call with your 
# client_code, client_secret and code
def generate_token(client_id, client_secret, code):
  """Generates a unique token in a json for the strava API
  
  Args: 
    - client_id (int) -> client id provided by strava API
    - client_id (str) -> client secret provided by strava API
    - client_id (str) -> code found in the strava token URL : 
      http://localhost/exchange_token?state=&code={YOUR_CODE_HERE}&scope=read,activity:read_all,profile:read_all
    
  Output:
    - None, but writes the user's token into a JSON titled strava_tokens.json
  
  """
  response = requests.post(
                      url = 'https://www.strava.com/oauth/token',
                      data = {
                              'client_id': client_id,
                              'client_secret': client_secret,
                              'code': code,
                              'grant_type': 'authorization_code'
                              }
                  )
  #Save json response as a variable
  strava_tokens = response.json()
  # Save tokens to file
  with open('strava_tokens.json', 'w') as outfile:
      json.dump(strava_tokens, outfile)


def refresh_token(client_id, client_secret, refresh_token):
    """
    Refreshes the token used to connect to Strava API.

    Parameters:
    client_id (str): The client ID provided by Strava.
    client_secret (str): The client secret provided by Strava.
    refresh_token (str): The refresh token used to refresh the access token.

    Returns:
    response: The response from the API request to refresh the token.

    """
    response = requests.post(url='https://www.strava.com/api/v3/oauth/token',
                             data={'client_id': client_id,
                                   'client_secret': client_secret,
                                   'grant_type': 'refresh_token',
                                   'refresh_token': refresh_token})
    return response

def write_token(token):
  with open('strava_tokens.json', 'w') as outfile:
    json.dump(token, outfile)

def get_token():
  with open('strava_tokens.json', 'r') as token:
    data = json.load(token)
  return data

def check_token(client_id, client_secret, token):
  """
    Check if the given token is still valid, and if not, refresh it.

    Parameters:
    client_id (str): Strava API client ID
    client_secret (str): Strava API client secret
    token (dict): Strava token with keys 'access_token', 'refresh_token', and 'expires_at'

    Returns:
    bool: True if the token was successfully refreshed, False otherwise.
    """
  if token['expires_at'] < time.time():
    print('Refreshing token!')
    new_token = refresh_token(client_id, client_secret, token['refresh_token'])
    strava_token = new_token.json()
    # Update the file
    write_token(strava_token)
    return True
  return False

def generate_csv(client_id, client_secret, period = 7,
                attributes = ["name", "start_date_local", "type", "distance", "moving_time", "has_heartrate", "average_heartrate"], 
                filename = f"week_ending_{datetime.today().strftime('%Y-%m-%d')}"):
  """
  Function to generate a csv file with the user's activities data from Strava API.
  
  Parameters:
  client_id (str): Strava API client id.
  client_secret (str): Strava API client secret.
  period (int, optional): The number of days from today to retrieve the activity data from. Default is 7.
  attributes (list, optional): A list of the activity attributes to retrieve from Strava API. 
                                Default is ["name", "start_date_local", "type", "distance", "moving_time", 
                                          "has_heartrate", "average_heartrate"].
  filename (str, optional): The name of the file to be generated. 
                            Default is "week_ending_[today's date in YYYY-MM-DD format]"
  
  Returns:
  None
  """
  # Get the tokens from file to connect to Strava
  strava_tokens = get_token()
  if check_token(client_id, client_secret, strava_tokens) == False:
    strava_tokens = get_token()
    
  # Loop through all activities
  page = 1
  access_token = strava_tokens['access_token']
  url = "https://www.strava.com/api/v3/activities/"
  # Create the dataframe ready for the API call to store your activity data
  activities = pd.DataFrame(columns = attributes)
  flag = False
  start_date = (datetime.today() - timedelta(days = period - 1)).strftime('%Y-%m-%d') if period else None
  while True:
      print(f"Processing page {page}...")
      # get page of activities from Strava
      r = requests.get(url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page))
      r = r.json()

      # if no results then exit loop
      if not r or flag:
          break
      
      # otherwise add new data to dataframe
      for x in range(len(r)):
        if flag:
          break
        for attr in attributes:
          # convert meters to miles
          if start_date:
            if attr == "start_date_local":
              if r[x][attr][:10] < start_date:
                flag = True 
                activities = activities.iloc[:-1]
                break
              else:
                r[x][attr] = pd.Timestamp(r[x][attr][:10]).day_name()
          if attr == "distance":
            r[x][attr] = round(r[x][attr] * 0.000621371, 2)
          # convert seconds to minutes
          if attr == "moving_time":
            r[x][attr] = round(r[x][attr] / 60, 2)
          if attr == "has_heartrate" and r[x][attr] == False:
            r[x]["average_heartrate"] = "n/a"
          if attr != "has_heartrate":
            activities.loc[x + (page-1)*200,attr] = r[x][attr]
      
      # increment page
      page += 1
  
  # Export your activities file as a csv 
  # to the folder you're running this script in
  activities = activities.set_index('name')
  activities = activities.rename(str.upper, axis='columns')
  activities = activities.rename(columns = {'START_DATE_LOCAL' : "WEEKDAY"})
  activities = activities.drop("HAS_HEARTRATE", axis= 1)
  activities.iloc[::-1].to_csv(f'./activities/{filename}.csv')
  print("CSV created!")

