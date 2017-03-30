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

tts.say("Hi, I'm Lucky. Lucky the robot. I've lived here at yoo of ell for about four months "
        ". I work with the researchers on their projects.")
time.sleep(0.8)
tts.say("It's nice to meet you! Do you like computer games?")
time.sleep(0.8)
tts.say("I'm going to watch you play a computer game. The researchers "
        "have asked me to watch how the game goes")
time.sleep(0.3)
tts.say(" and tell you about your results. Let's start!")



