###########################################
# Tello drone object tracker
# Author: fvilmos
###########################################

from utils.telloconnect import TelloConnect
from utils.followobject import FollowObject
import signal
import cv2
import argparse
import pyaudio
from text2digits import text2digits
from transformers import pipeline
from vosk import Model, KaldiRecognizer

def get_command(mic, recogniser):
    listening = True
    stream =  mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    
    while listening:
        stream.start_stream()
        try:
            data = stream.read(4096)
            if recogniser.AcceptWaveform(data):
                result = recogniser.Result()
                response = result[14:-3]
                listening = False
        except OSError:
            pass
        
    return response

def translate(sentence):
    # model_checkpoint for French to English translation
    model_checkpoint = "Helsinki-NLP/opus-mt-fr-en"

    translator = pipeline("translation_fr_to_en", model=model_checkpoint)
    
    translated_sentence = translator(sentence)[0]["translation_text"]

    t2d = text2digits.Text2Digits()
    converted_sentence = t2d.convert(translated_sentence)
    
    return converted_sentence

def analyze_command(command, tello):
    try:
        # Convert to lower case for consistency
        command = command.lower()

        # Extract number from command
        amount = [int(s) for s in command.split() if s.isdigit()]

        # Convert amount to centimeters if it exists
        if amount:
            amount = amount[0]
            if "meters" in command:
                amount *= 100
            elif "millimeters" in command:
                amount /= 10

        # Adjust drone movements based on command
        if "take off" in command:
            tello.send_cmd('takeoff')
        elif "land" in command:
            tello.send_cmd('land')
        elif "up" in command:
            if amount:
                tello.send_cmd(f'up {amount}')
            else:
                tello.send_cmd('up 30')
        elif "down" in command:
            if amount:
                tello.send_cmd(f'down {amount}')
            else:
                tello.send_cmd('down 30')
        elif "rotate clockwise" in command:
            if amount:
                tello.send_cmd(f'cw {amount}')
            else:
                tello.send_cmd('cw 20')
        elif "rotate counter-clockwise" in command:
            if amount:
                tello.send_cmd(f'ccw {amount}')
            else:
                tello.send_cmd('ccw 20')
        else:
            print(f"I don't understand the command \"{command}\".")
    except Exception as e:
        print(f"Error in command: {e}")

# Initialize speech recognition components
Speech2Text = Model("/Users/peterharfouche/Desktop/Telecom Paris/P4/Robotique/models/vosk-model-fr-0.22")
recogniser = KaldiRecognizer(Speech2Text, 16000)
mic = pyaudio.PyAudio()

if __name__=="__main__":
    # input arguments
    parser = argparse.ArgumentParser(description='Tello Object tracker. keys: t-takeoff, l-land, v-video, q-quit w-up, s-down, a-ccw rotate, d-cw rotate\n')
    parser.add_argument('-model', type=str, help='DNN model caffe or tensorflow, see data folder', default='')
    parser.add_argument('-proto', type=str, help='Prototxt file, see data folder', default='')
    parser.add_argument('-obj', type=str, help='Type of object to track. [Face, Person], default = Face', default='Face')
    parser.add_argument('-dconf', type=float, help='Detection confidence, default = 0.7', default=0.7)
    parser.add_argument('-debug', type=bool, help='Enable debug, lists messages in console', default=False)
    parser.add_argument('-video', type=str, help='Use as inputs a video file, no tello needed, debug must be True', default="")
    parser.add_argument('-vsize', type=list, help='Video size received from tello', default=(640,480))
    parser.add_argument('-th', type=bool, help='Horizontal tracking', default=False)
    parser.add_argument('-tv', type=bool, help='Vertical tracking', default=True)
    parser.add_argument('-td', type=bool, help='Distance tracking', default=True)
    parser.add_argument('-tr', type=bool, help='Rotation tracking', default=True)

    args = parser.parse_args()

    #processing speed
    pspeed = 1

    #img size
    imgsize=args.vsize

    # save video
    writevideo = False

    # signal handler
    def signal_handler(sig, frame):
        raise Exception

    # capture signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    if args.debug and args.video is not None:
        tello = TelloConnect(DEBUG=True, VIDEO_SOURCE=args.video)
    else:
        tello = TelloConnect(DEBUG=False)
    tello.set_image_size(imgsize)

    videow = cv2.VideoWriter('out.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 30, (imgsize))

    if tello.debug == True: pspeed = 30

    # ask stats periodically
    tello.add_periodic_event('wifi?',40,'Wifi')

    # wait till connected, than proceed
    tello.wait_till_connected()
    tello.start_communication()
    tello.start_video()

    fobj = FollowObject(tello, MODEL=args.model, PROTO=args.proto, CONFIDENCE=args.dconf, DEBUG=False, DETECT=args.obj)
    fobj.set_tracking( HORIZONTAL=args.th, VERTICAL=args.tv,DISTANCE=args.td, ROTATION=args.tr)

    while True:

        try:
            img = tello.get_frame()

            # wait for valid frame
            if img is None: continue

            imghud = img.copy()

            fobj.set_image_to_process(img)
            
            k = cv2.waitKey(pspeed)

            # Implement speech recognition
            #command = get_command(mic, recogniser)
            #command = translate(command)
            #analyze_command(command, tello)

        except Exception:
            tello.stop_video()
            tello.stop_communication()
            break

        fobj.draw_detections(imghud, ANONIMUS=False)
        cv2.imshow("TelloCamera",imghud)

        # write video
        if k ==ord('v'):
            if writevideo == False : writevideo = True
            else: writevideo = False

        if writevideo == True:
            videow.write(img)

        # exit
        if k == ord('q'):
            tello.stop_communication()
            break
        
        if k==ord('f'):
            print("Start listening...")
            command = get_command(mic, recogniser)
            command = translate(command)
            print("Stop listening...")

        if k == ord('t'):
            tello.send_cmd('takeoff')

        if k == ord('l'):
            tello.send_cmd('land')

        if k == ord('w'):
            tello.send_cmd('up 20')

        if k == ord('s'):
            tello.send_cmd('down 20')

        if k == ord('a'):
            tello.send_cmd('cw 20')

        if k == ord('d'):
            tello.send_cmd('ccw 20')

    cv2.destroyAllWindows()