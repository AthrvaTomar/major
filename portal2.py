import streamlit as st
import serial
import time

# Page configuration
st.set_page_config(
    page_title="Smart Home Control Portal",
    page_icon="💡",
    layout="wide"
)

# Function to establish serial connection
def connect_arduino(port):
    try:
        arduino = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Allow time for connection to establish
        return arduino
    except Exception as e:
        st.error(f"Error connecting to Arduino: {e}")
        return None

# Function to manually toggle devices
def toggle_device(arduino, device_num):
    if arduino is not None:
        arduino.write(f'{device_num}'.encode())
        
        # Update device status
        device_map = {1: "Living Room Light", 2: "Bedroom Light", 3: "Kitchen Light", 4: "Bathroom Light"}
        device = device_map[device_num]
        st.session_state.device_status[device] = not st.session_state.device_status[device]
        
        st.session_state.last_command = f"Manual toggle: {device}"
        time.sleep(1)

# Initialize session state variables
if 'arduino' not in st.session_state:
    st.session_state.arduino = None
if 'last_command' not in st.session_state:
    st.session_state.last_command = "No commands sent yet"
if 'device_status' not in st.session_state:
    st.session_state.device_status = {
        "Living Room Light": False,
        "Bedroom Light": False,
        "Kitchen Light": False,
        "Bathroom Light": False
    }

# Main UI components
st.title("💡 Smart Home Lighting Control")

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
    
    st.subheader("Last Action")
    st.write(st.session_state.get('last_command', "No commands sent yet"))

# Manual Control Section
st.header("Light Control")

col1, col2 = st.columns(2)

with col1:
    if st.button(f"{'Turn OFF' if st.session_state.device_status['Living Room Light'] else 'Turn ON'} Living Room Light", key="livingroom_toggle"):
        toggle_device(st.session_state.arduino, 1)
        
    if st.button(f"{'Turn OFF' if st.session_state.device_status['Bedroom Light'] else 'Turn ON'} Bedroom Light", key="bedroom_toggle"):
        toggle_device(st.session_state.arduino, 2)

with col2:
    if st.button(f"{'Turn OFF' if st.session_state.device_status['Kitchen Light'] else 'Turn ON'} Kitchen Light", key="kitchen_toggle"):
        toggle_device(st.session_state.arduino, 3)
        
    if st.button(f"{'Turn OFF' if st.session_state.device_status['Bathroom Light'] else 'Turn ON'} Bathroom Light", key="bathroom_toggle"):
        toggle_device(st.session_state.arduino, 4)
        

st.subheader("Light Status")
status_cols = st.columns(4)

for i, (device, status) in enumerate(st.session_state.device_status.items()):
    with status_cols[i]:
        st.metric(
            label=device,
            value="ON" if status else "OFF"
        )

# Footer
st.markdown("---")
st.caption("Smart Home Lighting Control © 2025")