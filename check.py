from naoqi import ALProxy
import time
import almath

nao_ip = "192.168.1.136"
nao_port = 9559



# Create connection to NAO movement center
motionProxy  = ALProxy("ALMotion", nao_ip, nao_port)

# Create connection to NAO posture center (e.g., sit down, stand up)
postureProxy = ALProxy("ALRobotPosture", nao_ip, nao_port)




# Wake up robot
#motionProxy.wakeUp()

motionProxy.setStiffnesses("Head",1.0)

# names      = "HeadYaw"
# angleLists = -25.0*almath.TO_RAD
# timeLists  = 0.5
# isAbsolute = True

# motionProxy.angleInterpolation(names,angleLists,timeLists,isAbsolute)


# names      = "HeadYaw"
# angleLists = 25.0*almath.TO_RAD
# timeLists  = 1
# isAbsolute = True

# motionProxy.angleInterpolation(names,angleLists,timeLists,isAbsolute)


# names      = "HeadYaw"
# angleLists = 0.0*almath.TO_RAD
# timeLists  = 0.5
# isAbsolute = True

# motionProxy.angleInterpolation(names,angleLists,timeLists,isAbsolute)

# names      = "HeadPitch"
# angleLists = 30.0*almath.TO_RAD
# timeLists  = 0.5
# isAbsolute = True

# motionProxy.angleInterpolation(names,angleLists,timeLists,isAbsolute)

# time.sleep(5)


# names      = "HeadPitch"
# angleLists = 0.0*almath.TO_RAD
# timeLists  = 0.5
# isAbsolute = True

# motionProxy.angleInterpolation(names,angleLists,timeLists,isAbsolute)

# time.sleep(2)


#---------------------------------------------------------------------------
names      = ["HeadYaw"]
angleLists = [-30.0*almath.TO_RAD,0.0]
timeLists  = [0.5,1.0]
isAbsolute = True

motionProxy.angleInterpolation(names,angleLists,timeLists,isAbsolute)
#---------------------------------------------------------------------------

motionProxy.setStiffnesses("Head",0.0)

#motionProxy.rest()

exit()

# Send robot to Stand Init


