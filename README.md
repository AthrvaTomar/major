# Smart Home Control System

## Project Overview
This Smart Home Control System allows you to manage household devices (fan, lights, TV) through multiple interaction methods: manual control, hand gestures, and voice commands. The project integrates hardware (Arduino) with computer vision and speech recognition technologies to create an accessible and flexible home automation solution.

## Features
- **Multi-modal Control**: Control your home devices through:
  - Manual button interface
  - Hand gesture recognition (1-4 fingers)
  - Voice commands
- **Real-time Status Dashboard**: Monitor the current state of all connected devices
- **Visual Feedback**: Camera feed with gesture recognition visualization
- **Flexible Configuration**: Easy Arduino port configuration

## System Architecture
The system consists of three main components:

1. **Hardware Layer**: 
   - Arduino microcontroller connected to relays that control electrical devices
   - USB connection to the host computer

2. **Processing Layer**:
   - Computer vision for hand gesture recognition using MediaPipe
   - Speech recognition for voice commands using Google's speech-to-text API

3. **User Interface Layer**:
   - Streamlit web application providing an intuitive control panel
   - Real-time visual feedback and device status indicators

## Setup Instructions

### Hardware Requirements
- Arduino board (Uno/Nano/Mega)
- Relay module (5V) with at least 4 channels
- USB cable for Arduino-Computer connection
- Electrical devices to control (lights, fan, etc.)

### Arduino Setup
1. Connect the relay module to the Arduino:
   - Connect relay inputs to Arduino pins A0, A1, A3, A4, A5
   - Connect VCC to 5V and GND to ground
   - Connect devices to the relay outputs (NC or NO depending on your setup)

2. Upload the Arduino code (`arduino_code.ino`) to your Arduino board using the Arduino IDE

### Software Requirements
- Python 3.7+
- Required Python packages:
  - streamlit
  - opencv-python
  - mediapipe
  - pyserial
  - SpeechRecognition
  - numpy
  - pillow

### Software Installation
1. Clone this repository or download the source files

2. Install required Python packages:
```bash
pip install streamlit opencv-python mediapipe pyserial SpeechRecognition numpy pillow
```

3. Connect your Arduino to the computer via USB cable

### Running the Application
1. Open a terminal/command prompt in the project directory

2. Launch the Streamlit application:
```bash
streamlit run home_automation_portal.py
```

3. The web interface will open in your default browser

4. In the sidebar, enter the correct COM port for your Arduino and click "Connect to Arduino"

## Usage Guide

### Manual Control
The "Manual Control" tab allows you to toggle devices on and off with button clicks:
- Click the corresponding device button to turn it on/off
- The device status indicators show the current state of each device

### Gesture Control
The "Gesture Control" tab enables hand gesture recognition:
1. Click "Start Hand Gesture Control" to activate the camera
2. Show a specific number of fingers to control devices:
   - 1 finger: Toggle Fan
   - 2 fingers: Toggle Light 1
   - 3 fingers: Toggle Light 3
   - 4 fingers: Toggle Light 4
3. Hold the gesture steady for about 3 seconds for it to register
4. Click "Stop Hand Gesture Control" when done

### Voice Control
The "Voice Control" tab enables voice command recognition:
1. Click "Start Voice Control" to activate the microphone
2. Speak commands clearly:
   - "fan" to toggle the fan
   - "light one" to toggle Light 1
   - "light three" to toggle Light 3
   - "light four" to toggle Light 4
3. The status indicator will show recognized commands
4. Click "Stop Voice Control" when done

## Troubleshooting

### Arduino Connection Issues
- Verify the correct COM port is selected
- Check that no other application is using the same COM port
- Try disconnecting and reconnecting the Arduino
- Ensure the correct Arduino code is uploaded

### Gesture Recognition Issues
- Ensure good lighting conditions
- Position your hand clearly in the camera frame
- Make gestures clear and distinct
- Keep your hand at a moderate distance from the camera

### Voice Recognition Issues
- Speak clearly and at a moderate pace
- Reduce background noise
- Check that your microphone is properly connected and detected
- Try using exact phrase patterns as mentioned in the guide

## File Structure
```
smart-home-control/
├── arduino_code.ino          # Arduino control code
├── home_automation_portal.py # Main Streamlit application
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

## Technical Details

### Device Mapping
- Device 1: Fan (Arduino pin A0)
- Device 2: Light 1 (Arduino pin A1)
- Device 3: Light 3 (Arduino pin A3)
- Device 4: Light 4 (Arduino pin A4)
- Device 5: Buzzer (Arduino pin A5)

### Communication Protocol
The system uses a simple serial communication protocol between the Python application and Arduino:
- Single digit commands ('1', '2', '3', '4') to toggle the corresponding device
- Each command toggles the device state (ON/OFF)

### Hand Gesture Recognition
The system uses MediaPipe Hands to detect hand landmarks and implements a finger counting algorithm based on the position of fingertips relative to knuckles.

### Voice Recognition
Speech recognition is implemented using Google's speech-to-text API through the SpeechRecognition Python library.

## Future Enhancements
- Add scheduling capabilities for automated control
- Implement device grouping for scene-based control
- Add mobile app support
- Integrate with weather APIs for conditional automation
- Add user authentication for secure access
- Support for more complex gestures
- Integration with popular smart home platforms

## Credits
This project utilizes the following open-source libraries:
- [Streamlit](https://streamlit.io/) for the web interface
- [MediaPipe](https://mediapipe.dev/) for hand gesture recognition
- [OpenCV](https://opencv.org/) for computer vision processing
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) for voice command processing

## License
This project is licensed under the MIT License - see the LICENSE file for details.