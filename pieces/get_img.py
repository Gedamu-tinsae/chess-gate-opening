import os
import requests

# Define the base URL and theme for the pieces (e.g., 'alpha' theme)
THEME = 'classic'  # Change this to switch between themes  (e.g., neo, alpha, classic).
BASE_URL = f'https://images.chesscomfiles.com/chess-themes/pieces/{THEME}/150/'

# URLs for chess pieces using the new theme
PIECES_URLS = {
    'wp': f'{BASE_URL}wp.png',  # White Pawn
    'wR': f'{BASE_URL}wr.png',  # White Rook
    'wN': f'{BASE_URL}wn.png',  # White Knight
    'wB': f'{BASE_URL}wb.png',  # White Bishop
    'wQ': f'{BASE_URL}wq.png',  # White Queen
    'wK': f'{BASE_URL}wk.png',  # White King
    'bp': f'{BASE_URL}bp.png',  # Black Pawn
    'bR': f'{BASE_URL}br.png',  # Black Rook
    'bN': f'{BASE_URL}bn.png',  # Black Knight
    'bB': f'{BASE_URL}bb.png',  # Black Bishop
    'bQ': f'{BASE_URL}bq.png',  # Black Queen
    'bK': f'{BASE_URL}bk.png'   # Black King
}

# Factor out the path to a variable
path_dir = 'root_folder/pieces/pieces_name'  # Change this to any other path as needed

# Create the directory for pieces if it doesn't exist
if not os.path.exists(path_dir):
    os.makedirs(path_dir)

# Download each piece and save it to the specified directory
for piece_name, url in PIECES_URLS.items():
    print(f'Downloading {piece_name} from {url}...')
    response = requests.get(url)
    
    if response.status_code == 200:
        # Save the image to the specified folder
        with open(f'{path_dir}/{piece_name}.png', 'wb') as file:
            file.write(response.content)
        print(f'{piece_name} downloaded and saved as {piece_name}.png')
    else:
        print(f'Failed to download {piece_name} from {url}')

print("All pieces downloaded.")
