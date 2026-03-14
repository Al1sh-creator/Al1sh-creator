#!/usr/bin/env python3
"""Interactive Chess Bot for GitHub Profile README"""
import chess
import chess.svg
import sys
import os

BOARD_FILE = ".github/chess/board.fen"
README_FILE = "README.md"
SVG_FILE = "chess-board.svg"
CHESS_START = "<!-- chess-start -->"
CHESS_END = "<!-- chess-end -->"
REPO = "Al1sh-creator/Al1sh-creator"

def load_board():
    if os.path.exists(BOARD_FILE):
        with open(BOARD_FILE) as f:
            fen = f.read().strip()
        if fen:
            return chess.Board(fen)
    return chess.Board()

def save_board(board):
    os.makedirs(os.path.dirname(BOARD_FILE), exist_ok=True)
    with open(BOARD_FILE, "w") as f:
        f.write(board.fen())

def render_svg(board):
    svg = chess.svg.board(board=board, size=380, coordinates=True)
    with open(SVG_FILE, "w") as f:
        f.write(svg)

def move_link(uci):
    base = f"https://github.com/{REPO}/issues/new"
    return f"[`{uci}`]({base}?title=chess%3A+{uci}&labels=chess&body=Playing+move+{uci})"

def update_readme(board):
    turn = "⬜ White" if board.turn == chess.WHITE else "⬛ Black"

    if board.is_checkmate():
        winner = "⬛ Black" if board.turn == chess.WHITE else "⬜ White"
        status = f"🏆 **Checkmate! {winner} wins!**"
        restart = f"[🔄 Start a new game](https://github.com/{REPO}/issues/new?title=chess%3A+restart&labels=chess&body=New+game)"
        moves_md = f"\n{restart}\n"
    elif board.is_stalemate() or board.is_insufficient_material():
        status = "🤝 **Draw!**"
        restart = f"[🔄 Start a new game](https://github.com/{REPO}/issues/new?title=chess%3A+restart&labels=chess&body=New+game)"
        moves_md = f"\n{restart}\n"
    else:
        check = " — ⚠️ **Check!**" if board.is_check() else ""
        status = f"**{turn}'s turn{check}**"
        legal = sorted([m.uci() for m in board.legal_moves])
        links = [move_link(m) for m in legal]
        rows = [" ".join(links[i:i+8]) for i in range(0, len(links), 8)]
        restart = f"[🔄 Restart](https://github.com/{REPO}/issues/new?title=chess%3A+restart&labels=chess&body=New+game)"
        moves_md = "\n" + "\n".join(rows) + f"\n\n{restart}\n"

    section = f"""{CHESS_START}
## ♟️ Play Chess Against Me!

> Click any move — it opens a GitHub Issue. The bot will update the board automatically!

{status}

![Chess Board](chess-board.svg)

**Make your move:**
{moves_md}
{CHESS_END}"""

    with open(README_FILE, encoding="utf-8") as f:
        content = f.read()

    start = content.find(CHESS_START)
    end = content.find(CHESS_END)

    if start != -1 and end != -1:
        new_content = content[:start] + section + content[end + len(CHESS_END):]
    else:
        new_content = content.rstrip() + "\n\n" + section + "\n"

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    move_uci = sys.argv[1].strip() if len(sys.argv) > 1 else None
    board = load_board()

    if move_uci == "restart":
        board = chess.Board()
        print("Game restarted!")
    elif move_uci:
        try:
            move = chess.Move.from_uci(move_uci)
            if move in board.legal_moves:
                board.push(move)
                print(f"Move {move_uci} applied!")
            else:
                print(f"Illegal move: {move_uci}")
                sys.exit(1)
        except Exception as e:
            print(f"Error processing move: {e}")
            sys.exit(1)

    save_board(board)
    render_svg(board)
    update_readme(board)
    print("Board updated successfully!")

if __name__ == "__main__":
    main()
