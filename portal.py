import streamlit as st
import cv2
import mediapipe as mp
import serial
import time
import speech_recognition as sr
import threading
import numpy as np
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Smart Home Control Portal",
    page_icon="🏠",
    layout="wide"
)

# Initialize MediaPipe Hand model
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Global variables
device_status = {
    "Fan": False,
    "Light 1": False,
    "Light 3": False, 
    "Light 4": False
}

# Function to establish serial connection
def connect_arduino(port):
    try:
        arduino = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Allow time for connection to establish
        return arduino
    except Exception as e:
        st.error(f"Error connecting to Arduino: {e}")
        return None

# Function to count fingers based on hand landmarks
def count_fingers(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]  # Landmark indices for fingertips
    finger_folded = []

    # Thumb logic
    if hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[2].x:
        finger_folded.append(False)  # Thumb is extended
    else:
        finger_folded.append(True)   # Thumb is folded

    # For the other four fingers
    for tip_index in finger_tips[1:]:
        if hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y:
            finger_folded.append(False)  # Finger is extended
        else:
            finger_folded.append(True)   # Finger is folded

    # Count extended fingers
    num_fingers = len([f for f in finger_folded if not f])
    return 0 if all(finger_folded) else num_fingers

# Function to process hand gestures
def process_hand_gestures(arduino):
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    cap = cv2.VideoCapture(0)
    last_sent_time = time.time()
    
    while st.session_state.hand_gesture_active:
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
                
                # Display finger count
                cv2.putText(img, f'Fingers: {finger_count}', (10, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Send command based on finger count
                current_time = time.time()
                if current_time - last_sent_time >= 3 and arduino is not None:
                    if 1 <= finger_count <= 4:
                        arduino.write(f'{finger_count}'.encode())
                        st.session_state.last_command = f"Sent command: {finger_count}"
                        
                        # Update device status
                        device_map = {1: "Fan", 2: "Light 1", 3: "Light 3", 4: "Light 4"}
                        if finger_count in device_map:
                            device = device_map[finger_count]
                            device_status[device] = not device_status[device]
                            
                    last_sent_time = current_time
        
        # Convert the image for display in Streamlit
        ret, buffer = cv2.imencode('.jpg', img)
        img_bytes = buffer.tobytes()
        
        # Update the image in session state to display in the UI
        st.session_state.camera_image = img_bytes
        
        time.sleep(0.1)  # Small delay to reduce CPU usage
    
    cap.release()

# Function to listen for voice commands
def listen_for_voice_commands(arduino):
    r = sr.Recognizer()
    
    while st.session_state.voice_control_active:
        try:
            with sr.Microphone() as source:
                st.session_state.voice_status = "Listening..."
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                
                try:
                    st.session_state.voice_status = "Processing..."
                    text = r.recognize_google(audio).lower()
                    st.session_state.voice_status = f"Recognized: {text}"
                    
                    # Map voice commands to device numbers
                    command_map = {
                        "fan": "1",
                        "light one": "2", 
                        "light 1": "2",
                        "light three": "3",
                        "light 3": "3", 
                        "light four": "4",
                        "light 4": "4"
                    }
                    
                    for key, value in command_map.items():
                        if key in text:
                            if arduino is not None:
                                arduino.write(value.encode())
                                
                                # Update device status
                                device_map = {"1": "Fan", "2": "Light 1", "3": "Light 3", "4": "Light 4"}
                                device = device_map[value]
                                device_status[device] = not device_status[device]
                                
                                st.session_state.last_command = f"Voice command: {key}"
                                time.sleep(1)
                                break
                
                except sr.UnknownValueError:
                    st.session_state.voice_status = "Sorry, I didn't catch that"
                except sr.RequestError:
                    st.session_state.voice_status = "Speech service unavailable"
        
        except Exception as e:
            st.session_state.voice_status = f"Error: {e}"
            time.sleep(1)
            
        time.sleep(0.1)

# Function to manually toggle devices
def toggle_device(arduino, device_num):
    if arduino is not None:
        arduino.write(f'{device_num}'.encode())
        
        # Update device status
        device_map = {1: "Fan", 2: "Light 1", 3: "Light 3", 4: "Light 4"}
        device = device_map[device_num]
        device_status[device] = not device_status[device]
        
        st.session_state.last_command = f"Manual toggle: {device}"
        time.sleep(1)

# Initialize session state variables
if 'arduino' not in st.session_state:
    st.session_state.arduino = None
if 'hand_gesture_active' not in st.session_state:
    st.session_state.hand_gesture_active = False
if 'voice_control_active' not in st.session_state:
    st.session_state.voice_control_active = False
if 'camera_image' not in st.session_state:
    st.session_state.camera_image = None
if 'voice_status' not in st.session_state:
    st.session_state.voice_status = "Voice control inactive"
if 'last_command' not in st.session_state:
    st.session_state.last_command = "No commands sent yet"

# Main UI components
st.title("🏠 Smart Home Control Portal")

# Sidebar for connection settings
with st.sidebar:
    st.header("Connection Settings")
    
    com_port = st.text_input("Arduino COM Port", "COM8")
    
    if st.button("Connect to Arduino"):
        st.session_state.arduino = connect_arduino(com_port)
        if st.session_state.arduino is not None:
            st.success("Successfully connected to Arduino!")
        
    if st.button("Disconnect Arduino"):
        if st.session_state.arduino is not None:
            st.session_state.arduino.close()
            st.session_state.arduino = None
            st.success("Arduino disconnected")
    
    st.subheader("System Status")
    st.write(f"Arduino: {'Connected' if st.session_state.arduino is not None else 'Disconnected'}")
    st.write(f"Hand Gesture Control: {'Active' if st.session_state.hand_gesture_active else 'Inactive'}")
    st.write(f"Voice Control: {'Active' if st.session_state.voice_control_active else 'Inactive'}")
    
    st.subheader("Last Action")
    st.write(st.session_state.last_command)

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["Manual Control", "Gesture Control", "Voice Control"])

# Tab 1: Manual Control
with tab1:
    st.header("Manual Device Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"{'Turn OFF' if device_status['Fan'] else 'Turn ON'} Fan", key="fan_toggle"):
            toggle_device(st.session_state.arduino, 1)
            
        if st.button(f"{'Turn OFF' if device_status['Light 1'] else 'Turn ON'} Light 1", key="light1_toggle"):
            toggle_device(st.session_state.arduino, 2)
    
    with col2:
        if st.button(f"{'Turn OFF' if device_status['Light 3'] else 'Turn ON'} Light 3", key="light3_toggle"):
            toggle_device(st.session_state.arduino, 3)
            
        if st.button(f"{'Turn OFF' if device_status['Light 4'] else 'Turn ON'} Light 4", key="light4_toggle"):
            toggle_device(st.session_state.arduino, 4)
    
    st.subheader("Device Status")
    status_cols = st.columns(4)
    
    for i, (device, status) in enumerate(device_status.items()):
        with status_cols[i]:
            st.metric(
                label=device,
                value="ON" if status else "OFF",
                delta="Active" if status else "Inactive",
                delta_color="normal"
            )

# Tab 2: Gesture Control
with tab2:
    st.header("Hand Gesture Control")
    st.write("Use hand gestures to control your devices")
    st.write("• Show 1 finger to toggle Fan")
    st.write("• Show 2 fingers to toggle Light 1")
    st.write("• Show 3 fingers to toggle Light 3")
    st.write("• Show 4 fingers to toggle Light 4")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.camera_image is not None:
            st.image(st.session_state.camera_image, channels="BGR", caption="Hand Gesture Camera Feed")
        else:
            st.write("Camera feed will appear here when enabled")
    
    with col2:
        if not st.session_state.hand_gesture_active:
            if st.button("Start Hand Gesture Control"):
                st.session_state.hand_gesture_active = True
                threading.Thread(target=process_hand_gestures, args=(st.session_state.arduino,), daemon=True).start()
        else:
            if st.button("Stop Hand Gesture Control"):
                st.session_state.hand_gesture_active = False

# Tab 3: Voice Control
with tab3:
    st.header("Voice Control")
    st.write("Use voice commands to control your devices")
    st.write("• Say 'fan' to toggle the fan")
    st.write("• Say 'light one' to toggle Light 1")
    st.write("• Say 'light three' to toggle Light 3")
    st.write("• Say 'light four' to toggle Light 4")
    
    st.subheader("Voice Recognition Status")
    st.info(st.session_state.voice_status)
    
    if not st.session_state.voice_control_active:
        if st.button("Start Voice Control"):
            st.session_state.voice_control_active = True
            threading.Thread(target=listen_for_voice_commands, args=(st.session_state.arduino,), daemon=True).start()
    else:
        if st.button("Stop Voice Control"):
            st.session_state.voice_control_active = False
            st.session_state.voice_status = "Voice control inactive"

# Footer
st.markdown("---")
st.caption("Smart Home Control Portal © 2025")