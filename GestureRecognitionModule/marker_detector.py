import cv2
from cv2 import aruco

import requests
from time import time

REQUEST_ADDRESS = "http://192.168.86.178:5000/addRecognitionTimestamp?data={}_{}"

gesture_list = []
SAMPLE_COUNT = 5
gesture_idx = 0

ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_4X4_50)
ARUCO_PARAMS = aruco.DetectorParameters_create()

def track():
    cv2.startWindowThread()
    cap = cv2.VideoCapture(0)
    while True:
        frameTime = time()
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        detected_markers = []
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, ARUCO_DICT, parameters=ARUCO_PARAMS)
        print(ids)

        if ids is not None:
            for item in ids:
                detected_markers.append(item[0])
        
        if 46 in detected_markers:
            gesture = "Paper"
        elif 45 in detected_markers:
            gesture = "Scissor"
        elif 49 in detected_markers:
            gesture = "Rock"
        else:
            gesture = "NaN"
        
        gesture_list.append(gesture)
        if len(gesture_list) > SAMPLE_COUNT:
            gesture_list.pop(0)
        
        gesture = get_final_gesture()
        
        if gesture != "NaN":
            requests.get(REQUEST_ADDRESS.format(gesture, frameTime))

        frame = aruco.drawDetectedMarkers(frame, corners)
        
        frame = cv2.flip(frame, 1)

        cv2.putText(frame, "Gesture: " + gesture, (0,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

        cv2.imshow("RoPS Gesture Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

def get_final_gesture():
    global gesture_list

    rockCount = 0
    paperCount = 0
    scissorCount = 0
    nanCount = 0

    for g in gesture_list:
        if g == "Rock":
            rockCount += 1
        elif g == "Paper":
            paperCount += 1
        elif g == "Scissor":
            scissorCount += 1
        else:
            nanCount += 1
        
    if paperCount >= scissorCount and paperCount > nanCount:
        return "Paper"
    elif scissorCount > paperCount and scissorCount > nanCount:
        return "Scissor"
    elif nanCount >= paperCount and nanCount >= scissorCount and nanCount >= rockCount:
        return "NaN"
    else:
        return "Rock"

if __name__ == "__main__":
    track()

'''
2. Robot's Time Feedback
3. Link Controller Server to Robot Server
'''