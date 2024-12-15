import os
import requests

# Define the base URL for the sound effects
BASE_URL = 'https://example.com/sounds/'  # Replace with the actual URL where the sounds are hosted

# URLs for sound effects
SOUND_EFFECTS_URLS = {
    'move_sound': f'{BASE_URL}move_sound.wav',
    'capture_sound': f'{BASE_URL}capture_sound.wav',
    'illegal_move_sound': f'{BASE_URL}illegal_move_sound.wav'
}

# Define the path to save sound files
path_dir = 'root_folder/sound'  # Change this to any other path as needed

# Create the directory for sounds if it doesn't exist
if not os.path.exists(path_dir):
    os.makedirs(path_dir)

# Download each sound and save it to the specified directory
for sound_name, url in SOUND_EFFECTS_URLS.items():
    print(f'Downloading {sound_name} from {url}...')
    response = requests.get(url)
    
    if response.status_code == 200:
        # Save the sound file to the specified folder
        with open(f'{path_dir}/{sound_name}.wav', 'wb') as file:
            file.write(response.content)
        print(f'{sound_name} downloaded and saved as {sound_name}.wav')
    else:
        print(f'Failed to download {sound_name} from {url}')

print("All sound effects downloaded.")
