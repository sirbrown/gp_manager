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

def get_google_media_filenames(service):
    """Retrieves a set of all media filenames (photos and videos) from Google Photos."""
    print("Fetching list of media from Google Photos... (This may take a while for large libraries)")
    media_filenames = set()
    next_page_token = None
    while True:
        try:
            results = service.mediaItems().list(
                pageSize=100, pageToken=next_page_token).execute()
            
            items = results.get('mediaItems', [])
            for item in items:
                media_filenames.add(item['filename'])
            
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    print(f"Found {len(media_filenames)} media items in Google Photos.")
    return media_filenames

def find_local_media_not_in_google_photos(local_folder, google_media_filenames):
    """Finds local media files that are not in the Google Photos library."""
    print("Scanning local folder for photos and videos...")
    media_not_found = []
    
    # Supported photo and video extensions
    supported_extensions = {
        # Photo formats
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.raw',
        # Video formats
        '.mpg', '.mpeg', '.mp4', '.mkv', '.mov', '.avi', '.wmv', '.flv', '.3gp', '.m4v', '.mts', '.m2ts'
    }

    for root, _, files in os.walk(local_folder):
        for file in files:
            # Check if the file extension is in our supported list
            if os.path.splitext(file)[1].lower() in supported_extensions:
                # Check if the filename is not in the set from Google Photos
                if file not in google_media_filenames:
                    media_not_found.append(os.path.join(root, file))

    return media_not_found

def main():
    """Main function to run the script."""
    service = get_google_photos_service()
    google_media_filenames = get_google_media_filenames(service)

    local_folder = input("Enter the full path to the folder you want to check: ")

    if not os.path.isdir(local_folder):
        print("Error: The provided path is not a valid directory.")
        return

    missing_media = find_local_media_not_in_google_photos(local_folder, google_media_filenames)

    output_file = 'media_not_in_google_photos.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for media_path in missing_media:
            f.write(f"{media_path}\n")

    print(f"\nFinished!")
    if missing_media:
        print(f"{len(missing_media)} photos or videos were not found in Google Photos.")
        print(f"A list of these files has been saved to: {output_file}")
    else:
        print("All local media files were found in your Google Photos library.")

if __name__ == '__main__':
    main()