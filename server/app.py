from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from dotenv import load_dotenv

"""
from game_logic import (
    initialize_game,
    process_move,
    find_character_position,
    determine_new_position,
    move_pawn,
    move_hero1,
    move_hero2,
    is_valid_move,
    check_for_combat,
    check_game_over,
)
from characters import characters
"""

app = Flask(__name__)
cors = CORS(app, resources={r"/socket.io/*": {"origins": "http://localhost:5500"}})

load_dotenv()
app.config["SECRET_KEY"] = os.environ.get("secret-key")


@app.route("/")
def index():
    return "Server:\nWelcome to the game!"


# socketio = SocketIO(app)
socketio = SocketIO(
    app, cors_allowed_origins=["http://127.0.0.1:5500", "http://localhost:5500"]
)

# Game initialization
board = [["" for _ in range(5)] for _ in range(5)]
player_turns = ["A", "B"]
current_player = player_turns[0]
game_over = False
move_history = []


characters = {
    "P": {"name": "Pawn", "movement": 1},
    "H1": {"name": "Hero1", "movement": 2},
    "H2": {"name": "Hero2", "movement": 2, "diagonal": True},
}


def initialize_game(player_a_characters, player_b_characters):
    global board, current_player, game_over, move_history
    board = [["" for _ in range(5)] for _ in range(5)]
    game_over = False
    move_history = []
    for i, char in enumerate(player_a_characters):
        board[0][i] = f"A-{char}"
    for i, char in enumerate(player_b_characters):
        board[4][i] = f"B-{char}"
    current_player = "A"
    emit(
        "game_initialized",
        {"board": board, "current_player": current_player},
        broadcast=True,
    )


def process_move(player, character, move):
    global current_player, game_over
    if game_over:
        return

    char_type = character[2:]
    char_pos = find_character_position(player, character)

    if not char_pos:
        emit("invalid_move", {"message": "Character does not exist."}, room=request.sid)
        return

    new_pos = determine_new_position(char_pos, char_type, move)

    if new_pos and is_valid_move(new_pos, player):
        board[new_pos[0]][new_pos[1]] = f"{player}-{character}"
        board[char_pos[0]][char_pos[1]] = ""
        move_history.append(f"{player}-{character} moved {move}")
        check_for_combat(new_pos, player)
        if check_game_over():
            emit("game_over", {"winner": player}, broadcast=True)
        else:
            current_player = "B" if player == "A" else "A"
            emit(
                "update_board",
                {
                    "board": board,
                    "current_player": current_player,
                    "move_history": move_history,
                },
                broadcast=True,
            )
    else:
        emit("invalid_move", {"message": "Invalid move."}, room=request.sid)


def find_character_position(player, character):
    for r in range(5):
        for c in range(5):
            if board[r][c] == f"{player}-{character}":
                return (r, c)
    return None


def determine_new_position(pos, char_type, move):
    r, c = pos
    if char_type == "P":
        return move_pawn(r, c, move)
    elif char_type == "H1":
        return move_hero1(r, c, move)
    elif char_type == "H2":
        return move_hero2(r, c, move)
    return None


def move_pawn(r, c, move):
    if move == "L":
        return (r, c - 1)
    elif move == "R":
        return (r, c + 1)
    elif move == "F":
        return (r - 1, c)
    elif move == "B":
        return (r + 1, c)
    return None


def move_hero1(r, c, move):
    if move == "L":
        return (r, c - 2)
    elif move == "R":
        return (r, c + 2)
    elif move == "F":
        return (r - 2, c)
    elif move == "B":
        return (r + 2, c)
    return None


def move_hero2(r, c, move):
    if move == "FL":
        return (r - 2, c - 2)
    elif move == "FR":
        return (r - 2, c + 2)
    elif move == "BL":
        return (r + 2, c - 2)
    elif move == "BR":
        return (r + 2, c + 2)
    return None


def is_valid_move(new_pos, player):
    r, c = new_pos
    if r < 0 or r >= 5 or c < 0 or c >= 5:
        return False
    if board[r][c] and board[r][c].startswith(player):
        return False
    return True


def check_for_combat(new_pos, player):
    r, c = new_pos
    opponent = "B" if player == "A" else "A"
    if board[r][c].startswith(opponent):
        board[r][c] = ""  # Remove opponent's character


def check_game_over():
    player_a_alive = any("A-" in cell for row in board for cell in row)
    player_b_alive = any("B-" in cell for row in board for cell in row)
    return not (player_a_alive and player_b_alive)


@socketio.on("initialize_game")
def handle_initialize_game(data):
    initialize_game(data["player_a_characters"], data["player_b_characters"])


@socketio.on("make_move")
def handle_make_move(data):
    process_move(data["player"], data["character"], data["move"])


if __name__ == "__main__":
    socketio.run(app, debug=True)
