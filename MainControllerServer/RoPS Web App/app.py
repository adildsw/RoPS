from flask import Flask, render_template, jsonify
import netifaces as ni
from flask_cors import CORS
from flask_restful import Api

app = Flask(__name__, static_folder='web/', template_folder='web/')

api = Api(app)

cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

temp_response = "[{'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 1, 'winner': 'Draw', 'robot_move': 'Rock', 'human_move': 'Rock', 'move_delay': 1619572875.615, 'robot_rhythm': 90, 'human_rhythm': 0}, {'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 2, 'winner': 'Robot', 'robot_move': 'Paper', 'human_move': 'Rock', 'move_delay': 1619572884.215, 'robot_rhythm': 90, 'human_rhythm': 0}, {'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 3, 'winner': 'Human', 'robot_move': 'Scissor', 'human_move': 'Rock', 'move_delay': 1619572892.895, 'robot_rhythm': 90, 'human_rhythm': 0}, {'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 4, 'winner': 'Human', 'robot_move': 'Scissor', 'human_move': 'Rock', 'move_delay': -0.5376110076904297, 'robot_rhythm': 90, 'human_rhythm': 89.0}, {'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 5, 'winner': 'Human', 'robot_move': 'Scissor', 'human_move': 'Rock', 'move_delay': -0.4656362533569336, 'robot_rhythm': 90, 'human_rhythm': 94.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 1, 'winner': 'Robot', 'robot_move': 'Rock', 'human_move': 'Scissor', 'move_delay': -0.6082160472869873, 'robot_rhythm': 90, 'human_rhythm': 92.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 2, 'winner': 'Robot', 'robot_move': 'Rock', 'human_move': 'Scissor', 'move_delay': -0.7052872180938721, 'robot_rhythm': 90, 'human_rhythm': 84.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 3, 'winner': 'Draw', 'robot_move': 'Rock', 'human_move': 'Rock', 'move_delay': -0.699099063873291, 'robot_rhythm': 90, 'human_rhythm': 89.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 4, 'winner': 'Robot', 'robot_move': 'Rock', 'human_move': 'Scissor', 'move_delay': -0.6389620304107666, 'robot_rhythm': 90, 'human_rhythm': 93.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 5, 'winner': 'Draw', 'robot_move': 'Rock', 'human_move': 'Rock', 'move_delay': -0.662708044052124, 'robot_rhythm': 90, 'human_rhythm': 83.0}]"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result")
def results():
    return render_template("result.html")

@app.route("/temp", methods=["GET"])
def temp():
    return jsonify(temp_response)

def main():
    host_ip = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']
    host_port = 5555
    app.run(host_ip, host_port, debug=True)

if __name__ == "__main__":
    main()