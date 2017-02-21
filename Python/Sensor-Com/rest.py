import sys
print sys.executable

from naoqi import ALProxy
nao_ip = "192.168.1.137"    # NAO Robot IP Address
nao_port = 9559             # NAO Robot Port
motionProxy  = ALProxy("ALMotion", nao_ip, nao_port)

motionProxy.rest()