from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.game_engine import GameEngine

app    = Flask(__name__, static_folder="static")
CORS(app)
engine = GameEngine()


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/start", methods=["POST"])
def start():
    data        = request.get_json()
    player_name = data.get("player_name", "").strip()
    house       = data.get("house", "Gryffindor").strip()

    if not player_name:
        return jsonify({"error": "Player name required"}), 400

    result = engine.start_game(player_name, house)
    return jsonify(result)


@app.route("/action", methods=["POST"])
def action():
    data        = request.get_json()
    player_name = data.get("player_name", "").strip()
    action      = data.get("action", "").strip()

    if not player_name or not action:
        return jsonify({"error": "Player name and action required"}), 400

    result = engine.take_action(player_name, action)
    return jsonify(result)


@app.route("/state/<player_name>", methods=["GET"])
def get_state(player_name):
    from src.state_manager import load_state
    return jsonify(load_state(player_name))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
