import cv2
import mediapipe as mp
import pyautogui
import math
import time

# Initialize hand detection
cam = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils
screen_w, screen_h = pyautogui.size()


# Helper function to calculate distance between two points
def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


# Variables to control gestures
prev_x, prev_y = 0, 0
dragging = False
swipe_time = 0
pinch_time = 0
stop_time = 0

# Reduce frame processing load by skipping frames
frame_skip = 3
frame_count = 0

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Skip frames to reduce lag

    # Hand detection
    hand_output = hands.process(rgb_frame)
    frame_h, frame_w, _ = frame.shape

    if hand_output.multi_hand_landmarks:
        for hand_landmarks in hand_output.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

            # Extract key points for gestures
            index_finger_tip = hand_landmarks.landmark[8]
            middle_finger_tip = hand_landmarks.landmark[12]
            thumb_tip = hand_landmarks.landmark[4]
            pinky_tip = hand_landmarks.landmark[20]
            wrist = hand_landmarks.landmark[0]

            # Move cursor smoothly
            pyautogui.moveTo(index_finger_tip.x * screen_w, index_finger_tip.y * screen_h, duration=0.1)

            # Gesture 1: Select (index + middle finger)
            if (index_finger_tip.y < hand_landmarks.landmark[5].y and
                    middle_finger_tip.y < hand_landmarks.landmark[5].y):
                pyautogui.click()
                pyautogui.sleep(0.2)

            # Gesture 2: Pinch for Drag and Drop
            if time.time() - pinch_time > 1:  # Add debounce time for pinch
                pinch_distance = distance(index_finger_tip, thumb_tip)
                if pinch_distance < 0.05 and not dragging:
                    print("Pinch detected: Start dragging")
                    pyautogui.mouseDown()
                    dragging = True
                    pinch_time = time.time()
                elif pinch_distance > 0.1 and dragging:
                    print("Pinch released: Drop object")
                    pyautogui.mouseUp()
                    dragging = False
                    pinch_time = time.time()

            # Gesture 3: Swipe for Scroll
            if time.time() - swipe_time > 0.5:  # Add debounce for swipe
                if prev_x != 0 and prev_y != 0:
                    delta_x = wrist.x - prev_x
                    delta_y = wrist.y - prev_y

                    if abs(delta_x) > 0.05:  # Swipe left or right
                        if delta_x > 0:
                            print("Swipe Right: Next Tab")
                            pyautogui.hotkey('ctrl', 'tab')
                        else:
                            print("Swipe Left: Previous Tab")
                            pyautogui.hotkey('ctrl', 'shift', 'tab')
                        swipe_time = time.time()

                    if abs(delta_y) > 0.05:  # Swipe up or down
                        if delta_y > 0:
                            print("Swipe Down: Scroll Down")
                            pyautogui.scroll(-50)
                        else:
                            print("Swipe Up: Scroll Up")
                            pyautogui.scroll(50)
                        swipe_time = time.time()

                prev_x, prev_y = wrist.x, wrist.y

            # Gesture 4: Stop Program (all fingers extended)
            if time.time() - stop_time > 1:  # Add debounce for stop gesture
                if (index_finger_tip.y < hand_landmarks.landmark[5].y and
                        middle_finger_tip.y < hand_landmarks.landmark[5].y and
                        thumb_tip.y < hand_landmarks.landmark[5].y and
                        pinky_tip.y < hand_landmarks.landmark[5].y):
                    print("All fingers raised, stopping the program.")
                    cam.release()
                    cv2.destroyAllWindows()
                    exit()
                stop_time = time.time()

    # Display frame
    cv2.imshow('Hand Gesture Mouse Control', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cam.release()
cv2.destroyAllWindows()

