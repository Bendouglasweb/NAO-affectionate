

from naoqi import ALProxy
import time
tts = ALProxy("ALTextToSpeech", "192.168.1.137", 9559)

motionProxy  = ALProxy("ALMotion", "192.168.1.137", 9559)
postureProxy = ALProxy("ALRobotPosture", "192.168.1.137", 9559)

# Wake up robot
motionProxy.wakeUp()

# Send robot to Stand Init
postureProxy.goToPosture("Stand", .8)

time.sleep(2)

# Go to rest position
motionProxy.rest()

# from time import gmtime, strftime
#
# for x in range(100):
#     tts.say(strftime("Look at me, I'm an absurdly expensive clock! It's %I %M %p"))
#     time.sleep(59)