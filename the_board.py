import pygame
import sys
import chess
import logging  
import random
import chess.engine
import socket
import threading
import os


pygame.init()
pygame.mixer.init()
logging.basicConfig(level=logging.DEBUG)

#CONSTANTS
#region
# Load sound effects
current_dir = os.path.dirname(__file__)
sound_path = os.path.join(current_dir, "sound\\")
pieces_path = os.path.join(current_dir, "pieces\\")
engine_path = os.path.join(current_dir, "stockfish\\stockfish.exe")

move_sound = pygame.mixer.Sound(sound_path + 'Move.mp3')
capture_sound = pygame.mixer.Sound(sound_path + 'Capture.mp3')


BOARD_WIDTH = 950
BOARD_HEIGHT = 675
THE_BG_COLOR = (48,46,43,255)
GAME_WIDTH = 400
GAME_HEIGHT = 400
MOVE_CANVAS_WIDTH = 400
MOVE_CANVAS_HIGHT = 480
SQUARE_SIZE = 60
GAME_BOARD_Y_OFFSET = 100
GAME_BOARD_X_OFFSET = 50
TEXT_COLOR_WHITE = (255,255,255,255)
TEXT_COLOR_BLACK = (0,0,0,255)
TEXT_COLOR_LIGHT_BLACK = (169, 169, 169, 255)
SQUARE_GREEN = (115,149,82,255)
SQUARE_WHITE = (235,236,208,255)
PROMOTION_MENU_COLOR = (200,180,50,0)
SCORE_COLOR = (0,255,50,255)
CAPTURED_PIECE_SIZE = SQUARE_SIZE // 2
CANVAS_COLOR = (38,37,34,255)
CANVAS_X = (SQUARE_SIZE * 8) + 40
CANVAS_Y = GAME_BOARD_Y_OFFSET
HIGHLIGHT_COLOR =  (80, 80, 80,150) 
BORDER_COLOR = (60, 60, 60,100)
BOT_MOVE_DELAY = 500  # 500 milliseconds = 0.5 second
PLAYER_HIGHLIGHT_COLOR = (0, 255, 0, 128)  # Green with transparency for player's moves
OPPONENT_HIGHLIGHT_COLOR = (255, 0, 0, 128)  # Red with transparency for opponent's moves


#imports
BUTTON_GREEN = (129,182,76,255)
BUTTON_RED = (255,0,50,255)
MENU_WIDTH = 400
MENU_HEIGHT = 500


# THEME DEFINITIONS
board_theme = {
    "Classic": ((235, 236, 208), (115, 149, 82)),  # Light and dark green
    "Blue": ((173, 216, 230), (0, 102, 204)),      # Light blue and dark blue
    "Dark": ((50, 50, 50), (100, 100, 100)),       # Dark shades
}

# Define piece themes and their corresponding folders
piece_themes = {
    "Classic": "classic",
    "Neo": "neo",
    "Alpha": "alpha",
}



font = pygame.font.Font(None,24)
screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))  # Set to board size

# Initialize a chess board
board = chess.Board()

# Set the initial menu
menu = 'Intro_menu'

# Global variables to track the selected piece
selected_square = None
dragging_piece_image = None
dragging_piece = None
dragging_piece_position = None
#endregion

def draw_board(screen, theme_name):
    #the board sqares
    light_color, dark_color = board_theme[theme_name]  # Get colors based on the selected theme
    for row in range(8):
        for col in range(8):
            color = light_color if (row+col) % 2 == 0 else dark_color
            pygame.draw.rect(screen,color,pygame.Rect(col*SQUARE_SIZE, GAME_BOARD_Y_OFFSET + row *SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    #the square labels [a-h] & [1-8]
    for i in range(8):
        label = font.render(str(i+1),True,TEXT_COLOR_BLACK)
        screen.blit(label,( 5, GAME_BOARD_Y_OFFSET + (7-i)*SQUARE_SIZE+5))
        label = font.render(chr(ord('a')+i),True,TEXT_COLOR_BLACK)
        screen.blit(label,(i*SQUARE_SIZE+45, GAME_BOARD_Y_OFFSET + (8*SQUARE_SIZE)-15))

def draw_pieces(screen, board, current_piece_theme):
    global PIECE_IMAGES

    PIECE_IMAGES = {
        f'{color}{piece_type}': pygame.transform.scale(
            pygame.image.load(f'{pieces_path}{piece_themes[current_piece_theme]}/{color}{piece_type}.png'), 
            (SQUARE_SIZE, SQUARE_SIZE)
        ) 
        for color in ['w', 'b'] 
        for piece_type in ['p', 'r', 'n', 'b', 'q', 'k']
    }

    # Draw all pieces on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and square != selected_square: #do not draw dragged piece
            piece_color = 'w' if piece.color == chess.WHITE else 'b'
            piece_type = piece.symbol().lower()
            piece_image = PIECE_IMAGES[piece_color + piece_type]
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            screen.blit(piece_image,(col * SQUARE_SIZE, GAME_BOARD_Y_OFFSET + row * SQUARE_SIZE))

def promotion_menu(screen,selected_promotion_option):
    #setting up the promotion window
    menu_background = pygame.Surface((400,100), pygame.SRCALPHA)  # Use SRCALPHA for transparency)
    menu_background.fill(PROMOTION_MENU_COLOR)
    menu_rect = menu_background.get_rect(center=(700, 50)) #positon of the menu
    screen.blit(menu_background, menu_rect)

    # Pieces for promotion
    if selected_promotion_option == 'Off':
        pieces_name = ['r', 'b', 'n']  # Only rook, bishop, knight
        promotion_pieces = ["wr", "wb", "wn"]  # Only corresponding white pieces
    else:
        pieces_name = ['q', 'r', 'b', 'n']  # Include queen
        promotion_pieces = ["wq", "wr", "wb", "wn"]  # Corresponding pieces

    piece_images = [pygame.transform.scale(PIECE_IMAGES[piece], (SQUARE_SIZE // 2, SQUARE_SIZE // 2)) for piece in promotion_pieces]

    #click detection
    piece_rects = []
    for i , piece_image in enumerate(piece_images):
        piece_rect = piece_image.get_rect(center=(menu_rect.left+75 *(i+1),menu_rect.centery))
        piece_rects.append(piece_rect)
        pygame.draw.rect(screen, PROMOTION_MENU_COLOR,piece_rect.inflate(10,10),2) #border around the pieces
        screen.blit(piece_image,piece_rect)

    # Update only the area where the promotion menu is drawn
    pygame.display.update(menu_rect)

    # Wait for selection 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, piece_rect in enumerate(piece_rects):
                    if piece_rect.collidepoint(mouse_x, mouse_y):
                        piece_name = pieces_name[i]
                        if piece_name == 'q':
                            return chess.QUEEN
                        elif piece_name == 'r':
                            return chess.ROOK
                        elif piece_name == 'b':
                            return chess.BISHOP
                        elif piece_name == 'n':
                            return chess.KNIGHT

#RESET GAME
#region
def reset_game_state(scroll_surface):
    board = chess.Board()
    captured_white,captured_black = [], []
    white_score, black_score = 0, 0
    
    scroll_surface.fill(CANVAS_COLOR)

    player_moves = []
    
    return board,captured_white,captured_black,white_score,black_score, player_moves

def update_captured_pieces(captured_piece, captured_white,captured_black):
    if captured_piece:
        piece_color = 'w' if captured_piece.color == chess.WHITE else 'b'
        if piece_color == 'w':
            captured_black.append(captured_piece.symbol().lower()) # white piece captured by black
        else:
            captured_white.append(captured_piece.symbol().lower())

#SCORE BOARDS AND CAPTURED PIECES
def draw_scoreboard_and_captured_pieces(screen,captured_white, captured_black, white_score, black_score,white_name,black_name):
    font_score_board = pygame.font.Font(None,36)
    
    #Draw black's captured pieces at whites side
    x_offset = 10
    for piece in captured_black:
        screen.blit(pygame.transform.scale(PIECE_IMAGES['w' + piece], (CAPTURED_PIECE_SIZE, CAPTURED_PIECE_SIZE)), (x_offset, 10))
        x_offset += CAPTURED_PIECE_SIZE  # shift and print
    screen.blit(font_score_board.render(f'{black_name}: {black_score}', True, SCORE_COLOR), (10, 50))

    # Draw white's captured pieces at black's side
    x_offset = 10
    for piece in captured_white:
        screen.blit(pygame.transform.scale(PIECE_IMAGES['b' + piece], (CAPTURED_PIECE_SIZE, CAPTURED_PIECE_SIZE)), (x_offset, GAME_HEIGHT+230))
        x_offset += CAPTURED_PIECE_SIZE
    screen.blit(font_score_board.render(f'{white_name}: {white_score}', True, SCORE_COLOR), (10, GAME_HEIGHT + 200))
#endregion

def update_scores(captured_white, captured_black):
    global piece_values
    piece_values = {
        'p': 1,
        'r': 5,
        'n': 3,
        'b': 3,
        'q': 9,
        'k': 0
    }
    
    white_score = sum(piece_values.get(piece.lower(), 0) for piece in captured_white)
    black_score = sum(piece_values.get(piece.lower(), 0) for piece in captured_black)
    
    return white_score, black_score

def draw_canvas(screen, scroll_surface,scroll_x):
    visible_rect = pygame.Rect(scroll_x,0,MOVE_CANVAS_WIDTH,MOVE_CANVAS_HIGHT)
    screen.blit(scroll_surface,(CANVAS_X,CANVAS_Y),visible_rect)

def draw_move_history(scroll_surface, player_moves, scroll_x):
     
    scroll_surface.fill(CANVAS_COLOR)
    font_move_history = pygame.font.Font(None, 24)

    pos_y = 50  # Starting position
    spacing_y = 30  # Spacing between each history
    max_height = 400  # Max column height
    col_width = 200  # Width of each column
    current_x = 10 - scroll_x
    current_y = pos_y

    for idx, move in enumerate(player_moves):
        move_number = idx + 1

        # Check if column needs to wrap
        if current_y > max_height:
            current_x += col_width
            current_y = pos_y

        # Alternate text color based on whether the move is from white or black
        if idx % 2 == 0:
            text_color = TEXT_COLOR_WHITE  # White's move
        else:
            text_color = TEXT_COLOR_LIGHT_BLACK  # Black's move

        # Display move number
        move_number_surface = font_move_history.render(str(move_number), True, text_color)
        scroll_surface.blit(move_number_surface, (current_x, current_y))

        # Display the move using UCI notation
        move_surface = font_move_history.render(move.uci(), True, text_color)
        scroll_surface.blit(move_surface, (current_x + 50, current_y))

        current_y += spacing_y

def display_message(screen, message):
    # Create a temporary surface for the message
    message_surface = pygame.Surface((400, 50))  # Width and height of the message box
    message_surface.fill((0, 0, 0, 0))  # Transparent fill

    # Render the message
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, (255, 0, 0))  # Red text for visibility

    # Blit the text onto the message surface
    message_surface.blit(text, (10, 10))  # Adjust position within the surface

    # Calculate the position to display the message above the board
    message_rect = message_surface.get_rect(center=(GAME_BOARD_X_OFFSET + 200, GAME_BOARD_Y_OFFSET - 30))

    # Draw the message surface onto the main screen
    screen.blit(message_surface, message_rect)

    # Update only the area where the message is drawn
    pygame.display.update(message_rect)

    # Keep the message visible for a brief period
    pygame.time.delay(2000)  # Show the message for 2 seconds

    # Optionally clear the message area after the delay
    screen.fill((0, 0, 0), message_rect)  # Clear the message area if needed
    pygame.display.update(message_rect)  # Update to clear the area

def handle_piece_drag(event, board, selected_en_passant_option, selected_stalemate_option, 
                      selected_castling_option, selected_promotion_option, captured_white, 
                      captured_black, white_score, black_score, current_piece_theme, scroll_surface, 
                      player_moves, scroll_x, screen, redo_log, current_highlight_option):
    global selected_square, dragging_piece, dragging_piece_image, dragging_piece_position, current_sound_option, is_click_enabled

    # Convert mouse position to board coordinates
    if event.type == pygame.MOUSEBUTTONDOWN and is_click_enabled:
        x, y = event.pos
        col = x // SQUARE_SIZE
        row = (y - GAME_BOARD_Y_OFFSET) // SQUARE_SIZE

        logging.debug(f"Mouse button down at: {event.pos}, col: {col}, row: {row}")

        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if piece and piece.color == board.turn:  # Start dragging the selected piece
                selected_square = square
                dragging_piece = piece
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_type = piece.symbol().lower()

                # Get the image for the piece being dragged
                dragging_piece_image = pygame.image.load(
                    os.path.join(pieces_path, piece_themes[current_piece_theme], f"{piece_color}{piece_type}.png")
                )
                
                # dragging_piece_image = pygame.image.load(f'bottom_up/pieces/{piece_themes[current_piece_theme]}/{piece_color}{piece_type}.png')

                dragging_piece_image = pygame.transform.scale(dragging_piece_image, (SQUARE_SIZE, SQUARE_SIZE))

                # Set initial dragging position
                dragging_piece_position = (x - SQUARE_SIZE // 2, y - SQUARE_SIZE // 2)

                logging.debug(f"Started dragging piece: {piece_color}{piece_type} from square: {selected_square}")

    elif event.type == pygame.MOUSEMOTION and dragging_piece:
        # Update the position of the dragged piece, keeping it centered under the cursor
        x, y = event.pos
        dragging_piece_position = (x - SQUARE_SIZE // 2, y - SQUARE_SIZE // 2)

    elif event.type == pygame.MOUSEBUTTONUP and dragging_piece:
        x, y = event.pos
        col = x // SQUARE_SIZE
        row = (y - GAME_BOARD_Y_OFFSET) // SQUARE_SIZE

        logging.debug(f"Mouse button up at: {event.pos}, col: {col}, row: {row}")

        if 0 <= col < 8 and 0 <= row < 8:
            target_square = chess.square(col, 7 - row)
            move = chess.Move(selected_square, target_square)

            # Handle castling check
            if selected_castling_option == "Off" and board.is_castling(move):
                logging.debug("Castling is disabled.")
                display_message(screen, "Castling is disabled.")  # Show message to player
                reset_drag_variables()
                return white_score, black_score

            # Handle En Passant check
            if selected_en_passant_option == "Off" and board.is_en_passant(move):
                logging.debug("En Passant is disabled.")
                display_message(screen, "En Passant is disabled.")  # Show message to player
                reset_drag_variables()
                return white_score, black_score

            # Check for pawn promotion
            if (board.piece_at(selected_square).piece_type == chess.PAWN and 
                chess.square_rank(target_square) in (0, 7)):  # Promotion condition
                if selected_promotion_option == 'Off':
                    logging.debug("Pawn promotion is disabled.")
                    promoted_piece_type = promotion_menu(screen, 'Off')  # Open menu without queen option
                    move = chess.Move(selected_square, target_square, promotion=promoted_piece_type)
                else:
                    promoted_piece_type = promotion_menu(screen, 'On')  # Open menu with queen option
                    move = chess.Move(selected_square, target_square, promotion=promoted_piece_type)

            if move in board.legal_moves:
                captured_piece = board.piece_at(target_square)  # Check for capture

                if board.is_en_passant(move):  # Handle en passant capture
                    en_passant_square = chess.square(move.to_square % 8, move.from_square // 8)
                    captured_piece = board.piece_at(en_passant_square)
                    board.push(move)
                    logging.debug(f"En Passant capture at {en_passant_square}")

                else:  # Handle regular move
                    board.push(move)


                player_moves.append(move)  # Add the move to the player_moves list
                redo_log.clear()  # Clear redo log after a new move

                # Log captured pieces and scores for undo/redo functionality
                if captured_piece:
                    update_captured_pieces(captured_piece, captured_white, captured_black)
                    white_score, black_score = update_scores(captured_white, captured_black)
                    logging.debug(f"Captured White: {captured_white}, Captured Black: {captured_black}")
                    logging.debug(f"Scores - White: {white_score}, Black: {black_score}")

                # Play sounds based on the move
                if current_sound_option == "On":
                    if captured_piece:  # Play capture sound
                        capture_sound.play()
                        logging.debug(f"Captured piece: {captured_piece} at {target_square}")
                    else:  # Play normal move sound
                        move_sound.play()
                        logging.debug(f"Moved piece from {selected_square} to {target_square}")

                # Draw the canvas and update the move history
                draw_canvas(screen, scroll_surface, scroll_x)
                draw_move_history(scroll_surface, player_moves, scroll_x)

                # Log the move and captured piece for undo/redo
                redo_log.append((move, captured_piece, white_score, black_score))


                 # Handle stalemate check if the option is turned off
                if selected_stalemate_option == "Off" and board.is_stalemate():
                    logging.debug("Stalemate is disabled.")
                    if white_score > black_score:
                        display_message(screen, "White wins by score!")
                    elif black_score > white_score:
                        display_message(screen, "Black wins by score!")
                    else:
                        display_message(screen, "Stalemate by score!")
                    board.pop()  # Undo the move
                    reset_drag_variables()
                    return white_score, black_score
                

                # Check for end game conditions after the move
                if board.is_checkmate():
                    logging.debug("Checkmate detected.")
                    display_message(screen, "Checkmate! Game Over.")
                elif board.is_stalemate():
                    logging.debug("Stalemate detected.")
                    display_message(screen, "Stalemate! Game Over.")
                elif board.is_insufficient_material():
                    logging.debug("Draw by insufficient material.")
                    display_message(screen, "Draw! Insufficient material.")
                elif board.is_seventyfive_moves():
                    logging.debug("Draw by 75-move rule.")
                    display_message(screen, "Draw! 75-move rule.")
                elif board.is_fivefold_repetition():
                    logging.debug("Draw by fivefold repetition.")
                    display_message(screen, "Draw! Fivefold repetition.")
                elif board.is_variant_draw():
                    logging.debug("Draw detected by variant rule.")
                    display_message(screen, "Draw by rule! Game Over.")


        # If highlighting is enabled and a piece is selected, show possible moves
        if current_highlight_option == "On" and selected_square is not None:
            highlight_possible_moves(screen, board, selected_square)

        # Reset drag variables        
        reset_drag_variables()

    return white_score, black_score

def reset_drag_variables():
    global selected_square, dragging_piece, dragging_piece_image, dragging_piece_position, is_click_enabled
    selected_square = None
    dragging_piece = None
    dragging_piece_image = None
    dragging_piece_position = None
    is_click_enabled = True

# Global variable to control click handling || otherwise the click is registerd multiple times
is_click_enabled = True
def handle_piece_movement(event, board, selected_en_passant_option, selected_stalemate_option, 
                           selected_castling_option, selected_promotion_option,
                           captured_white, captured_black, white_score, black_score,scroll_surface,player_moves,scroll_x,screen,redo_log,current_highlight_option):
    global selected_square, is_click_enabled, current_sound_option

    # Convert mouse position to board coordinates
    if event.type == pygame.MOUSEBUTTONDOWN and is_click_enabled:
        x, y = event.pos
        col = x // SQUARE_SIZE
        row = (y - GAME_BOARD_Y_OFFSET) // SQUARE_SIZE

        # Make sure the click is within the board area
        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)

            if selected_square is None:
                # Select the piece at the clicked square
                if board.piece_at(square):
                    selected_square = square
            else:
                # Try to move the selected piece to the clicked square
                move = chess.Move(selected_square, square)

                 # Handle castling check
                if selected_castling_option == "Off" and board.is_castling(move):
                    logging.debug("Castling is disabled.")
                    display_message(screen, "Castling is disabled.")  # Show message to player
                    selected_square = None  # Deselect the piece
                    return white_score, black_score  # Return the current scores

                # Handle En Passant check
                if selected_en_passant_option == "Off" and board.is_en_passant(move):
                    logging.debug("En Passant is disabled.")
                    display_message(screen, "En Passant is disabled.")  # Show message to player
                    selected_square = None  # Deselect the piece
                    return white_score, black_score  # Return the current scores

                # Check if the piece is a pawn and moving to the last rank
                if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(square) in (0, 7):
                    logging.debug(f"Pawn promotion triggered at {square}")
                    
                    # Logic for pawn promotion
                    if selected_promotion_option == 'Off':
                        # Open the promotion menu without the queen option
                        promoted_piece_type = promotion_menu(screen, 'Off')
                    else:
                        # Open the promotion menu with the queen option
                        promoted_piece_type = promotion_menu(screen, 'On')

                    # Create a promotion move with the selected piece type
                    move = chess.Move(selected_square, square, promotion=promoted_piece_type)
                    logging.debug(f"Promoting pawn to {promoted_piece_type} at {square}")
                    


                if move in board.legal_moves:
                    # Check if this is an en passant capture
                    if board.is_en_passant(move):
                        # Get the captured pawn's square
                        en_passant_square = chess.square(move.to_square % 8, move.from_square // 8)
                        captured_piece = board.piece_at(en_passant_square)
                        # Perform the en passant move
                        board.push(move)
                    else:
                        # Handle regular move
                        captured_piece = board.piece_at(move.to_square)
                        board.push(move)



                    redo_log.clear()  # Clear redo log after a new move
                    player_moves.append(move)

                    draw_canvas(screen, scroll_surface, scroll_x)
                    draw_move_history(scroll_surface, player_moves, scroll_x)

                    # Update captured pieces and scores
                    if captured_piece:
                        update_captured_pieces(captured_piece, captured_white, captured_black)
                        white_score, black_score = update_scores(captured_white, captured_black)
                        # Log the move and the captured piece for undo/redo
                        redo_log.append((move, captured_piece, white_score, black_score))


                    # Play sounds based on the move
                    if current_sound_option == "On":
                        if captured_piece:  # If there's a captured piece, play capture sound
                            capture_sound.play()  # Replace with your capture sound
                        else:  # If it's just a normal move
                            move_sound.play()  # Play sound when a piece is moved

                    # Handle stalemate check if the option is turned off
                    if selected_stalemate_option == "Off" and board.is_stalemate():
                        logging.debug("Stalemate is disabled.")
                        # Check scores to determine winner
                        if white_score > black_score:
                            display_message(screen, "White wins by score!")
                        elif black_score > white_score:
                            display_message(screen, "Black wins by score!")
                        else:
                            display_message(screen, "Stalemate by score!")
                        board.pop()  # Undo the move
                        selected_square = None
                        return white_score, black_score  # Return the current scores

                    # Check for game-ending conditions
                    if board.is_checkmate():
                        logging.debug("Checkmate detected.")
                        display_message(screen, "Checkmate! Game Over.")
                    elif board.is_stalemate():
                        logging.debug("Stalemate detected.")
                        display_message(screen, "Stalemate! Game Over.")
                    elif board.is_insufficient_material():
                        logging.debug("Draw by insufficient material.")
                        display_message(screen, "Draw! Insufficient material.")
                    elif board.is_seventyfive_moves():
                        logging.debug("Draw by 75-move rule.")
                        display_message(screen, "Draw! 75-move rule.")
                    elif board.is_fivefold_repetition():
                        logging.debug("Draw by fivefold repetition.")
                        display_message(screen, "Draw! Fivefold repetition.")
                    elif board.is_variant_draw():
                        logging.debug("Draw detected by variant rule.")
                        display_message(screen, "Draw by rule! Game Over.")

                selected_square = None  # Deselect the piece after the move

        # Disable further clicks until the action is processed
        is_click_enabled = False

    # Re-enable clicks after processing the current event
    if event.type == pygame.MOUSEBUTTONUP:
        is_click_enabled = True
    
    # If highlighting is enabled and a piece is selected, show possible moves
    if current_highlight_option == "On" and selected_square is not None:
        highlight_possible_moves(screen, board, selected_square)


    return white_score, black_score

def undo_move(board, player_moves, captured_white, captured_black, redo_log, white_score, black_score):
    if not player_moves:
        logging.debug("No moves to undo.")
        return board, white_score, black_score, captured_white, captured_black  # No moves to undo

    last_move = player_moves.pop()

    if last_move not in board.move_stack:
        logging.warning("Attempting to undo a non-existent move.")
        return board, white_score, black_score, captured_white, captured_black  # Invalid move, exit early

    board.pop()  # Undo last move on the board

    # Check for en passant
    if board.is_en_passant(last_move):
        en_passant_target_square = last_move.to_square
        en_passant_captured_square = chess.square(last_move.from_square % 8, last_move.to_square // 8)
        
        # Restore the captured piece for en passant (the pawn)
        captured_piece = board.piece_at(en_passant_captured_square)
        if captured_piece:
            piece_symbol = captured_piece.symbol().lower()
            if captured_piece.color == chess.WHITE:
                if piece_symbol in captured_black:
                    captured_black.remove(piece_symbol)  # Remove from captured list
                    black_score -= piece_values.get(piece_symbol, 0)  # Adjust score
                    logging.debug(f"Restored white captured piece (en passant): {piece_symbol}")
                else:
                    logging.warning(f"Piece {piece_symbol} not found in captured_black.")
            else:
                if piece_symbol in captured_white:
                    captured_white.remove(piece_symbol)  # Remove from captured list
                    white_score -= piece_values.get(piece_symbol, 0)  # Adjust score
                    logging.debug(f"Restored black captured piece (en passant): {piece_symbol}")
                else:
                    logging.warning(f"Piece {piece_symbol} not found in captured_white.")

        # Now restore the en passant captured piece to the board
        board.set_piece_at(en_passant_captured_square, captured_piece)

    else:
        # Normal move capture handling
        captured_piece = board.piece_at(last_move.to_square)

        if captured_piece:
            piece_symbol = captured_piece.symbol().lower()

            if captured_piece.color == chess.WHITE:
                if piece_symbol in captured_black:
                    captured_black.remove(piece_symbol)  # Remove from captured list
                    black_score -= piece_values.get(piece_symbol, 0)  # Adjust score
                    logging.debug(f"Restored black captured piece: {piece_symbol}")
                else:
                    logging.warning(f"Piece {piece_symbol} not found in captured_black.")
            else:
                if piece_symbol in captured_white:
                    captured_white.remove(piece_symbol)  # Remove from captured list
                    white_score -= piece_values.get(piece_symbol, 0)  # Adjust score
                    logging.debug(f"Restored white captured piece: {piece_symbol}")
                else:
                    logging.warning(f"Piece {piece_symbol} not found in captured_white.")

    # Log the undo for redo functionality
    redo_log.append((last_move, captured_piece, white_score, black_score))
    logging.debug(f"Undo move logged: {last_move}")

    return board, white_score, black_score, captured_white, captured_black


def redo_moves(board, redo_log, player_moves, captured_white, captured_black, white_score, black_score):
    if not redo_log:
        logging.debug("No moves to redo.")
        return board, white_score, black_score, captured_white, captured_black

    next_move, captured_piece, prev_white_score, prev_black_score = redo_log.pop()

    if next_move not in board.legal_moves:
        logging.warning(f"Attempting to redo an illegal move: {next_move}")
        return board, white_score, black_score, captured_white, captured_black  # Invalid move, exit early

    board.push(next_move)  # Redo the move
    logging.debug(f"Redone move: {next_move}")

    player_moves.append(next_move)

    # Check if the move was an en passant
    if board.is_en_passant(next_move):
        en_passant_target_square = next_move.to_square
        en_passant_captured_square = chess.square(next_move.from_square % 8, next_move.to_square // 8)

        # Re-add the captured piece for en passant (the pawn)
        captured_piece = board.piece_at(en_passant_captured_square)
        if captured_piece:
            piece_symbol = captured_piece.symbol().lower()
            if captured_piece.color == chess.WHITE:
                captured_black.append(piece_symbol)  # Re-add to captured list
                black_score += piece_values.get(piece_symbol, 0)  # Adjust score
                logging.debug(f"Re-added white captured piece (en passant): {piece_symbol}")
            else:
                captured_white.append(piece_symbol)  # Re-add to captured list
                white_score += piece_values.get(piece_symbol, 0)  # Adjust score
                logging.debug(f"Re-added black captured piece (en passant): {piece_symbol}")

    else:
        # Normal move capture handling
        if captured_piece:
            piece_symbol = captured_piece.symbol().lower()

            if captured_piece.color == chess.WHITE:
                captured_black.append(piece_symbol)  # Re-add to captured list
                black_score += piece_values.get(piece_symbol, 0)  # Adjust score
                logging.debug(f"Re-added black's captured piece: {piece_symbol}")
            else:
                captured_white.append(piece_symbol)  # Re-add to captured list
                white_score += piece_values.get(piece_symbol, 0)  # Adjust score
                logging.debug(f"Re-added white's captured piece: {piece_symbol}")

    return board, white_score, black_score, captured_white, captured_black


#region highlight first implementation
# def highlight_possible_moves(screen, board, selected_square):
#     if selected_square is None:
#         return

#     # Get all legal moves for the selected piece
#     legal_moves = [move for move in board.legal_moves if move.from_square == selected_square]

#     # Highlight each legal move by coloring the target square
#     for move in legal_moves:
#         target_square = move.to_square
#         target_col = chess.square_file(target_square)  # x position
#         target_row = 7 - chess.square_rank(target_square)  # y position (reverse for screen)

#         # Set a color for highlighting (e.g., light blue with transparency)
#         highlight_color = HIGHLIGHT_COLOR  
#         border_color = BORDER_COLOR

#         # # Draw the rectangle highlight
#         # pygame.draw.rect(screen, highlight_color, (target_col * SQUARE_SIZE, 
#         #                                            target_row * SQUARE_SIZE + GAME_BOARD_Y_OFFSET, 
#         #                                            SQUARE_SIZE, SQUARE_SIZE), 0)
        
#         '''Transparency values of a color RGBA do not work with pygame.draw, so we need to use blint'''
#         # Create a transparent surface to draw the highlight
#         highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

#         # Calculate the center of the circle
#         center_x = SQUARE_SIZE // 2
#         center_y = SQUARE_SIZE // 2

#         # Draw the circular border first on the transparent surface
#         pygame.draw.circle(highlight_surface, border_color, (center_x, center_y), SQUARE_SIZE // 5 + 2)

#         # Draw the circular highlight (with transparency)
#         pygame.draw.circle(highlight_surface, highlight_color, (center_x, center_y), SQUARE_SIZE // 5)

#         # Blit the transparent highlight surface onto the main screen
#         screen.blit(highlight_surface, (target_col * SQUARE_SIZE, target_row * SQUARE_SIZE + GAME_BOARD_Y_OFFSET))
#endregion

# At the top of your file or within your game state management
last_move_start = None
last_move_end = None

def highlight_possible_moves(screen, board, selected_square):
    if selected_square is None:
        return

    # Get all legal moves for the selected piece
    legal_moves = [move for move in board.legal_moves if move.from_square == selected_square]

    # Highlight the last move if it exists
    if last_move_start is not None and last_move_end is not None:
        highlight_square(screen, last_move_start, OPPONENT_HIGHLIGHT_COLOR)  # Highlight the start square of the last move
        highlight_square(screen, last_move_end, OPPONENT_HIGHLIGHT_COLOR)    # Highlight the end square of the last move

    # Highlight each legal move by coloring the target square
    for move in legal_moves:
        highlight_square(screen, move.to_square, PLAYER_HIGHLIGHT_COLOR)  # Highlight player moves

def highlight_square(screen, square, color):
    target_col = chess.square_file(square)  # x position
    target_row = 7 - chess.square_rank(square)  # y position (reverse for screen)

    # Create a transparent surface to draw the highlight
    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

    center_x = SQUARE_SIZE // 2
    center_y = SQUARE_SIZE // 2

    # Draw the circular border first on the transparent surface
    pygame.draw.circle(highlight_surface, BORDER_COLOR, (center_x, center_y), SQUARE_SIZE // 5 + 2)

    # Draw the circular highlight (with transparency)
    pygame.draw.circle(highlight_surface, color, (center_x, center_y), SQUARE_SIZE // 5)

    # Blit the transparent highlight surface onto the main screen
    screen.blit(highlight_surface, (target_col * SQUARE_SIZE, target_row * SQUARE_SIZE + GAME_BOARD_Y_OFFSET))

def update_last_move(start_square, end_square):
    global last_move_start, last_move_end
    last_move_start = start_square
    last_move_end = end_square

#A LITTEL NICE FEATURE HERE ACTUALLY SINGLE MOVE REDO || AND YOU CAN CHOOSE THE BOTS MOVES
def handle_piece_drag_bot(event, board, selected_en_passant_option, selected_stalemate_option, 
                           selected_castling_option, selected_promotion_option, captured_white, 
                           captured_black, white_score, black_score, current_piece_theme, 
                           scroll_surface, player_moves, scroll_x, screen, redo_log, 
                           current_highlight_option,time_limit, bot_enabled):
    global selected_square, dragging_piece, dragging_piece_image, dragging_piece_position, current_sound_option, is_click_enabled

    # Convert mouse position to board coordinates
    if event.type == pygame.MOUSEBUTTONDOWN and is_click_enabled:
        x, y = event.pos
        col = x // SQUARE_SIZE
        row = (y - GAME_BOARD_Y_OFFSET) // SQUARE_SIZE

        logging.debug(f"Mouse button down at: {event.pos}, col: {col}, row: {row}")

        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)

            # Human player's turn
            if piece and piece.color == board.turn:  # Start dragging the selected piece
                selected_square = square
                dragging_piece = piece
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_type = piece.symbol().lower()


                # Load the dragging piece image dynamically
                dragging_piece_image = pygame.image.load(
                    os.path.join(pieces_path, piece_themes[current_piece_theme], f"{piece_color}{piece_type}.png")
                )

                # # Get the image for the piece being dragged
                # dragging_piece_image = pygame.image.load(
                #     f'bottom_up/pieces/{piece_themes[current_piece_theme]}/{piece_color}{piece_type}.png'
                # )
                dragging_piece_image = pygame.transform.scale(dragging_piece_image, (SQUARE_SIZE, SQUARE_SIZE))

                # Set initial dragging position
                dragging_piece_position = (x - SQUARE_SIZE // 2, y - SQUARE_SIZE // 2)

                logging.debug(f"Started dragging piece: {piece_color}{piece_type} from square: {selected_square}")

    elif event.type == pygame.MOUSEMOTION and dragging_piece:
        # Update the position of the dragged piece, keeping it centered under the cursor
        x, y = event.pos
        dragging_piece_position = (x - SQUARE_SIZE // 2, y - SQUARE_SIZE // 2)

    elif event.type == pygame.MOUSEBUTTONUP and dragging_piece:
        x, y = event.pos
        col = x // SQUARE_SIZE
        row = (y - GAME_BOARD_Y_OFFSET) // SQUARE_SIZE

        logging.debug(f"Mouse button up at: {event.pos}, col: {col}, row: {row}")

        if 0 <= col < 8 and 0 <= row < 8:
            target_square = chess.square(col, 7 - row)
            move = chess.Move(selected_square, target_square)

            # Handle castling check
            if selected_castling_option == "Off" and board.is_castling(move):
                logging.debug("Castling is disabled.")
                display_message(screen, "Castling is disabled.")  # Show message to player
                reset_drag_variables()
                return white_score, black_score

            # Handle En Passant check
            if selected_en_passant_option == "Off" and board.is_en_passant(move):
                logging.debug("En Passant is disabled.")
                display_message(screen, "En Passant is disabled.")  # Show message to player
                reset_drag_variables()
                return white_score, black_score

            # Check for pawn promotion
            if (board.piece_at(selected_square).piece_type == chess.PAWN and 
                chess.square_rank(target_square) in (0, 7)):  # Promotion condition
                if selected_promotion_option == 'Off':
                    promoted_piece_type = promotion_menu(screen, 'Off')  # Open menu without queen option
                    move = chess.Move(selected_square, target_square, promotion=promoted_piece_type)
                else:
                    promoted_piece_type = promotion_menu(screen, 'On')  # Open menu with queen option
                    move = chess.Move(selected_square, target_square, promotion=promoted_piece_type)

            if move in board.legal_moves:
                captured_piece = board.piece_at(target_square)  # Check for capture
                board.push(move)
                player_moves.append(move)  # Add the move to the player_moves list
                redo_log.clear()  # Clear redo log after a new move

                # Log captured pieces and scores for undo/redo functionality
                if captured_piece:
                    update_captured_pieces(captured_piece, captured_white, captured_black)
                    white_score, black_score = update_scores(captured_white, captured_black)
                    logging.debug(f"Captured White: {captured_white}, Captured Black: {captured_black}")
                    logging.debug(f"Scores - White: {white_score}, Black: {black_score}")

                # Play sounds based on the move
                if current_sound_option == "On":
                    if captured_piece:  # Play capture sound
                        capture_sound.play()
                        logging.debug(f"Captured piece: {captured_piece} at {target_square}")
                    else:  # Play normal move sound
                        move_sound.play()
                        logging.debug(f"Moved piece from {selected_square} to {target_square}")

                # Draw the canvas and update the move history
                draw_canvas(screen, scroll_surface, scroll_x)
                draw_move_history(scroll_surface, player_moves, scroll_x)

                # Log the move and captured piece for undo/redo
                redo_log.append((move, captured_piece, white_score, black_score))

            # Update the last move with the bot's move
            update_last_move(move.from_square, move.to_square)

            # If highlighting is enabled and a piece is selected, show possible moves
            if current_highlight_option == "On" and selected_square is not None:
                highlight_possible_moves(screen, board, selected_square)

            # Reset drag variables
            reset_drag_variables()

        # Bot's turn handling (drag logic)
        if bot_enabled and board.turn == chess.BLACK:
            # Add a slight delay before bot moves
            #pygame.time.wait(BOT_MOVE_DELAY)  # Wait for 0.5 seconds

            legal_moves = list(board.legal_moves)
            if legal_moves:
                #move = random.choice(legal_moves)  # Let bot choose a random move

                # Use the Stockfish engine to get the best move
                move = make_bot_move(board, time_limit)  # Set your desired time limit here

                # Handle castling check
                if selected_castling_option == "Off" and board.is_castling(move):
                    logging.debug("Castling is disabled.")
                    display_message(screen, "Castling is disabled.")
                    return white_score, black_score

                # Handle En Passant check
                if selected_en_passant_option == "Off" and board.is_en_passant(move):
                    logging.debug("En Passant is disabled.")
                    display_message(screen, "En Passant is disabled.")
                    return white_score, black_score

                # Check for pawn promotion
                if (board.piece_at(move.from_square).piece_type == chess.PAWN and 
                    chess.square_rank(move.to_square) in (0, 7)):
                    promoted_piece_type = promotion_menu(screen, 'On')
                    move = chess.Move(move.from_square, move.to_square, promotion=promoted_piece_type)

                # Update captured pieces and scores
                captured_piece = board.piece_at(move.to_square)
                # Make the bot's move
                board.push(move)
                player_moves.append(move)

                if captured_piece:
                    update_captured_pieces(captured_piece, captured_white, captured_black)
                    white_score, black_score = update_scores(captured_white, captured_black)

                # Log the move for undo/redo
                redo_log.append((move, captured_piece, white_score, black_score))

                # Play sounds based on the move
                if current_sound_option == "On":
                    if captured_piece:
                        capture_sound.play()
                    else:
                        move_sound.play()

                # Draw updates to the canvas and move history
                draw_canvas(screen, scroll_surface, scroll_x)
                draw_move_history(scroll_surface, player_moves, scroll_x)

                # Update the last move with the bot's move
                update_last_move(move.from_square, move.to_square)
                
                # If highlighting is enabled and a piece is selected, show possible moves
                if current_highlight_option == "On" and selected_square is not None:
                    highlight_possible_moves(screen, board, selected_square)

                logging.debug(f"Bot moved piece: {move}")

    return white_score, black_score

# Global flag to manage turns
is_bot_turn = False
def handle_piece_movement_bot(event, board, selected_en_passant_option, selected_stalemate_option,
                               selected_castling_option, selected_promotion_option,
                               captured_white, captured_black, white_score, black_score,
                               scroll_surface, player_moves, scroll_x, screen, redo_log, current_highlight_option,time_limit):
    global selected_square, is_click_enabled, current_sound_option, is_bot_turn

    # Convert mouse position to board coordinates
    if event.type == pygame.MOUSEBUTTONDOWN and is_click_enabled:
        x, y = event.pos
        col = x // SQUARE_SIZE
        row = (y - GAME_BOARD_Y_OFFSET) // SQUARE_SIZE

        # Make sure the click is within the board area
        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)

            if selected_square is None:
                # Handle White's human move
                if board.piece_at(square):
                    selected_square = square
            else:
                # Try to move the selected piece to the clicked square
                move = chess.Move(selected_square, square)

                # Handle castling check
                if selected_castling_option == "Off" and board.is_castling(move):
                    logging.debug("Castling is disabled.")
                    display_message(screen, "Castling is disabled.")
                    selected_square = None
                    return white_score, black_score

                # Handle En Passant check
                if selected_en_passant_option == "Off" and board.is_en_passant(move):
                    logging.debug("En Passant is disabled.")
                    display_message(screen, "En Passant is disabled.")
                    selected_square = None
                    return white_score, black_score

                # Check for pawn promotion
                if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(square) in (0, 7):
                    logging.debug(f"Pawn promotion triggered at {square}")

                    # Logic for pawn promotion
                    if selected_promotion_option == 'Off':
                        promoted_piece_type = promotion_menu(screen, 'Off')
                    else:
                        promoted_piece_type = promotion_menu(screen, 'On')

                    move = chess.Move(selected_square, square, promotion=promoted_piece_type)
                    logging.debug(f"Promoting pawn to {promoted_piece_type} at {square}")

                # Check if the move is legal
                if move in board.legal_moves:
                    captured_piece = board.piece_at(square)
                    board.push(move)
                    redo_log.clear()  # Clear redo log after a new move
                    player_moves.append(move)

                    draw_canvas(screen, scroll_surface, scroll_x)
                    draw_move_history(scroll_surface, player_moves, scroll_x)

                    # Update captured pieces and scores
                    if captured_piece:
                        update_captured_pieces(captured_piece, captured_white, captured_black)
                        white_score, black_score = update_scores(captured_white, captured_black)
                        redo_log.append((move, captured_piece, white_score, black_score))

                    # Play sounds based on the move
                    if current_sound_option == "On":
                        if captured_piece:
                            capture_sound.play()
                        else:
                            move_sound.play()

                    # Handle stalemate check if the option is turned off
                    if selected_stalemate_option == "Off" and board.is_stalemate():
                        logging.debug("Stalemate is disabled, game continues.")
                        display_message(screen, "Stalemate is disabled.")
                        board.pop()  # Undo the move
                        selected_square = None
                        return white_score, black_score
                    
                    # Update the last move with the player's move
                    update_last_move(selected_square, square)

                selected_square = None  # Deselect the piece after the move

        # After the player's turn, set the flag indicating it's now the bot's turn
        is_bot_turn = board.turn == chess.BLACK

    # Bot's turn handling (if it's black's turn)
    if is_bot_turn and board.turn == chess.BLACK and is_click_enabled:
        legal_moves = list(board.legal_moves)
        if legal_moves:
            #move = random.choice(legal_moves)

            # Use the Stockfish engine to get the best move
            move = make_bot_move(board, time_limit)  # Set your desired time limit here

            # Handle castling check
            if selected_castling_option == "Off" and board.is_castling(move):
                logging.debug("Castling is disabled.")
                display_message(screen, "Castling is disabled.")
                return white_score, black_score  # Return current scores

            # Handle En Passant check
            if selected_en_passant_option == "Off" and board.is_en_passant(move):
                logging.debug("En Passant is disabled.")
                display_message(screen, "En Passant is disabled.")
                return white_score, black_score  # Return current scores

            # Check for pawn promotion
            if board.piece_at(move.from_square).piece_type == chess.PAWN and chess.square_rank(move.to_square) in (0, 7):
                logging.debug(f"Pawn promotion triggered at {move.to_square}")
                if selected_promotion_option == 'Off':
                    promoted_piece_type = promotion_menu(screen, 'Off')
                else:
                    promoted_piece_type = promotion_menu(screen, 'On')

                move = chess.Move(move.from_square, move.to_square, promotion=promoted_piece_type)
                logging.debug(f"Promoting pawn to {promoted_piece_type} at {move.to_square}")

            # Update captured pieces and scores
            captured_piece = board.piece_at(move.to_square)

            # Make the move
            board.push(move)
            player_moves.append(move)

            if captured_piece:
                update_captured_pieces(captured_piece, captured_white, captured_black)
                white_score, black_score = update_scores(captured_white, captured_black)

            # Log the move for undo/redo functionality
            redo_log.append((move, captured_piece, white_score, black_score))

            # Play sounds based on the move
            if current_sound_option == "On":
                if captured_piece:
                    capture_sound.play()
                else:
                    move_sound.play()

            # Handle stalemate
            if selected_stalemate_option == "Off" and board.is_stalemate():
                logging.debug("Stalemate is disabled, game continues.")
                display_message(screen, "Stalemate is disabled.")
                board.pop()  # Undo the move if stalemate is not allowed

            # Draw updates to the canvas and move history
            draw_canvas(screen, scroll_surface, scroll_x)
            draw_move_history(scroll_surface, player_moves, scroll_x)

            # Update the last move with the bot's move
            update_last_move(move.from_square, move.to_square)

            # If highlighting is enabled, show possible moves for the bot's last move
            if current_highlight_option == "On":
                highlight_possible_moves(screen, board, move.from_square)

            # Disable further clicks until the action is processed
            is_click_enabled = False

    # Re-enable clicks after processing the current event
    if event.type == pygame.MOUSEBUTTONUP:
        is_click_enabled = True

    # If highlighting is enabled and a piece is selected, show possible moves
    if current_highlight_option == "On" and selected_square is not None:
        highlight_possible_moves(screen, board, selected_square)

    return white_score, black_score

def make_bot_move(board, time_limit):
    
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    try:
        result = engine.play(board, chess.engine.Limit(time=time_limit))
        return result.move
    except Exception as e:
        logging.error(f"Error getting move from Stockfish: {e}")
        return None  # Handle case when no move is returned
    finally:
        engine.quit()

def undo_bots(board, player_moves, captured_white, captured_black, redo_log, white_score, black_score):
    global is_bot_turn  # Ensure to access the global turn flag

    if not player_moves:
        logging.debug("No moves to undo for bots.")
        return board, white_score, black_score, captured_white, captured_black, chess.WHITE  # No moves to undo

    # Undo the bot's last move
    last_move = player_moves.pop()  # Undo the bot's last move

    if last_move not in board.move_stack:
        logging.warning("Attempting to undo a non-existent move.")
        return board, white_score, black_score, captured_white, captured_black, chess.WHITE  # Invalid move, exit early

    board.pop()  # Undo the last move on the board

    # Retrieve the piece that was on the destination square before the move
    captured_piece = board.piece_at(last_move.to_square)

    # If a piece was captured, restore it safely
    if captured_piece:
        piece_symbol = captured_piece.symbol().lower()

        if captured_piece.color == chess.WHITE:
            if piece_symbol in captured_black:
                captured_black.remove(piece_symbol)  # Remove from captured list
                black_score -= piece_values[piece_symbol]  # Adjust score
                logging.debug(f"Restored black captured piece: {piece_symbol}")
            else:
                logging.warning(f"Piece {piece_symbol} not found in captured_black.")
        else:
            if piece_symbol in captured_white:
                captured_white.remove(piece_symbol)  # Remove from captured list
                white_score -= piece_values[piece_symbol]  # Adjust score
                logging.debug(f"Restored white captured piece: {piece_symbol}")
            else:
                logging.warning(f"Piece {piece_symbol} not found in captured_white.")

    # Log the undo for redo functionality
    redo_log.append((last_move, captured_piece, white_score, black_score))
    logging.debug(f"Undo bot move logged: {last_move}")

    # Now, check if there is a player move to undo
    if player_moves:  # Ensure there are player moves to undo
        last_player_move = player_moves.pop()  # Undo the player's last move

        if last_player_move in board.move_stack:
            board.pop()  # Undo the last player's move on the board
            
            # Handle captured piece restoration for the player's move
            captured_piece = board.piece_at(last_player_move.to_square)
            if captured_piece:
                piece_symbol = captured_piece.symbol().lower()
                if captured_piece.color == chess.WHITE:
                    if piece_symbol in captured_black:
                        captured_black.remove(piece_symbol)
                        black_score -= piece_values[piece_symbol]
                else:
                    if piece_symbol in captured_white:
                        captured_white.remove(piece_symbol)
                        white_score -= piece_values[piece_symbol]

            # Log the player's undo for redo functionality
            redo_log.append((last_player_move, captured_piece, white_score, black_score))
            logging.debug(f"Undo player move logged: {last_player_move}")

    # Switch the turn back to the player after undoing the bot's and player's moves
    is_bot_turn = False  # It's now the player's turn
    current_turn = chess.WHITE  # Set current turn to WHITE (the player's turn)

    return board, white_score, black_score, captured_white, captured_black, current_turn

def redo_bots(board, redo_log, player_moves, captured_white, captured_black, white_score, black_score):
    if not redo_log:
        logging.debug("No moves to redo for bots.")
        return board, white_score, black_score, captured_white, captured_black

    # Retrieve the next move from the redo log
    next_move, captured_piece, prev_white_score, prev_black_score = redo_log.pop()

    # Ensure the move is still legal before applying it
    if next_move not in board.legal_moves:
        logging.warning(f"Attempting to redo an illegal move: {next_move}")
        return board, white_score, black_score, captured_white, captured_black  # Invalid move, exit early

    # Push the move onto the board
    board.push(next_move)
    logging.debug(f"Redone bot move: {next_move}")

    # Add the move to the player's move history
    player_moves.append(next_move)

    # Handle captured pieces during redo
    if captured_piece:
        piece_symbol = captured_piece.symbol().lower()

        if captured_piece.color == chess.WHITE:
            captured_black.append(piece_symbol)  # Re-add to black's captured list
            black_score += piece_values[piece_symbol]  # Adjust score
            logging.debug(f"Re-added black's captured piece: {piece_symbol}")
        elif captured_piece.color == chess.BLACK:
            captured_white.append(piece_symbol)  # Re-add to white's captured list
            white_score += piece_values[piece_symbol]  # Adjust score
            logging.debug(f"Re-added white's captured piece: {piece_symbol}")

    # Update scores to reflect the previous state
    logging.debug(f"Scores after redo: White: {white_score}, Black: {black_score}")

    # After redoing a move, ensure the turn switches back to the player
    # Set the bot turn flag to False to prevent the bot from moving after the redo
    is_bot_turn = False

    return board, white_score, black_score, captured_white, captured_black


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def handle_movement_online(event, board, selected_en_passant_option, selected_stalemate_option, 
                           selected_castling_option, selected_promotion_option,
                           captured_white, captured_black, white_score, black_score,
                           scroll_surface, player_moves, scroll_x, screen, redo_log, 
                           current_highlight_option, conn, is_white):

    global selected_square, is_click_enabled, current_sound_option

    if event.type == pygame.MOUSEBUTTONDOWN and is_click_enabled:
        x, y = event.pos
        col = x // SQUARE_SIZE
        row = (y - GAME_BOARD_Y_OFFSET) // SQUARE_SIZE

        # Make sure the click is within the board area
        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)
            print(f"Selected Square: {selected_square}, Target Square: {square}")  # Debugging info

            piece_at_square = board.piece_at(square)

            if selected_square is None:
                # Select the piece at the clicked square if it's the player's piece
                if piece_at_square and piece_at_square.color == is_white:
                    selected_square = square
                    print(f"Piece selected at {square}")  # Debugging info

            else:
                # Handle the case of selecting a new piece
                if square == selected_square:
                    # Deselect the piece if the same square is clicked
                    selected_square = None
                    print("Piece deselected")  # Debugging info
                elif piece_at_square and piece_at_square.color == is_white:
                    # If the clicked square contains the player's piece, switch selection
                    selected_square = square
                    print(f"Piece switched to {square}")  # Debugging info
                else:
                    # Attempt to create a move
                    move = chess.Move(selected_square, square)
                    print(f"Move being created: {move}")  # Debugging move creation

                    # Ensure the move is within valid bounds
                    if move in board.legal_moves:
                        # Check for a piece at the target square before moving
                        captured_piece = board.piece_at(square)
                        print(f"Piece at target square before move: {captured_piece}")  # Debugging info
                        
                        # Push the move to the board
                        board.push(move)
                        player_moves.append(move)

                        # Log the captured piece (if any) for updating scores and captured lists
                        #if captured_piece:
                        print(f"Captured piece: {captured_piece}")  # Debugging capture info
                        update_captured_pieces(captured_piece, captured_white, captured_black)
                        white_score, black_score = update_scores(captured_white, captured_black)

                        # Draw and update the game state
                        draw_canvas(screen, scroll_surface, scroll_x)
                        draw_move_history(scroll_surface, player_moves, scroll_x)

                        # Send the move to the server
                        move_data = f"{move.from_square},{move.to_square}"
                        conn.send(move_data.encode())

                        # Play sounds based on the move
                        if current_sound_option == "On":
                            if captured_piece:
                                capture_sound.play()  # Play capture sound
                            else:
                                move_sound.play()  # Play sound for normal move

                        # Handle specific rules and promotion
                        check_rules_and_promotion(board, move, selected_en_passant_option, 
                                                  selected_stalemate_option, selected_castling_option, 
                                                  selected_promotion_option, screen)

                        selected_square = None  # Deselect the piece after the move
                    else:
                        print("Invalid move or out-of-bound square selected.")
                        selected_square = None  # Reset selection on invalid move

        is_click_enabled = False

    if event.type == pygame.MOUSEBUTTONUP:
        is_click_enabled = True

    # Highlight possible moves if necessary
    if current_highlight_option == "On" and selected_square is not None:
        highlight_possible_moves(screen, board, selected_square)

    return white_score, black_score

def receive_moves(conn, board, screen, scroll_surface, scroll_x, player_moves,
                  captured_white, captured_black, white_score, black_score,
                  selected_en_passant_option, selected_stalemate_option, 
                  selected_castling_option, selected_promotion_option):
    while True:
        move_data = conn.recv(1024).decode()
        if move_data:
            from_square, to_square = map(int, move_data.split(","))
            move = chess.Move(from_square, to_square)

            # Check if the piece at the from_square exists before moving
            piece_at_from_square = board.piece_at(from_square)
            if piece_at_from_square is None:
                print(f"No piece at {from_square}. Cannot proceed with move.")
                continue  # Skip this iteration

            # Check for a piece at the target square before moving
            captured_piece = board.piece_at(move.to_square)
            print(f"Captured piece before move: {captured_piece}")  # Debugging info

            # Push the move to the board
            board.push(move)
            player_moves.append(move)

            # Handle captured pieces and update scores
            #if captured_piece:
            update_captured_pieces(captured_piece, captured_white, captured_black)
            white_score, black_score = update_scores(captured_white, captured_black)

            # Handle specific rules and promotion
            check_rules_and_promotion(board, move, selected_en_passant_option, 
                                      selected_stalemate_option, selected_castling_option, 
                                      selected_promotion_option, screen)

            # Draw and update the game state
            draw_canvas(screen, scroll_surface, scroll_x)
            draw_move_history(scroll_surface, player_moves, scroll_x)

            # If highlighting is enabled, show possible moves for the last move
            if current_highlight_option == "On":
                highlight_possible_moves(screen, board, move.from_square)

def check_rules_and_promotion(board, move, selected_en_passant_option, selected_stalemate_option, 
                              selected_castling_option, selected_promotion_option, screen):
    # Handle specific rules
    if selected_stalemate_option == "Off" and board.is_stalemate():
        logging.debug("Stalemate is disabled, game continues.")
        display_message(screen, "Stalemate is disabled.")
        board.pop()  # Undo the move if stalemate is not allowed
    elif selected_castling_option == "Off" and board.is_castling(move):
        logging.debug("Castling is disabled, undoing the move.")
        display_message(screen, "Castling is disabled.")
        board.pop()  # Undo the move if castling is disabled
    elif selected_en_passant_option == "Off" and board.is_en_passant(move):
        logging.debug("En Passant is disabled, undoing the move.")
        display_message(screen, "En Passant is disabled.")
        board.pop()  # Undo the move if en passant is disabled

    # Handle pawn promotion (check if it's a pawn moving to the last rank)
    piece_at_from_square = board.piece_at(move.from_square)
    if piece_at_from_square and piece_at_from_square.piece_type == chess.PAWN and chess.square_rank(move.to_square) in [0, 7]:
        logging.debug("Pawn is promoting.")
        if selected_promotion_option == "Auto Queen":
            move.promotion = chess.QUEEN

def listen_for_moves(client_socket, board, player_moves, captured_white, captured_black,
                     white_score, black_score, selected_en_passant_option, 
                     selected_stalemate_option, selected_castling_option, 
                     selected_promotion_option, scroll_surface, scroll_x, screen, 
                     current_highlight_option, player_names):  # Add player names as parameters
    
    while True:
        try:
            # Wait for data from the other player
            data = client_socket.recv(1024).decode()  # Adjust buffer size if needed
            if data:
                print(f"Received data: {data}")  # Debug log

                # Check if the data is a player name notification
                if data.startswith("white_name:") or data.startswith("black_name:"):
                    # Extract and handle player names
                    player_name = data.split(":", 1)[1]  # Get the name after "white_name:" or "black_name:"
                    print(f"Received player name: {player_name}")  # Debug log

                    # Update names based on the received data
                    if data.startswith("white_name:"):
                        white_name = player_name
                    else:  # This means it starts with "black_name:"
                        black_name = player_name

                    # Update names based on the received data
                    if data.startswith("white_name:"):
                        player_names['white'] = player_name  # Update the dictionary
                    else:
                        player_names['black'] = player_name
                    
                    continue  # Skip the rest of the loop and wait for the next data

                # Ensure data is in the correct format for moves
                if "," in data:  # Check if the data contains a comma, indicating a move
                    try:
                        from_square, to_square = map(int, data.split(","))
                        move = chess.Move(from_square, to_square)

                        # Check if the piece at the from_square exists before moving
                        piece_at_from_square = board.piece_at(from_square)
                        if piece_at_from_square is None:
                            print(f"No piece at {from_square}. Cannot proceed with move.")
                            continue  # Skip this iteration
                        
                        # Check for a piece at the target square before moving
                        captured_piece = board.piece_at(move.to_square)
                        print(f"Captured piece before move: {captured_piece}")  # Debugging info

                        # Update the board with the received move
                        board.push(move)
                        player_moves.append(move)

                        # Handle captured pieces and update scores
                        #if captured_piece:
                        update_captured_pieces(captured_piece, captured_white, captured_black)
                        white_score, black_score = update_scores(captured_white, captured_black)

                        # Handle specific rules and promotion
                        check_rules_and_promotion(board, move, selected_en_passant_option, 
                                                  selected_stalemate_option, selected_castling_option, 
                                                  selected_promotion_option, screen)

                        # Draw and update the game state
                        draw_canvas(screen, scroll_surface, scroll_x)
                        draw_move_history(scroll_surface, player_moves, scroll_x)

                        # If highlighting is enabled, show possible moves for the last move
                        if current_highlight_option == "On":
                            highlight_possible_moves(screen, board, move.from_square)

                    except ValueError:
                        print(f"Invalid move format: {data}")  # Handle case where move parsing fails
                        continue  # Skip this iteration

        except Exception as e:
            print(f"Error receiving move: {e}")
            break  # Exit the loop on error




def main_menu(selected_board_theme,selected_piece_theme,selected_move_method,selected_sound_option,selected_en_passant_option, selected_stalemate_option,selected_castling_option, selected_promotion_option,white_name,black_name,selected_highlight_option,bot_val,time_limit=None, player_color=None, client_socket=None): #need default time limit for 2 player mode call

#region intializations
    from the_menu import Button
    from the_menu import go_back

    # define screen in the main menu to Resize the display mode for the board
    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))  # Set to board size
    pygame.display.set_caption('GAME PLAY')

    #BACK BUTTON
    button_back = Button('Back',820,600,100,50,BUTTON_GREEN,BUTTON_RED)

    # COLLAPSE BUTTON
    button_collapse = Button('Status', 720, 600, 100, 50, BUTTON_GREEN, BUTTON_RED)

    #UNDO BUTTON
    button_undo = Button('Undo',520,600,100,50,BUTTON_GREEN,BUTTON_RED)
    #REDO BUTTON
    button_redo = Button('Redo',620,600,100,50,BUTTON_GREEN,BUTTON_RED)

    running = True
    global menu,current_board_theme,current_piece_theme, current_move_method,current_sound_option,current_en_passant_option, current_stalemate_option,current_castling_option,current_promotion_option,current_highlight_option
    global selected_square, dragging_piece, dragging_piece_image, dragging_piece_position

    # Set the current theme to the selected theme
    current_board_theme = selected_board_theme
    current_piece_theme = selected_piece_theme
    current_move_method = selected_move_method
    current_sound_option = selected_sound_option
    current_en_passant_option = selected_en_passant_option
    current_stalemate_option = selected_stalemate_option
    current_castling_option = selected_castling_option
    current_promotion_option = selected_promotion_option
    current_highlight_option = selected_highlight_option

    # Menu expanded state
    menu_expanded = False

    scroll_surface = pygame.Surface((1000,MOVE_CANVAS_HIGHT))
    scroll_surface.fill(CANVAS_COLOR)
    scroll_x = 0

    board,captured_white,captured_black,white_score,black_score,player_moves = reset_game_state(scroll_surface)

    redo_log = []
    undo_button_pressed = False
    current_turn = chess.WHITE
#endregion

    player_names = {'white': white_name, 'black': black_name} 
    if client_socket:  # Check if online mode is active
        move_listener_thread = threading.Thread(target=listen_for_moves, args=(
            client_socket, board, player_moves,
            captured_white, captured_black,
            white_score, black_score,
            current_en_passant_option, current_stalemate_option, 
            current_castling_option, current_promotion_option,
            scroll_surface, scroll_x, screen,
            current_highlight_option,player_names
        ))
        move_listener_thread.daemon = True  # Ensure the thread exits when the main program does
        move_listener_thread.start()

    while running:
        screen.fill(THE_BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check if the back button is pressed
            if button_back.handle_event(event):
                 go_back()  # Return to the previous menu
                 pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
                 return #exit game loop
            
            # Check if the collapse button is pressed to toggle menu
            if button_collapse.handle_event(event):
                menu_expanded = not menu_expanded  # Toggle menu expansion
                

        # Determine if the player is white
        is_white = player_color == "white"  # Assuming player_color is a string
        
        white_name = player_names['white']
        black_name = player_names['black']
        if client_socket:  # Check if online mode is active
            white_score, black_score = handle_movement_online(
                event,
                board,
                current_en_passant_option,
                current_stalemate_option,
                current_castling_option,
                current_promotion_option,
                captured_white,
                captured_black,
                white_score,
                black_score,
                scroll_surface,
                player_moves,
                scroll_x,
                screen,
                redo_log, 
                current_highlight_option,
                client_socket,  # Pass the socket connection
                is_white        # Pass the player's color (True for white, False for black)
            )

                      
        elif bot_val:  # Check if playing against a bot
            if current_move_method == 'Click':
                white_score, black_score = handle_piece_movement_bot(event, board, current_en_passant_option, 
                                                                current_stalemate_option, current_castling_option, 
                                                                current_promotion_option, captured_white, 
                                                                captured_black, white_score, black_score, 
                                                                scroll_surface, player_moves, scroll_x, screen, 
                                                                redo_log, current_highlight_option,time_limit)
            
            elif current_move_method == 'Drag':
                 white_score, black_score = handle_piece_drag_bot(event, board, current_en_passant_option, current_stalemate_option, 
                                current_castling_option, current_promotion_option, captured_white, captured_black, 
                                white_score, black_score, current_piece_theme, scroll_surface,player_moves,scroll_x,screen,redo_log,current_highlight_option,time_limit,bot_enabled=True)
                 
            if button_undo.handle_event(event):
                if not undo_button_pressed:
                    undo_button_pressed = True
                    if player_moves or is_bot_turn:  # Check if there are moves to undo (player or bot)
                        board, white_score, black_score, captured_white, captured_black, current_turn = undo_bots(board, player_moves, captured_white, captured_black, redo_log, white_score, black_score)

                        # Draw the updated scoreboard and captured pieces
                        draw_scoreboard_and_captured_pieces(screen, captured_white, captured_black, white_score, black_score, white_name, black_name)
                        pygame.display.update()
                    
                    undo_button_pressed = False

            elif button_redo.handle_event(event):
                if redo_log:
                    board, white_score, black_score, captured_white, captured_black = redo_bots(
                        board, redo_log, player_moves, captured_white, captured_black, white_score, black_score
                    )

                    # Draw the updated scoreboard and captured pieces
                    draw_scoreboard_and_captured_pieces(screen, captured_white, captured_black, white_score, black_score, white_name, black_name)
                    pygame.display.update()

                    # After a redo, set the turn to the opposite player
                    current_turn = chess.BLACK if current_turn == chess.WHITE else chess.WHITE
                    is_bot_turn = False  # Ensure it's not the bot's turn after a redo

        else: # Two-player mode
            # Handle piece movement based on the current movement mode
            if current_move_method == 'Click':
                white_score, black_score = handle_piece_movement(event, board,current_en_passant_option, current_stalemate_option,current_castling_option,current_promotion_option,
                                      captured_white, captured_black, white_score, black_score,scroll_surface,player_moves,scroll_x,screen,redo_log,current_highlight_option)
                
            elif current_move_method == 'Drag':
                white_score, black_score = handle_piece_drag(event, board, current_en_passant_option, current_stalemate_option, 
                                current_castling_option, current_promotion_option, captured_white, captured_black, 
                                white_score, black_score, current_piece_theme, scroll_surface,player_moves,scroll_x,screen,redo_log,current_highlight_option)


             #handle undo button
            
            if button_undo.handle_event(event):
                if not undo_button_pressed:
                    undo_button_pressed = True
                    if player_moves:
                        board,white_score,black_score,captured_white,captured_black = undo_move(board,player_moves,captured_white,captured_black,redo_log,white_score,black_score)

                        # Draw the updated scoreboard and captured pieces
                        draw_scoreboard_and_captured_pieces(screen, captured_white, captured_black, white_score, black_score,white_name,black_name)
                        pygame.display.update()

                        current_turn = chess.BLACK if current_turn == chess.WHITE else chess.WHITE
                    undo_button_pressed = False

            elif button_redo.handle_event(event):
                if redo_log :
                    board, white_score,black_score, captured_white, captured_black = redo_moves(board,redo_log,player_moves,captured_white,captured_black,white_score,black_score)

                    # Draw the updated scoreboard and captured pieces
                    draw_scoreboard_and_captured_pieces(screen, captured_white, captured_black, white_score, black_score,white_name,black_name)
                    pygame.display.update()

                    current_turn = chess.BLACK if current_turn == chess.WHITE else chess.WHITE

#draw
#region            
        # Draw the chessboard with the current theme
        draw_board(screen, current_board_theme)
        #Draw the chess pieces || on top highlight
        draw_pieces(screen, board,current_piece_theme)

        # If dragging, draw the dragging piece
        if dragging_piece_image:
            screen.blit(dragging_piece_image, dragging_piece_position)

        # Draw the back button
        button_back.draw(screen)
        # Draw the collapse button
        button_collapse.draw(screen)
        #draw undo button
        button_undo.draw(screen)
        #draw redo button
        button_redo.draw(screen)

        #Canvas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            scroll_x += 5
        if keys[pygame.K_LEFT]:
            scroll_x -= 5
        
        scroll_x = max(0,scroll_x)
        max_scroll_x = (len(player_moves)//2)*200
        scroll_x = min(scroll_x,max_scroll_x)
        #draw canvas and the move history 
        draw_canvas(screen, scroll_surface,scroll_x)
        draw_move_history(scroll_surface,player_moves,scroll_x)
        #draw score and captured pieces
        draw_scoreboard_and_captured_pieces(screen,captured_white,captured_black,white_score,black_score,white_name,black_name)

        if current_highlight_option == "On":
            highlight_possible_moves(screen, board, selected_square)

        
#endregion

        # If the menu is expanded, display the current themes and options
        if menu_expanded:
            # Define a background color for the menu labels
            label_background_color = (50, 50, 50)  # Dark grey color for the background
            label_padding = 5  # Padding around the text

            # Display current themes
            board_theme_label = font.render(f"Current Board Theme: {current_board_theme}", True, TEXT_COLOR_WHITE)
            board_theme_rect = board_theme_label.get_rect(topleft=(10, 10))
            pygame.draw.rect(screen, label_background_color, board_theme_rect.inflate(label_padding * 2, label_padding * 2))
            screen.blit(board_theme_label, board_theme_rect.topleft)

            piece_theme_label = font.render(f"Current Piece Theme: {current_piece_theme}", True, TEXT_COLOR_WHITE)
            piece_theme_rect = piece_theme_label.get_rect(topleft=(300, 10))
            pygame.draw.rect(screen, label_background_color, piece_theme_rect.inflate(label_padding * 2, label_padding * 2))
            screen.blit(piece_theme_label, piece_theme_rect.topleft)

            move_label = font.render(f"Current Move Method: {current_move_method}", True, TEXT_COLOR_WHITE)
            move_rect = move_label.get_rect(topleft=(600, 10))
            pygame.draw.rect(screen, label_background_color, move_rect.inflate(label_padding * 2, label_padding * 2))
            screen.blit(move_label, move_rect.topleft)

            promotion_label = font.render(f"Current Promotion Status: {current_promotion_option}", True, TEXT_COLOR_WHITE)
            promotion_rect = promotion_label.get_rect(topleft=(10, 30))
            pygame.draw.rect(screen, label_background_color, promotion_rect.inflate(label_padding * 2, label_padding * 2))
            screen.blit(promotion_label, promotion_rect.topleft)

            sound_label = font.render(f"Current Sound Status: {current_sound_option}", True, TEXT_COLOR_WHITE)
            sound_rect = sound_label.get_rect(topleft=(300, 30))
            pygame.draw.rect(screen, label_background_color, sound_rect.inflate(label_padding * 2, label_padding * 2))
            screen.blit(sound_label, sound_rect.topleft)

            en_passant_label = font.render(f"Current En Passant Status: {current_en_passant_option}", True, TEXT_COLOR_WHITE)
            en_passant_rect = en_passant_label.get_rect(topleft=(600, 30))
            pygame.draw.rect(screen, label_background_color, en_passant_rect.inflate(label_padding * 2, label_padding * 2))
            screen.blit(en_passant_label, en_passant_rect.topleft)

            castling_label = font.render(f"Current Castling Status: {current_castling_option}", True, TEXT_COLOR_WHITE)
            castling_rect = castling_label.get_rect(topleft=(10, 50))
            pygame.draw.rect(screen, label_background_color, castling_rect.inflate(label_padding * 2, label_padding * 2))
            screen.blit(castling_label, castling_rect.topleft)

            stalemate_label = font.render(f"Current Stalemate Status: {current_stalemate_option}", True, TEXT_COLOR_WHITE)
            stalemate_rect = stalemate_label.get_rect(topleft=(300, 50))
            pygame.draw.rect(screen, label_background_color, stalemate_rect.inflate(label_padding * 2, label_padding * 2))
            screen.blit(stalemate_label, stalemate_rect.topleft)

        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()