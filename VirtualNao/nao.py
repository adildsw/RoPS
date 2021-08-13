from __future__ import division
from naoqi import ALProxy
import time
import motion
import random
import subprocess

server_ip = "http://192.168.86.178:5000/"
Nao_ip = "192.168.86.35"
PORT=9559

ROUNDS_PER_GAME= 5
human_wins=0
robot_wins=0
draw=0

rock_joint = [0,0]
paper_joint=[1,1.7]
scissor_joint=[1,-1]
rShoulderPitchJoints = [0.05,0.7] #shoulder pitch joint for pose A and B
rElbowRollJoints = [1.5,0.9] #elbow roll joint for pose A and B

# tts = ALProxy("ALTextToSpeech", Nao_ip, PORT)
# motionProxy = ALProxy("ALMotion", Nao_ip, PORT)
# postureProxy = ALProxy("ALRobotPosture", Nao_ip, PORT)

human_winning_phrase = ["You win.", " I lose", "Congrats, you win.", "You are the winner."]
robot_winning_phrase = ["Haha I win.","I win", "I am sorry, you lose.","Sorry you lose.", "I am the winner"]
draw_phrase = ["It's a draw.","Draw.","Too bad, it's a draw.","no one wins."]


bpm_faster_phrase = ["A little fast, slow down your rhythm.", "Your rhythm was a little fast."]
bpm_slower_phrase = ["Your rhythm is a little slow.", "speed up your rhythm a little."]

move_early_phrase = ["you serve your move early.", "You land your move early."]
move_late_phrase = ["you serve your move late.", "You land your move late."]
good_timing_phrase=["And your timing is perfect", "Good timing budy", "You get the timing right"]

game_user_win_phrase = ["Congratulation, You win this game.", "You are the winner. Congratulation", "Congratulation. But I will beat you next time."]
game_user_lose_phrase= ["I am sorry but you lose this game.", "I am the winner, beat me next time", "You lose, good luck next time."]

# randomly select 'rock','paper' and 'scissor' and return pre-defined joint data for corresponding choise
def getRandomChoice():
    choice = random.randint(0,2)
    # choice = 0
    if choice ==0:
        return "Rock", rock_joint
    elif choice == 1:
        return "Paper", paper_joint
    elif choice ==2:
        return "Scissor",scissor_joint


# Specified joint data and time series data for robot movement
# @param bps: rhythm speed in bps
# @param iteration: number of total beats 
def playEachRound(bpm,tts,motionProxy):
    names      = ["RShoulderPitch", "RElbowRoll", "RHand","RWristYaw"]

    choice, choiceJoint= getRandomChoice() #make random choice
    print (choice)

    pitch = rShoulderPitchJoints*3 
    roll = rElbowRollJoints*3  

    hand = [0,0,0,0,0]
    hand.append(choiceJoint[0]) #add choice joint
    wrist = [0,0,0,0,0]
    wrist.append(choiceJoint[1])
    angleLists = [pitch,roll,hand,wrist] #combine all joints data
  
    timePerBeat = 60/(bpm*2)
    startMove = 1 
    endMove = startMove+timePerBeat*6
    # timeList = np.arange(startMove, endMove, timePerBeat).tolist()[0:6]

    timeList = []
    t = startMove + timePerBeat
    while t<=endMove:
        timeList.append(t)
        t += timePerBeat

    times = [timeList,timeList,timeList,timeList]

    id=motionProxy.post.angleInterpolation(names, angleLists, times, True)
    motionProxy.wait(id,0)

    sendTimestamp(choice,tts)

def showSampleBeat(bpm,iteration,motionProxy,tts):
    names      = ["RShoulderPitch", "RElbowRoll"]
    angleLists = [rShoulderPitchJoints*iteration,rElbowRollJoints*iteration] #combine all joints data

    timePerBeat = 60/(bpm*2)
    startMove = 1 
    endMove = startMove+timePerBeat*iteration*2
    # timeList = np.arange(startMove, endMove, timePerBeat).tolist()[0:iteration*2]
    timeList = []
    t = startMove+timePerBeat
    while t<=endMove:
        timeList.append(t)
        t += timePerBeat

    times      = [timeList,timeList]

    id2 = motionProxy.post.angleInterpolation(names, angleLists, times, True)
    return id2


def sendTimestamp(action,tts):
    timestamp = time.time()
    # print(timestamp)
    # requests.get(server_ip + "addTimestamp?data=" + action + "_" + str(timestamp))
    res = req(server_ip + "addTimestamp?data=" + action + "_" + str(timestamp))
    print(res)
    winner = res.text.split("_")[0]
    move_delay = res.text.split("_")[1]
    bpm_difference = res.text.split("_")[2]
    valid = res.text.split("_")[3]

    print (res.text)
    sayFeedback(winner, move_delay, bpm_difference, valid,tts)
    # updateGameScore(winner)


# def updateGameScore(winner):
#     global human_wins, robot_wins, draw
#     if winner == "Robot":
#         robot_wins += 1
#     elif winner == "Human":
#         human_wins += 1
#     elif winner == "Draw":
#         draw += 1


def sayFeedback(winner, move_delay, bpm_difference, valid, tts):
    global human_wins, robot_wins, draw
    ## Valid round
        ## winner
    if winner == "Robot":
        robot_wins+=1
        tts.say(robot_winning_phrase[random.randint(0,len(robot_winning_phrase)-1)])
        say(robot_winning_phrase[random.randint(0,len(robot_winning_phrase)-1)])
    elif winner == "Human":
        human_wins += 1
        tts.say(human_winning_phrase[random.randint(0,len(human_winning_phrase)-1)])
        say(human_winning_phrase[random.randint(0,len(human_winning_phrase)-1)])
    elif winner == "Draw":
        draw += 1
        tts.say(draw_phrase[random.randint(0,len(draw_phrase)-1)])
        say(draw_phrase[random.randint(0,len(draw_phrase)-1)])
    time.sleep(0.5)

    if (valid == "Valid"):
        delay_check = False
        ## move delay
        if move_delay == "Early":
            tts.say(move_early_phrase[random.randint(0,len(move_early_phrase)-1)])
            say(move_early_phrase[random.randint(0,len(move_early_phrase)-1)])
            time.sleep(0.5)
        elif move_delay=="Late":
            tts.say(move_late_phrase[random.randint(0,len(move_late_phrase)-1)])
            say(move_late_phrase[random.randint(0,len(move_late_phrase)-1)])
            time.sleep(0.5)
        else:
            delay_check=True

        ## bpm difference 
        if bpm_difference == "Fast" and delay_check==True:
            tts.say(bpm_faster_phrase[random.randint(0,len(bpm_faster_phrase)-1)])
            say(bpm_faster_phrase[random.randint(0,len(bpm_faster_phrase)-1)])
            time.sleep(0.5)
        elif bpm_difference=="Slow" and delay_check==True:
            tts.say(bpm_slower_phrase[random.randint(0,len(bpm_slower_phrase)-1)])
            say(bpm_slower_phrase[random.randint(0,len(bpm_slower_phrase)-1)])
            time.sleep(0.5)

        # if (move_delay== "Good" and bpm_difference == "Good"):
        #     tts.say(good_timing_phrase[random.randint(0,len(good_timing_phrase)-1)])
        #     time.sleep(0.5)

    elif (valid == "Early"):
        tts.say("You landed your move way too early")
        say("You landed your move way too early")
    elif (valid == "Late"):
        tts.say("You landed your move way too late")
        say("You landed your move way too late")
    elif (valid == "Fast"):
        tts.say("Your rhythm is way too fast")
        say("Your rhythm is way too fast")
    elif (valid == "Slow"):
        tts.say("Your rhythm is way too slow")
        say("Your rhythm is way too slow")
    else:
        tts.say("Opps, I am receving craps")
        say("Opps, I am receving craps")

def startSample():
    tts = ALProxy("ALTextToSpeech")
    motionProxy = ALProxy("ALMotion")
    bpm = req(server_ip+"bpm")

    tts.say("Here is the sample beat")
    time.sleep(1.0)
    showSampleBeat(bpm=int(bpm),iteration=5,motionProxy=motionProxy,tts=tts)

def req(url):
    text = subprocess.check_output(["python", "request.py", url], shell=True)
    
    return text

def say(text):
    subprocess.call(["python", "tts.py", text], shell=True)

def main():
    tts = ALProxy("ALTextToSpeech")
    motionProxy = ALProxy("ALMotion")
    postureProxy = ALProxy("ALRobotPosture")

    #############################
    # Init posture
    motionProxy.wakeUp()
    postureProxy.goToPosture("Stand", 0.5)

    global human_wins, robot_wins, draw
    human_wins = 0
    robot_wins = 0
    draw = 0

    #############################
    # Greeting
    tts.say("Ready? ")
    say("Ready?")
    time.sleep(1.0)

    #############################
    # Game session starts
    # bpm = requests.get(server_ip+"bpm").text
    # print (bpm)
    bpm = req(server_ip+"bpm")

    for i in range(ROUNDS_PER_GAME):
        tts.say("Round" + str(i+1) + "start")
        playEachRound(bpm=int(bpm),tts=tts,motionProxy=motionProxy)
        time.sleep(1.0)
    
    tts.say("You won {} times, lost {} times, and the game was a draw {} times.".format(human_wins, robot_wins, draw))
    time.sleep(0.5)
    if (human_wins > robot_wins):
        tts.say(game_user_win_phrase[random.randint(0,len(game_user_win_phrase)-1)])
        say(game_user_win_phrase[random.randint(0,len(game_user_win_phrase)-1)])
    elif (robot_wins > human_wins):
        tts.say(game_user_lose_phrase[random.randint(0,len(game_user_lose_phrase)-1)])
        say(game_user_lose_phrase[random.randint(0,len(game_user_lose_phrase)-1)])
    else:
        tts.say("This game is a draw. ")
        say("This game is a draw. ")

def getSomeSnack():
    tts = ALProxy("ALTextToSpeech")
    tts.say("Amelia, Thank you so much for playing with me")
    say("Amelia, Thank you so much for playing with me")
    time.sleep(1)
    tts.say("Please get some snack!")
    say("Please get some snack!")


if __name__ == "__main__":
    main()
    getSomeSnack()