import socket
import threading
import chess
import pygame
from the_board import draw_board, draw_pieces, current_board_theme,SQUARE_SIZE, highlight_possible_moves, current_piece_theme, GAME_BOARD_Y_OFFSET

# Setup socket connection (client)
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('SERVER_IP_ADDRESS', 5555))  # Replace with your server's IP
    return client_socket

# Thread to handle receiving opponent's moves
def receive_moves_from_opponent(client_socket, board, screen, captured_white, captured_black, white_score, black_score):
    while True:
        try:
            move_data = client_socket.recv(1024).decode('utf-8')
            if move_data:
                move = chess.Move.from_uci(move_data)
                board.push(move)
                # Update the game board, UI, etc.
                draw_board(screen, current_board_theme)
                draw_pieces(screen, board, current_piece_theme)
                pygame.display.update()
        except ConnectionResetError:
            print("Connection to opponent lost.")
            break

# Send move to the server
def send_move_to_server(client_socket, move):
    move_data = move.uci()  # Send move in UCI format (e.g., "e2e4")
    client_socket.sendall(move_data.encode('utf-8'))

# Update the handle_piece_movement function
def handle_piece_movement(event, board, selected_en_passant_option, selected_stalemate_option, 
                          selected_castling_option, selected_promotion_option, captured_white, captured_black, 
                          white_score, black_score, scroll_surface, player_moves, scroll_x, screen, redo_log, 
                          current_highlight_option, client_socket):  # Add client_socket as argument
    
    global selected_square, is_click_enabled, current_sound_option

    if event.type == pygame.MOUSEBUTTONDOWN and is_click_enabled:
        x, y = event.pos
        col = x // SQUARE_SIZE
        row = (y - GAME_BOARD_Y_OFFSET) // SQUARE_SIZE

        if 0 <= col < 8 and 0 <= row < 8:
            square = chess.square(col, 7 - row)

            if selected_square is None:
                if board.piece_at(square):
                    selected_square = square
            else:
                move = chess.Move(selected_square, square)

                if move in board.legal_moves:
                    board.push(move)
                    send_move_to_server(client_socket, move)  # Send move to server
                    draw_board(screen, current_board_theme)
                    draw_pieces(screen, board, current_piece_theme)
                    pygame.display.update()

                selected_square = None
        is_click_enabled = False

    if event.type == pygame.MOUSEBUTTONUP:
        is_click_enabled = True

    if current_highlight_option == "On" and selected_square is not None:
        highlight_possible_moves(screen, board, selected_square)

    return white_score, black_score
