from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from dotenv import load_dotenv


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

load_dotenv()

app = Flask(__name__)
cors = CORS(app, resources={r"/socket.io/*": {"origins": "http://localhost:5500"}})

# Uncomment the line below, add 'client-url' to .env for custom client URL, i.e. to incorporate ports of choice
# cors = CORS(app, resources={r"/socket.io/*": {"origins": os.environ.get("client-url")}})


app.config["SECRET_KEY"] = os.environ.get("secret-key")


@app.route("/")
def index():
    return "Server:\nWelcome to the game!"


# socketio = SocketIO(app)
socketio = SocketIO(
    app, cors_allowed_origins=["http://127.0.0.1:5500", "http://localhost:5500"]
)

"""
# Uncomment the section below, add 'client-url' to .env for custom client URL, i.e. to incorporate ports of choice
socketio = SocketIO(
    app, cors_allowed_origins=[os.environ.get("client-url")]
)
"""

# Game initialization
board = [["" for _ in range(5)] for _ in range(5)]
player_turns = ["A", "B"]
current_player = player_turns[0]
game_over = False
move_history = []


@socketio.on("initialize_game")
def handle_initialize_game(data):
    initialize_game(data["player_a_characters"], data["player_b_characters"])


@socketio.on("make_move")
def handle_make_move(data):
    process_move(data["player"], data["character"], data["move"])


if __name__ == "__main__":
    socketio.run(app, debug=True)
