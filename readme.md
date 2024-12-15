# Chess Game with AI, Multiplayer, and Custom Rules

Welcome to this versatile Chess Game project! Built using Python and Pygame, it combines a variety of gameplay modes, including single-player (against an AI bot powered by Stockfish), local multiplayer, and online multiplayer. The game incorporates customizable rules, advanced features, and real-time tracking of moves, scores, and captured pieces.

## Features

### Game Modes
1. **Single Player**:
   - Play against an AI bot integrated with Stockfish's API for decision-making.
   - Adjustable difficulty levels: Beginner, Intermediate, and Advanced.
2. **Multiplayer**:
   - **Local Play**: Two players can play on the same computer.
   - **Online Play**: Play with a friend over the network using real-time move synchronization.

### Gameplay Features
- **Movement Options**:
  - **Click**: Select and move pieces by clicking.
  - **Drag-and-Drop**: Move pieces intuitively by dragging them across the board.
- **Customizable Rules**:
  - Toggle features like En Passant, Castling, Pawn Promotion, and Stalemate from the settings menu.
  - Choose promotion options (e.g., queen, rook, bishop, knight).
- **Bot Gameplay**:
  - Powered by Stockfish's API for sophisticated decision-making.
  - Adjustable time limit for the bot's moves.
- **Undo/Redo Moves**:
  - Undo or redo player and bot moves with updates to captured pieces and scores.
- **Move History & Highlights**:
  - A scrollable log displays all moves made during the game.
  - Highlights the last move for both players and shows legal moves when selecting pieces.
- **Player Names & Score Tracking**:
  - Input custom player names reflected in the scoreboard.
  - Captured pieces are displayed in real-time.
- **Sound Effects**:
  - Customizable sounds for moves, captures, and other events.

## Installation

### Prerequisites
- **Python 3.x**
- **Pygame** library
- **Stockfish** chess engine

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo-link
   cd chess-game
   ```

2. Install dependencies:
   ```bash
   pip install pygame chess
   ```

3. Download and set up **Stockfish**:
   - Visit the [Stockfish downloads page](https://stockfishchess.org/download/).
   - Choose the appropriate version for your operating system.
   - Extract the downloaded files and place the `stockfish` or `stockfish.exe` binary in the `stockfish/` folder of the project.

4. Run the game:
   ```bash
   python main.py
   ```

## How to Play

### Single Player
- Choose the difficulty level.
- Move pieces using click or drag-and-drop. The bot responds after each move based on Stockfish's calculations.

### Multiplayer
- **Local**: Two players share the same computer.
- **Online**: One player hosts a server, and the other connects using the provided IP address.

### Customization
- Toggle game rules like En Passant, Castling, and Pawn Promotion via the settings menu.
- Switch between movement options (click or drag-and-drop).

## File Structure
```
├── rootfolder/            # Resources for the game
   ├── pieces/                # Piece images and themes
   ├── sounds/                # Sound files
   ├── stockfish/             # Stockfish engine
   ├── the_board.py           # Core game logic
   ├── the_menu.py            # Settings menu and rules
   ├── server.py              # Online multiplayer server logic
   ├── client.py              # Online multiplayer client logic
```

## Running Multiplayer
To play in online multiplayer mode:
1. Open three terminal instances.
2. Navigate to the root folder in all instances:
   ```bash
   cd "C:\Users\to\root\folder"
   ```
3. Start the server:
   ```bash
   python server.py
   ```
4. Run `the_menu.py` on the other two instances to start the game for both players.

## Known Issues

### End Game
- The end game screen (e.g., checkmate, stalemate, or draw) is incomplete.
  - It should display results with options to replay or quit.
  - Not fully implemented in all movement functions.
- En Passant capture is not added to the score tally.

### Bot Behavior
- Add a delay between player and bot turns.
- Fix click-based movement for bots, as it occasionally behaves unpredictably.
- Consider implementing a custom AI algorithm instead of Stockfish for more flexibility.

## Suggestions for Improvement

### Networking
- Implement graceful handling of disconnects, including notifications and reconnect options.
- Add user feedback (e.g., loading screens) during connection setup.
- Provide retry options for failed connections.

### Gameplay
- Add a pawn promotion dialog for players to choose the desired piece.
- Handle all end game conditions properly, including notifications for checkmate, stalemate, or draw.
- Improve error handling and stability for online multiplayer.
- Include a timed chess clock for competitive play.

### User Experience
- Enhance visual feedback for invalid moves and rule violations.
- Prompt players for their names at the start to personalize the experience.
- Introduce additional themes for boards and pieces.

## Stockfish Integration

### How It Works
- The game utilizes Stockfish's API for AI decision-making.
- Players can set a time limit for the bot’s moves, affecting its depth of calculation and performance.

### Setting Up Stockfish
Follow these steps to download and install Stockfish:
1. Visit the [Stockfish downloads page](https://stockfishchess.org/download/).
2. Extract the ZIP file and locate the `stockfish` or `stockfish.exe` binary.
3. Place the binary in the `stockfish/` folder.
4. Test Stockfish in the terminal:
   ```bash
   cd path/to/stockfish
   ./stockfish
   ```
   Use commands like `position startpos` and `go` to interact with the engine.

## Future Features
- **Timed Chess Clock**: Add a timer for each player.
- **Spectator Mode**: Allow others to watch live games.
- **Enhanced AI**: Implement a custom chess AI.
- **Expanded Themes**: Offer more customization for board and piece designs.

---

**License**: MIT License

---

### Links
- **Comprehensive Chess Rules**: [Eddie's YouTube Playlist](https://www.youtube.com/watch?v=EnYui0e73Rs&list=PLBwF487qi8MGU81nDGaeNE1EnNEPYWKY_&index=1)
- **Live Demo**: [Gameplay Video](https://www.youtube.com/watch?v=fGK8V6CtfEc)

