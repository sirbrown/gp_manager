As an expert in Python programming with in-depth knowledge of the Google Photos API, I will provide you with a Python script to identify which photos from a local folder and its subfolders are not already uploaded to your Google Photos account.

How the Script Works

The script will perform the following actions:

Authenticate with your Google Account: It will use the Google Photos API to securely connect to your account. The first time you run it, you'll be prompted to authorize access through your web browser. This process creates a token.json file to remember your authorization for future runs.

Retrieve a list of your photos: It will fetch the filenames of all the photos currently in your Google Photos library, including those in synchronized accounts.

Scan your local folder: You will be asked to provide the path to the folder on your computer that you want to check. The script will then recursively scan this folder and its subfolders for image files.

Compare and identify missing photos: It will compare the filenames of your local photos with the list from Google Photos.

Log the results: The full path of any local photo that is not found in your Google Photos will be saved to a text file named photos_not_in_google_photos.txt.

Prerequisites

Before running the script, you need to set up your environment and obtain credentials to access the Google Photos API.

1. Enable the Google Photos Library API:

Go to the Google Cloud Console.

Create a new project or select an existing one.

In the navigation menu, go to APIs & Services > Library.[1][2]

Search for "Photos Library API" and enable it for your project.[1][2]

2. Configure your OAuth consent screen:

In the Google Cloud Console, go to APIs & Services > OAuth consent screen.

Choose the "External" user type and click "Create".

Fill in the required information (App name, User support email, Developer contact information) and save. You can skip the "Scopes" and "Test users" sections for this purpose.

3. Create OAuth 2.0 Credentials:

Go to APIs & Services > Credentials.[2][3]

Click Create Credentials and select OAuth client ID.[2][3]

Choose "Desktop app" as the application type.[2][3]

Give it a name and click "Create".

A window will pop up with your client ID and client secret. Click Download JSON and save the file as client_secret.json in the same directory where you will save the Python script.[3]

4. Install the necessary Python libraries:

Open your terminal or command prompt and install the following libraries using pip:

code
Bash
download
content_copy
expand_less
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
The Python Code

Save the following code as a Python file (e.g., check_google_photos.py) in the same directory where you saved your client_secret.json file.

code
Python
download
content_copy
expand_less
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes required to access the Google Photos library
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
API_SERVICE_NAME = 'photoslibrary'
API_VERSION = 'v1'

def get_google_photos_service():
    """Authenticates with the Google Photos API and returns a service object."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)

def get_google_photos_filenames(service):
    """Retrieves a set of all filenames from Google Photos."""
    print("Fetching list of photos from Google Photos... (This may take a while for large libraries)")
    photo_filenames = set()
    next_page_token = None
    while True:
        try:
            results = service.mediaItems().list(
                pageSize=100, pageToken=next_page_token).execute()
            
            items = results.get('mediaItems', [])
            for item in items:
                photo_filenames.add(item['filename'])
            
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    print(f"Found {len(photo_filenames)} photos in Google Photos.")
    return photo_filenames

def find_local_photos_not_in_google_photos(local_folder, google_photos_filenames):
    """Finds local photos that are not in the Google Photos library."""
    print("Scanning local folder for photos...")
    photos_not_found = []
    supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.raw'}

    for root, _, files in os.walk(local_folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in supported_extensions:
                if file not in google_photos_filenames:
                    photos_not_found.append(os.path.join(root, file))

    return photos_not_found

def main():
    """Main function to run the script."""
    service = get_google_photos_service()
    google_photos_filenames = get_google_photos_filenames(service)

    local_folder = input("Enter the full path to the folder you want to check: ")

    if not os.path.isdir(local_folder):
        print("Error: The provided path is not a valid directory.")
        return

    missing_photos = find_local_photos_not_in_google_photos(local_folder, google_photos_filenames)

    output_file = 'photos_not_in_google_photos.txt'
    with open(output_file, 'w') as f:
        for photo_path in missing_photos:
            f.write(f"{photo_path}\n")

    print(f"\nFinished!")
    if missing_photos:
        print(f"{len(missing_photos)} photos were not found in Google Photos.")
        print(f"A list of these photos has been saved to: {output_file}")
    else:
        print("All local photos were found in your Google Photos library.")

if __name__ == '__main__':
    main()
How to Run the Script

Make sure you have check_google_photos.py and client_secret.json in the same directory.

Open a terminal or command prompt, navigate to that directory, and run the script:

code
Bash
download
content_copy
expand_less
python check_google_photos.py

The first time you run it, a browser window will open asking you to log in to your Google account and grant permission.

After you grant permission, the script will start fetching the list of your photos from Google Photos. This might take some time if you have a large library.

You will then be prompted to enter the full path to the local folder you want to check.

The script will scan your local files and compare them against the list from Google Photos.

Once finished, it will create a file named photos_not_in_google_photos.txt in the same directory, containing the paths to the photos that were not found in your Google Photos account.

Important Considerations

Filename-based matching: This script identifies photos based on their filenames. If you have photos with the same filename but different content, this script will consider them as duplicates. Also, if a photo was renamed after being uploaded to Google Photos, this script will not be able to match it.

API Quotas: The Google Photos API has usage quotas. For most personal use cases, this should not be an issue.

Security: The client_secret.json file and the token.pickle file contain sensitive information. Do not share them.

Sources
help
dev.to
youtube.com
medium.com
Google Search Suggestions
Display of Search Suggestions is required when using Grounding with Google Search. Learn more
Google Photos API python list user's photos
Google Photos API python authentication
google photos api python client library
google photos api search media items by filename
google photos api get photo fingerprint