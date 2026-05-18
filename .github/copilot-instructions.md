# Google Photos Manager - AI Instructions

## Project Overview
CLI tool to identify local photos/videos not uploaded to Google Photos by comparing filenames.

## Architecture
Single-file application ([main.py](../main.py)) with three main functions, each covering a distinct concern:
1. `get_google_photos_service()` - OAuth2 authentication
2. `get_google_media_filenames()` - Paginated API fetching
3. `find_local_media_not_in_google_photos()` - Recursive directory scan and comparison

## Google Photos API Setup

### Prerequisites (documented in [README.md](../README.md))
1. Enable Photos Library API in Google Cloud Console
2. Create OAuth Desktop credentials
3. Download as [client_secret.json](../client_secret.json) (must be in project root)

### Authentication Error Handling
- **Missing file**: If `client_secret.json` is not found, the application displays an error message and terminates gracefully
- **Invalid file**: If `client_secret.json` is malformed or contains invalid credentials, the application prompts the user to provide a valid file and terminates gracefully

### Authentication Flow
- **First run**: Opens browser for OAuth consent → creates `token.pickle`
- **Subsequent runs**: Loads cached credentials from `token.pickle`
- **Token refresh**: Automatic if expired and refresh_token available
- **Scope**: `photoslibrary.readonly` (read-only access)

## Key Dependencies
```powershell
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## API Implementation Details

### Pagination Pattern
```python
next_page_token = None
while True:
    results = service.mediaItems().list(pageSize=100, pageToken=next_page_token).execute()
    # Process results['mediaItems']
    next_page_token = results.get('nextPageToken')
    if not next_page_token:
        break
```
- Fetches 100 items per request (API maximum)
- Stores only filenames in set (memory-efficient for large libraries)

### Supported File Extensions
**Photos**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.heic`, `.raw`  
**Videos**: `.mpg`, `.mpeg`, `.mp4`, `.mkv`, `.mov`, `.avi`, `.wmv`, `.flv`, `.3gp`, `.m4v`, `.mts`, `.m2ts`

## Comparison Logic
- **Filename-only matching**: Does NOT compare file hashes or metadata
- **Limitation**: Different files with same name will match (false negative)
- Uses Python `set` for O(1) lookup performance

## Output
Creates `media_not_in_google_photos.txt` with UTF-8 encoding containing full paths (one per line)

## Typical Workflow
```powershell
python main.py
# Prompts for local folder path
# Outputs: "{count} photos/videos not found in Google Photos"
```

## Error Handling

### API Errors
- Exceptions caught with generic `except Exception` during fetch loop
- Skips failed API requests silently and proceeds with the next, potentially resulting in incomplete comparison (no logging or user notification occurs)

### Input Validation
- Directory validation: Checks `os.path.isdir()` before scanning
