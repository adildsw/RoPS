# Importing System Libraries
from copy import deepcopy
from time import sleep, time
from datetime import datetime
from requests import get

# Importing 3rd-Party Libraries
import netifaces as ni
from flask import Flask, request, render_template, jsonify


# System Parameters
ROBOT_SERVER_IP = "http://192.168.86.77:5500/"
LATENCY = 0.3034
BPM_DIFFERENCE_THRESHOLD = 5
MOVE_DELAY_THRESHOLD = 0.3
BPM_DIFFERENCE_VIOLATION_THRESHOLD = 10
MOVE_DELAY_VIOLATION_THRESHOLD = 0.5

# Auxiliary Variables 
timestamp = []
recognition_timestamp = []
bpm_timestamp = []

# Game Parameters
bpm = 90
sample_count = 10
round_start_time = 0
round_count = 0
game_count = 0

game_logs = []

app = Flask(__name__, static_folder='RoPS Web App/web/', template_folder='RoPS Web App/web/')

temp_response = "[{'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 1, 'winner': 'Draw', 'robot_move': 'Rock', 'human_move': 'Rock', 'move_delay': 1619572875.615, 'robot_rhythm': 90, 'human_rhythm': 0}, {'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 2, 'winner': 'Robot', 'robot_move': 'Paper', 'human_move': 'Rock', 'move_delay': 1619572884.215, 'robot_rhythm': 90, 'human_rhythm': 0}, {'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 3, 'winner': 'Human', 'robot_move': 'Scissor', 'human_move': 'Rock', 'move_delay': 1619572892.895, 'robot_rhythm': 90, 'human_rhythm': 0}, {'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 4, 'winner': 'Human', 'robot_move': 'Scissor', 'human_move': 'Rock', 'move_delay': -0.5376110076904297, 'robot_rhythm': 90, 'human_rhythm': 89.0}, {'game_start_time': '2021-04-27 21:21:11.114488', 'round_count': 5, 'winner': 'Human', 'robot_move': 'Scissor', 'human_move': 'Rock', 'move_delay': -0.4656362533569336, 'robot_rhythm': 90, 'human_rhythm': 94.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 1, 'winner': 'Robot', 'robot_move': 'Rock', 'human_move': 'Scissor', 'move_delay': -0.6082160472869873, 'robot_rhythm': 90, 'human_rhythm': 92.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 2, 'winner': 'Robot', 'robot_move': 'Rock', 'human_move': 'Scissor', 'move_delay': -0.7052872180938721, 'robot_rhythm': 90, 'human_rhythm': 84.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 3, 'winner': 'Draw', 'robot_move': 'Rock', 'human_move': 'Rock', 'move_delay': -0.699099063873291, 'robot_rhythm': 90, 'human_rhythm': 89.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 4, 'winner': 'Robot', 'robot_move': 'Rock', 'human_move': 'Scissor', 'move_delay': -0.6389620304107666, 'robot_rhythm': 90, 'human_rhythm': 93.0}, {'game_start_time': '2021-04-27 21:37:45.659164', 'round_count': 5, 'winner': 'Draw', 'robot_move': 'Rock', 'human_move': 'Rock', 'move_delay': -0.662708044052124, 'robot_rhythm': 90, 'human_rhythm': 83.0}]"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result")
def results():
    return render_template("result.html")

@app.route("/temp")
def temp():
    return jsonify(temp_response)

# -----------------------------------------------
# Game Setting APIs
# -----------------------------------------------
@app.route("/bpm", methods=["GET"])
def get_bpm():
    return str(bpm)

@app.route("/setBpm", methods=["GET"])
def set_bpm():
    global bpm
    bpm = int(request.args.get("bpm"))
    return str(bpm)

@app.route("/sampleCount", methods=["GET"])
def get_sample_count():
    return str(sample_count)

@app.route("/setSampleCount", methods=["GET"])
def set_sample_count():
    global sample_count
    sample_count = request.args.get("sampleCount")
    return "Sample count set to " + sample_count

# -----------------------------------------------
# Robot Movement Timestamp APIs
# -----------------------------------------------
@app.route("/timestamps", methods=["GET"])
def get_timestamps():
    return str(timestamp)

@app.route("/addTimestamp", methods=["GET"])
def add_timestamp():
    global timestamp
    timestamp.append(request.args.get("data"))
    
    sleep(2)

    round_count, winner, robot_move, human_move, move_delay, robot_rhythm, human_rhythm = compute_results()

    game_result = "Round Count: {} | Winner: {} | Robot's Move: {} | Human's Move: {} | Move Delay: {} | Robot's Rhythm: {} | Human's Rhythm: {}".format(round_count, winner, robot_move, human_move, move_delay, robot_rhythm, human_rhythm)
    print(game_result)

    violation_status = "Valid"

    rhythm_feedback = "Good"
    if abs(human_rhythm - robot_rhythm) > BPM_DIFFERENCE_THRESHOLD:
        if human_rhythm - robot_rhythm < 0:
            rhythm_feedback = "Slow"
            if abs(human_rhythm - robot_rhythm) > BPM_DIFFERENCE_VIOLATION_THRESHOLD:
                violation_status = rhythm_feedback
        else:
            rhythm_feedback = "Fast"
            if abs(human_rhythm - robot_rhythm) > BPM_DIFFERENCE_VIOLATION_THRESHOLD:
                violation_status = rhythm_feedback

    move_feedback = "Good"
    if abs(move_delay) > MOVE_DELAY_THRESHOLD:
        if move_delay < 0:
            move_feedback = "Early"
            if abs(move_delay) > MOVE_DELAY_VIOLATION_THRESHOLD:
                violation_status = move_feedback
        else:
            move_feedback = "Late"
            if abs(move_delay) > MOVE_DELAY_VIOLATION_THRESHOLD:
                violation_status = move_feedback

    return winner + "_" + move_feedback + "_" + rhythm_feedback + "_" + violation_status

@app.route("/clearTimestamps", methods=["GET"])
def clear_timestamps():
    global timestamp
    timestamp.clear()
    return "Timestamp cleared"

# -----------------------------------------------
# Human Gesture Recognition Timestamp APIs
# -----------------------------------------------
@app.route("/recognitionTimestamps", methods=["GET"])
def get_recognition_timestamps():
    return str(recognition_timestamp)

@app.route("/addRecognitionTimestamp", methods=["GET"])
def add_recognition_timestamp():
    global recognition_timestamp
    recognition_timestamp.append(request.args.get("data"))
    return "Recognition Timestamp added"

@app.route("/clearRecognitionTimestamps", methods=["GET"])
def clear_recognition_timestamps():
    global recognition_timestamp
    recognition_timestamp.clear()
    return "Recognition Timestamp cleared"

# -----------------------------------------------
# Human BPM Estimation Timestamp APIs
# -----------------------------------------------
@app.route("/BPMTimestamps", methods=["GET"])
def get_BPM_timestamps():
    return str(bpm_timestamp)

@app.route("/addBPMTimestamp", methods=["GET"])
def add_bpm_timestamp():
    global bpm_timestamp
    bpm_timestamp.append(request.args.get("data"))
    return "BPM Timestamp added"
    
@app.route("/clearBPMTimestamps", methods=["GET"])
def clear_bpm_timestamps():
    global bpm_timestamp
    bpm_timestamp.clear()
    return "BPM Timestamps cleared"

# -----------------------------------------------
# Miscellaneous APIs
# -----------------------------------------------
@app.route("/latency", methods=["GET"])
def latency():
    timeClient = float(request.args.get("time"))
    timeServer = time()
    print("Latency: {}".format(timeClient - timeServer))
    return "{}".format(timeClient - timeServer)

@app.route("/gamelogs")
def get_game_logs():
    global game_logs
    # game_logs = "[{'game_count': 1, 'round_start_time': '2021-04-28 22:53:26.269526', 'round_count': 1, 'winner': 'Human', 'robot_move': 'Paper', 'human_move': 'Scissor', 'move_delay': -0.10903716087341309, 'robot_rhythm': 140.0, 'human_rhythm': 102.0, 'round_validity': 'Invalid'}, {'game_count': 1, 'round_start_time': '2021-04-28 22:53:36.003027', 'round_count': 2, 'winner': 'Draw', 'robot_move': 'Paper', 'human_move': 'Paper', 'move_delay': 0.24558424949645996, 'robot_rhythm': 140.0, 'human_rhythm': 141.0, 'round_validity': 'Valid'}, {'game_count': 1, 'round_start_time': '2021-04-28 22:53:44.839862', 'round_count': 3, 'winner': 'Robot', 'robot_move': 'Rock', 'human_move': 'Scissor', 'move_delay': 0.30166196823120117, 'robot_rhythm': 140.0, 'human_rhythm': 116.0, 'round_validity': 'Invalid'}, {'game_count': 1, 'round_start_time': '2021-04-28 22:53:54.689656', 'round_count': 4, 'winner': 'Human', 'robot_move': 'Rock', 'human_move': 'Paper', 'move_delay': 0.2990841865539551, 'robot_rhythm': 140.0, 'human_rhythm': 130.0, 'round_validity': 'Valid'}, {'game_count': 1, 'round_start_time': '2021-04-28 22:54:05.677435', 'round_count': 5, 'winner': 'Draw', 'robot_move': 'Rock', 'human_move': 'Rock', 'move_delay': 0.31174612045288086, 'robot_rhythm': 140.0, 'human_rhythm': 116.0, 'round_validity': 'Invalid'}]"
    return jsonify(str(game_logs))

@app.route("/playSampleRhythm")
def play_sample_rhythm():
    get(ROBOT_SERVER_IP + "playSampleRhythm")
    return "Done"

@app.route("/startGame")
def start_game():
    global game_count, round_count
    game_count += 1
    round_count = 0
    get(ROBOT_SERVER_IP + "startGame")
    return "Done"

def compute_results():
    global game_count, round_count, round_start_time

    robot_data = timestamp[len(timestamp) - 1]
    robot_move = robot_data.split("_")[0]
    robot_time = float(robot_data.split("_")[1]) - LATENCY

    rt = deepcopy(recognition_timestamp)
    bt = deepcopy(bpm_timestamp)

    bpm_time = 0
    bpm_value = 0

    gesture_time = 0
    gesture_value = "NaN"

    # Estimating BPM Value and Timestamp
    min_time = 9999
    for idx, entry in enumerate(bt):
        temp_bpm = float(entry.split("_")[0])
        temp_time = float(entry.split("_")[1])

        if abs(robot_time - temp_time) < min_time:
            min_time = abs(temp_time - robot_time)
            bpm_time = temp_time
            bpm_value = temp_bpm
    clear_bpm_timestamps()

    # Estimating Gesture Value and Timestamp
    min_time = 9999
    for idx, entry in enumerate(rt):
        temp_gesture = entry.split("_")[0]
        temp_time = float(entry.split("_")[1])

        if abs(robot_time - temp_time) < min_time:
            min_time = abs(temp_time - robot_time)
            gesture_time = temp_time
            gesture_value = temp_gesture
    clear_recognition_timestamps()

    game_count = game_count
    round_count += 1
    round_start_time = str(datetime.now())
    robot_move = robot_move
    human_move = gesture_value
    move_delay = bpm_time - robot_time
    robot_rhythm = float(bpm)
    human_rhythm = bpm_value
    winner = evaluate_winner(robot_move, human_move)

    round_validity = "Valid"
    if abs(move_delay) > MOVE_DELAY_VIOLATION_THRESHOLD or abs(human_rhythm - robot_rhythm) > BPM_DIFFERENCE_VIOLATION_THRESHOLD:
        round_validity = "Invalid"

    game_logs.append(
        {
            'game_count': game_count,
            'round_start_time': round_start_time,
            'round_count': round_count,
            'winner': winner,
            'robot_move': robot_move,
            'human_move': human_move,
            'move_delay': move_delay,
            'robot_rhythm': robot_rhythm,
            'human_rhythm': human_rhythm,
            'round_validity': round_validity
        }
    )

    with open('datalogs/{}.txt'.format(time()), 'w') as f:
        for item in game_logs:
            f.write("%s\n" % item)

    return round_count, winner, robot_move, human_move, move_delay, robot_rhythm, human_rhythm


def evaluate_winner(robot_move, human_move):
    if robot_move == human_move:
        return "Draw"
    elif (robot_move == "Rock" and human_move == "Paper") or (robot_move == "Paper" and human_move == "Scissor") or (robot_move == "Scissor" and human_move == "Rock"):
        return "Human"
    else:
        return "Robot"

if __name__ == "__main__":
    host_ip = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']
    host_port = 5000
    app.run(host_ip, host_port)