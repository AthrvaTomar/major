import speech_recognition as sr
import pyttsx3 
import time
import serial

# Initialize the recognizer 
r = sr.Recognizer() 

# Initialize the Arduino
arduino = serial.Serial('COM8', 9600)

# Loop infinitely for user to speak
while(1):    

    try:
        with sr.Microphone() as source2:
        
            """wait for a second to let the recognizer
            adjust the energy threshold based on
            the surrounding noise level"""
            r.adjust_for_ambient_noise(source2, duration=0.2)

            #listens for the user's input 
            print("Listening...\n")
            audio2 = r.listen(source2)

            # Using google to recognize audio
            MyText = r.recognize_google(audio2)
            MyText = MyText.lower()
            print(MyText)

            # Send input to arduino
            if(MyText == "111" or "222" or "333" or "444" or "close"):
                
                if(MyText == "111"):
                    arduino.write('1'.encode())
                    time.sleep(1)
                elif(MyText == "222"):
                    arduino.write('2'.encode())
                    time.sleep(1)
                elif(MyText == "333"):
                    arduino.write('3'.encode())
                    time.sleep(1)
                elif(MyText == "444"):
                    arduino.write('4'.encode())
                    time.sleep(1)
                elif(MyText == "close"):
                    arduino.close()
                    break

    except sr.UnknownValueError:
        print("Speak Again in ...")
        time.sleep(1)
        print("5")
        time.sleep(1)
        print("4")
        time.sleep(1)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1\n")