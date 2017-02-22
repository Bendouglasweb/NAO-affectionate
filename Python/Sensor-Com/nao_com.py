from naoqi import ALProxy
import time

nao_ip = "192.168.1.137"
nao_port = "9559"

# Create connection to NAO Text To Speech center
tts = ALProxy("ALTextToSpeech", nao_ip, nao_port)

# Create connection to NAO movement center
motionProxy  = ALProxy("ALMotion", nao_ip, nao_port)

# Create connection to NAO posture center (e.g., sit down, stand up)
postureProxy = ALProxy("ALRobotPosture", nao_ip, nao_port)

# Set TTS parameters
tts.setParameter("speed", 75)
tts.setParameter("pitchShift", 1.1)

# Wake up robot
motionProxy.wakeUp()

# Make NAO speak
tts.say("Hi, I'm Lucky. Lucky the robot.")
time.sleep(2)
tts.say("You've finished this round!")
time.sleep(2)
tts.say("You still managed to hit 2 times!")
time.sleep(2)
tts.say("You did not hit any last round.")
time.sleep(2)

exit()

# Send robot to Stand Init
postureProxy.goToPosture("Stand", .8)

time.sleep(2)

# Go to rest position
motionProxy.rest()

