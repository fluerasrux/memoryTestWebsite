import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import json

# Path to your service account key JSON file
SERVICE_ACCOUNT_KEY_PATH = 'ServiceAccountKey.json'

# Initialize the Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': '...'
    })

# Code mappings for responses
codes = {
    "yes_no": {"yes": 1, "no": 0},
    "study_time": {"morning": 1, "afternoon": 2, "evening": 3, "night": 4},
    "classification": {
        "freshman": 1, "sophomore": 2, "junior": 3, "senior": 4,
        "5th year": 5, "grad student": 6
    }
}

# Function to apply coding to data
def apply_coding(value, category):
    return codes[category].get(value.lower(), value)  # Keep original if not found

# Function to download Firebase data as JSON
def download_firebase_data():
    ref = db.reference('/')
    data = ref.get()
    with open('firebase_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print("Data successfully downloaded and saved to firebase_data.json")
    return data  # Return the data for further processing

# Run the download function
data = download_firebase_data()

# Load the JSON data
with open('firebase_data.json') as f:
    data = json.load(f)

# Extract and format participant data
participants = data['Participants']

# Process Firebase data for export
def process_data(data):
    records = []
    for participant_id, details in data.items():
        record = {
            "participantID": participant_id,
            "age": details["age"],
            "classif": apply_coding(details["classif"], "classification"),
            "darkMode": apply_coding(details["darkMode"], "yes_no"),
            "eyeDisorders": apply_coding(details["eyeProb"], "yes_no"),
            "favColor": details["favoriteColor"],
            "studyTime": apply_coding(details["studyTime"], "study_time"),
            "testTime": details["submission-time"],
            "test1%": details["experimentResults"][0]["percentage"] if len(details["experimentResults"]) > 0 else None,
            "test2%": details["experimentResults"][1]["percentage"] if len(details["experimentResults"]) > 1 else None,
            "test3%": details["experimentResults"][2]["percentage"] if len(details["experimentResults"]) > 2 else None,
            "test4%": details["experimentResults"][3]["percentage"] if len(details["experimentResults"]) > 3 else None,
            "shownLists": [result["shownList"] for result in details["experimentResults"]],
            "responses": [result["response"] for result in details["experimentResults"]]
        }
        records.append(record)
    
    return records  # Return the records for DataFrame creation

# Call the process_data function and create DataFrame
rows = process_data(participants)
df = pd.DataFrame(rows)
df.to_csv('output.csv', index=False)
print("Data successfully saved to output.csv")
