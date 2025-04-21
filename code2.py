import cv2
import mediapipe as mp
import serial
import time  # Import time module

# Initialize MediaPipe Hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Initialize Arduino serial communication
# Change the COM port accordingly
arduino = serial.Serial('COM8', 9600)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize a timer for sending data
last_sent_time = time.time()  # Store the current time

# Function to count fingers based on hand landmarks
def count_fingers(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]  # Landmark indices for fingertips
    finger_folded = []

    # Thumb logic (adjust for "thumbs up")
    if hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[2].x:
        finger_folded.append(False)  # Thumb is extended
    else:
        finger_folded.append(True)   # Thumb is folded

    # For the other four fingers (compare y-coordinates)
    for tip_index in finger_tips[1:]:
        if hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y:
            finger_folded.append(False)  # Finger is extended
        else:
            finger_folded.append(True)   # Finger is folded

    # Count how many fingers are extended
    num_fingers = len([f for f in finger_folded if not f])

    # If all fingers are folded, return 0
    if all(finger_folded):
        return 0

    return num_fingers

# Main loop for capturing video and processing hand gestures
while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Count fingers
            finger_count = count_fingers(hand_landmarks)
            

            # Get the current time
            current_time = time.time()

            # Check if 5 seconds have passed since the last data was sent
            if current_time - last_sent_time >= 3:
                # Send finger count to Arduino
                arduino.write(f'{finger_count}'.encode())
                
                print(finger_count)

                # Update the last sent time
                last_sent_time = current_time

            # Display the number of fingers detected
            cv2.putText(img, f'Fingers: {finger_count}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 255, 0), 2)

    cv2.imshow("Hand Gesture Detection", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
