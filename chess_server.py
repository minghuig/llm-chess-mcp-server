#!/usr/bin/env python3
"""
MCP Chess Server - Play chess games with an LLM
"""

import chess
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Global game state (single game in memory)
current_game: chess.Board = chess.Board()
last_move_san: str = ""
captured_white: list[str] = []  # White pieces captured by Black
captured_black: list[str] = []  # Black pieces captured by White


def get_game_status(board: chess.Board) -> str:
    """Get the current game status as a human-readable string."""
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"Checkmate! {winner} wins!"
    elif board.is_stalemate():
        return "Stalemate - Draw"
    elif board.is_insufficient_material():
        return "Draw - Insufficient material"
    elif board.is_fifty_moves():
        return "Draw - Fifty move rule"
    elif board.is_repetition():
        return "Draw - Threefold repetition"
    elif board.is_check():
        return "Check!"
    else:
        return "Ongoing"


def format_board_state(board: chess.Board) -> str:
    """Format the complete game state as a readable string."""
    output = []

    # ASCII board representation with Unicode chess pieces and labels
    output.append("Current Board:")

    # Show captured white pieces (captured by Black) at the top
    output.append(" ".join(captured_white))

    # Get the unicode board and add rank labels on the left
    board_lines = board.unicode().split('\n')
    for i, line in enumerate(board_lines):
        rank = 8 - i
        output.append(f"{rank} {line}")

    output.append("  a b c d e f g h")

    # Show captured black pieces (captured by White) at the bottom
    output.append(" ".join(captured_black))

    # Show last move if available
    if last_move_san:
        output.append(f"Last move: {last_move_san}")

    # Game metadata
    turn = "White" if board.turn == chess.WHITE else "Black"
    output.append(f"Turn: {turn}")
    output.append(f"Status: {get_game_status(board)}")
    output.append(f"FEN: {board.fen()}")

    return "\n".join(output)


# Create MCP server
app = Server("chess-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available chess game tools."""
    return [
        Tool(
            name="new_game",
            description="Start a new chess game. This will reset the current game board to the initial position.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="make_move",
            description=(
                "Make a chess move. Validates the move and applies it if legal. "
                "Accepts moves in UCI format (e.g., 'e2e4', 'e7e5', 'e1g1' for castling) "
                "or Standard Algebraic Notation (e.g., 'e4', 'Nf3', 'O-O' for castling). "
                "Returns the updated board state after the move."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "move": {
                        "type": "string",
                        "description": "The move to make in UCI format (e.g., 'e2e4') or SAN format (e.g., 'e4', 'Nf3')"
                    }
                },
                "required": ["move"]
            }
        ),
        Tool(
            name="get_game_state",
            description=(
                "Get the current state of the chess game. Returns the board position with "
                "Unicode chess pieces and rank/file labels, captured pieces for each side, "
                "last move played, whose turn it is, game status, and FEN notation."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls for chess operations."""
    global current_game, last_move_san, captured_white, captured_black

    if name == "new_game":
        current_game = chess.Board()
        last_move_san = ""
        captured_white = []
        captured_black = []
        return [
            TextContent(
                type="text",
                text=f"New game started!\n\n{format_board_state(current_game)}"
            )
        ]

    elif name == "make_move":
        move_str = arguments.get("move")
        if not move_str:
            return [
                TextContent(
                    type="text",
                    text="Error: Move parameter is required"
                )
            ]

        try:
            # Try to parse the move (supports both UCI and SAN formats)
            move = current_game.parse_san(move_str)
        except ValueError:
            try:
                # If SAN fails, try UCI format
                move = chess.Move.from_uci(move_str)
            except ValueError:
                return [
                    TextContent(
                        type="text",
                        text=f"Error: Invalid move format '{move_str}'. Use UCI format (e.g., 'e2e4') or SAN format (e.g., 'e4', 'Nf3')."
                    )
                ]

        # Check if the move is legal
        if move not in current_game.legal_moves:
            return [
                TextContent(
                    type="text",
                    text=f"Error: Illegal move '{move_str}'. That move is not legal in the current position."
                )
            ]

        # Store the move in SAN notation before applying it
        last_move_san = current_game.san(move)

        # Check if this move captures a piece
        captured_piece = current_game.piece_at(move.to_square)
        if captured_piece:
            # Get the unicode symbol for the captured piece
            piece_symbol = captured_piece.unicode_symbol()
            # Add to appropriate captured list based on piece color
            if captured_piece.color == chess.WHITE:
                captured_white.append(piece_symbol)
            else:
                captured_black.append(piece_symbol)

        # Make the move
        current_game.push(move)

        return [
            TextContent(
                type="text",
                text=f"Move {move_str} played successfully!\n\n{format_board_state(current_game)}"
            )
        ]

    elif name == "get_game_state":
        return [
            TextContent(
                type="text",
                text=format_board_state(current_game)
            )
        ]

    else:
        return [
            TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )
        ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
