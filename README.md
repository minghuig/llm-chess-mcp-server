# Chess MCP Server

A Model Context Protocol (MCP) server that enables LLMs to play chess games. Built with Python using the `python-chess` library for chess logic and move validation.

## Features

- **new_game**: Start a fresh chess game
- **make_move**: Make a move with automatic validation (supports UCI and SAN notation)
- **get_game_state**: View the current board with rank/file labels, last move, turn, and game status

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

Run the server directly:
```bash
python chess_server.py
```

### Configuring with Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chess": {
      "command": "python",
      "args": ["/Users/minghuiguo/Documents/ai_chess_mcp_server/chess_server.py"]
    }
  }
}
```

Make sure to update the path to match your actual installation directory.

### Playing Chess

Once configured, you can interact with Claude to play chess:

**Example conversation:**
```
You: Let's play chess! Start a new game.
Claude: [calls new_game tool]

You: I'll play e4
Claude: [calls make_move with "e4"]

You: What's the current board state?
Claude: [calls get_game_state]
```

### Move Notation

The server accepts moves in two formats:

1. **UCI notation**: `e2e4`, `g1f3`, `e1g1` (for castling)
2. **Standard Algebraic Notation (SAN)**: `e4`, `Nf3`, `O-O` (for castling)

## Tools

### new_game
Starts a new chess game with the standard starting position.

**Parameters**: None

**Returns**: Confirmation message with the initial board state

### make_move
Makes a chess move after validating it's legal.

**Parameters**:
- `move` (string): The move in UCI or SAN format

**Returns**: Success message with updated board state, or error if move is illegal

### get_game_state
Returns the current state of the game.

**Parameters**: None

**Returns**:
- Unicode chess piece visualization with rank/file labels
- Last move played (in SAN notation)
- Current turn (White/Black)
- Game status (Ongoing/Check/Checkmate/Draw)
- Number of moves played

## Implementation Details

- Single global game stored in memory
- Game resets when `new_game` is called
- Uses `python-chess` for all chess logic and validation
- Supports standard chess rules including castling, en passant, and promotion
