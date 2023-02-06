import gspread
from oauth2client.service_account import ServiceAccountCredentials

def upload_csv(csv_name, target, scope = ["https://spreadsheets.google.com/feeds", 
                         'https://www.googleapis.com/auth/spreadsheets',
                        "https://www.googleapis.com/auth/drive.file", 
                        "https://www.googleapis.com/auth/drive"]):

    """
    Uploads a CSV file to Google Sheets using the Google Sheets API.

    Arguments:
    csv_name -- a string representing the name of the CSV file (without the '.csv' extension)
    target -- a string representing the name of the target Google Sheets document
    scope -- a list of strings representing the Google Sheets API scopes (default is a list of all required scopes)

    Returns:
    None
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open(target)
    print("Uploading to Google Sheets...")
    with open(f'{csv_name}.csv', 'r') as file_obj:
        content = file_obj.read()
        client.import_csv(spreadsheet.id, data=content)
    print("Upload Sucsessful!")