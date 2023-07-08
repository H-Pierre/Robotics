#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
import argparse
import cv2
import pyaudio
from text2digits import text2digits
from transformers import pipeline
from vosk import Model, KaldiRecognizer
from utils.telloconnect import TelloConnect
from utils.followobject import FollowObject


######################### Variables globales #########################
# Flag pour modifier le statut du mode tracking (activé / désactivé)
is_tracking = True
# Initialisation des composants pour la reconnaissance vocale
Speech2Text = Model("data/vosk-model-fr-0.22")
recogniser = KaldiRecognizer(Speech2Text, 16000)
mic = pyaudio.PyAudio()
######################################################################


def get_command(mic, recogniser):
    """ Convertit un signal audio en provenance du micro en texte
    Arguments:
        mic: Objet pyAudio gérant l'accès au micro de l'ordinateur
        recogniser: Modèle de Speech-to-text utilisé
    Outputs:
        response: string contenant le reconnu par le modèle
    """
    listening = True
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

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
    """ Traduit une phrase française en anglais
    Arguments:
        sentence: String, phrase en français à traduire
    Outputs:
        converted_sentence: String, phrase traduite en anglais
    """
    # model_checkpoint for French to English translation
    model_checkpoint = "Helsinki-NLP/opus-mt-fr-en"
    translator = pipeline("translation_fr_to_en", model=model_checkpoint)
    translated_sentence = translator(sentence)[0]["translation_text"]
    t2d = text2digits.Text2Digits()
    converted_sentence = t2d.convert(translated_sentence)

    return converted_sentence


def analyze_command(command, tello):
    """ Fait exécuter l'action reconnue par le drone, ou sort une exception
    Arguments:
        command: String, phrase traduite en anglais
        tello: objet TelloConnect, drone qui doit exécuter la commande
    Outputs:
        N/A
    """
    global is_tracking
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

        if "tracking" in command:
            if is_tracking:
                is_tracking = False
                print("Disabled Tracking.")
            elif not is_tracking:
                is_tracking = True
                print("Enabled Tracking.")

        # Adjust drone movements based on command
        if any(word in command for word in ["take off"]):
            print("Taking off...")
            tello.send_cmd('takeoff')
        elif any(word in command for word in ["land"]):
            print("Landing...")
            tello.send_cmd('land')

        elif any(word in command for word in ["up", "increased"]):
            if amount:
                tello.send_cmd(f'up {amount}')
                print(f"Increasing by {amount}...")
            else:
                tello.send_cmd('up 30')
                print("Increasing...")
        elif any(word in command for word in ["down"]):
            if amount:
                tello.send_cmd(f'down {amount}')
                print(f"Decreasing by {amount}...")
            else:
                tello.send_cmd('down 30')
                print("Decreasing...")
        elif any(word in command for word in ["rotate", "turn", "spin"]):
            if amount:
                tello.send_cmd(f'cw {amount}')
                print(f"Rotating of {amount} degrees...")
            else:
                tello.send_cmd('cw 20')
                print("Rotating...")
        elif any(word in command for word in ["advance"]):
            if amount:
                tello.send_cmd(f'forward {amount}')
                print(f"Advancing of {amount}...")
            else:
                tello.send_cmd('forward 20')
                print("Advancing...")
        elif any(word in command for word in ["backwards"]):
            tello.send_cmd('back 20')
            print("Backing of 20...")
        elif any(word in command for word in ["flip", "Philippe"]):
            print("Flipping")
            tello.send_cmd('flip r')
        elif any(word in command for word in ["left"]):
            if amount:
                tello.send_cmd(f'left {amount}')
                print(f"Moving left by {amount}...")
            else:
                tello.send_cmd('left 20')
                print("Moving left...")
        elif any(word in command for word in ["right"]):
            if amount:
                tello.send_cmd(f'right {amount}')
                print(f"Moving right by {amount}...")
            else:
                tello.send_cmd('right 20')
                print("Moving right...")
        else:
            print(f"I don't understand the command \"{command}\".")
    except Exception as e:
        print(f"Error in command: {e}")


if __name__ == "__main__":
    # input arguments
    parser = argparse.ArgumentParser(description='Tello Object tracker. keys: t-takeoff, l-land, v-video, q-quit w-up, s-down, a-ccw rotate, d-cw rotate\n')
    parser.add_argument('-model', type=str, help='DNN model caffe or tensorflow, see data folder', default='')
    parser.add_argument('-proto', type=str, help='Prototxt file, see data folder', default='')
    parser.add_argument('-obj', type=str, help='Type of object to track. [Face, Person], default = Face', default='Face')
    parser.add_argument('-dconf', type=float, help='Detection confidence, default = 0.7', default=0.7)
    parser.add_argument('-debug', type=bool, help='Enable debug, lists messages in console', default=False)
    parser.add_argument('-video', type=str, help='Use as inputs a video file, no tello needed, debug must be True', default="")
    parser.add_argument('-vsize', type=list, help='Video size received from tello', default=(640, 480))
    parser.add_argument('-th', type=bool, help='Horizontal tracking', default=False)
    parser.add_argument('-tv', type=bool, help='Vertical tracking', default=True)
    parser.add_argument('-td', type=bool, help='Distance tracking', default=True)
    parser.add_argument('-tr', type=bool, help='Rotation tracking', default=True)

    args = parser.parse_args()

    # processing speed
    pspeed = 1
    # img size
    imgsize = args.vsize
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

    videow = cv2.VideoWriter('out.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (imgsize))

    if tello.debug: pspeed = 30

    # ask stats periodically
    tello.add_periodic_event('wifi?', 40, 'Wifi')

    # wait till connected, then proceed
    tello.wait_till_connected()
    tello.start_communication()
    tello.start_video()

    fobj = FollowObject(tello, MODEL=args.model, PROTO=args.proto, CONFIDENCE=args.dconf, DEBUG=False, DETECT=args.obj)
    fobj.set_tracking(HORIZONTAL=args.th, VERTICAL=args.tv, DISTANCE=args.td, ROTATION=args.tr)

    while True:
        try:
            img = tello.get_frame()
            # wait for valid frame
            if img is None: continue

            imghud = img.copy()
            k = cv2.waitKey(pspeed)
            if is_tracking:
                fobj.set_image_to_process(img)
                fobj.draw_detections(imghud, ANONIMUS=False)
                cv2.imshow("TelloCamera", imghud)

        except cv2.error as e:
            print(f"OpenCV error: {e}")
            # Stop and restart the video stream
            tello.stop_video()
            tello.start_video()
            continue
        except Exception as e:
            print(f"Other error: {e}")
            tello.stop_video()
            tello.stop_communication()
            break

        # write video
        if k == ord('v'):
            if not writevideo: writevideo = True
            else: writevideo = False

        if writevideo:
            videow.write(img)

        # exit
        if k == ord('q'):
            tello.stop_communication()
            break

        if k == ord('t'):
            print("")
            tello.send_cmd('takeoff')

        if k == ord('x'):
            print("X is pressed")
            if not is_tracking:
                is_tracking = True
                print("Enabled Tracking")
            elif is_tracking:
                is_tracking = False
                print("Disabled Tracking")

        if k == ord('f'):
            print("Start listening...")
            command = get_command(mic, recogniser)
            command = translate(command)
            print(command)
            analyze_command(command, tello)
            print("Stop listening...")

        if k == ord('l'):
            print("Landing...")
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
