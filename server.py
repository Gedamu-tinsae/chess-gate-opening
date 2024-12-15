import socket
import threading

# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 5555  # Define the port for the server

# Store player names
white_name = ""
black_name = ""

# Handle client communication
def handle_client(client_socket, opponent_socket, client_color):
    global white_name, black_name
    while True:
        try:
            # Receive the message from the client
            data = client_socket.recv(1024).decode('utf-8')

            if not data:
                continue

            # Handle player name reception
            if data.startswith("NAMES:"):
                if client_color == 'white':
                    white_name = data.split(":")[1]
                    print(f"Stored white player's name: {white_name}")
                    opponent_socket.send(f"white_name:{white_name}".encode('utf-8'))
                else:  # black
                    black_name = data.split(":")[1]
                    print(f"Stored black player's name: {black_name}")
                    opponent_socket.send(f"black_name:{black_name}".encode('utf-8'))

            # Fetch player names on request
            elif data == "get_white_name":
                client_socket.send(f"white_name:{white_name}".encode('utf-8'))
            elif data == "get_black_name":
                client_socket.send(f"black_name:{black_name}".encode('utf-8'))

            # Handle move exchange between players
            else:
                # Send the move to the opponent
                opponent_socket.send(data.encode('utf-8'))

        except ConnectionResetError:
            print(f"{client_color} player disconnected.")
            break

    client_socket.close()

# Start the server
def start_server(host=SERVER_HOST, port=SERVER_PORT):
    global white_name, black_name

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Only two players allowed
    print("Server started, waiting for players...")

    # Accept player 1 (white)
    player1_socket, _ = server_socket.accept()
    print("Player 1 connected, assigned color: white")
    player1_socket.send("white".encode('utf-8'))  # Send player color

    # Accept player 2 (black)
    player2_socket, _ = server_socket.accept()
    print("Player 2 connected, assigned color: black")
    player2_socket.send("black".encode('utf-8'))  # Send player color

    # Create threads to handle communication
    threading.Thread(target=handle_client, args=(player1_socket, player2_socket, 'white')).start()
    threading.Thread(target=handle_client, args=(player2_socket, player1_socket, 'black')).start()

if __name__ == '__main__':
    start_server()
