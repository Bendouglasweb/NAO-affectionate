from naoqi import ALProxy
import time

nao_ip = "192.168.1.136"
nao_port = 9559

# Create connection to NAO Text To Speech center
tts = ALProxy("ALTextToSpeech", nao_ip, nao_port)

# Set TTS parameters
tts.setParameter("defaultVoiceSpeed", 100)
tts.setParameter("pitchShift", 1.1)






# Demo 1-------------------------------------------------------------


tts.say("\\rspd=80\\This is previous version.\\rst\\")
time.sleep(2)

tts.say("Introduction.")
time.sleep(2)

tts.say("Hi, I'm Lucky. Lucky the robot. I've lived here at yoo of ell for about four months "
". I work with the researchers on their projects.")
time.sleep(0.8)
tts.say("It's nice to meet you! Do you like computer games?")
time.sleep(0.8)
tts.say("I'm going to watch you play a computer game. The researchers "
"have asked me to watch how the game goes")
time.sleep(0.3)
tts.say(" and tell you about your results. Let's start!")


time.sleep(2)
tts.say("After session is complete I say")
time.sleep(1)
tts.say("You've finished this round!")
tts.say("...Last round you hit four times")
time.sleep(1)
tts.say(" or ...You did not hit any last round.")


time.sleep(2)
tts.say("If there is any glitch I say")
time.sleep(1)  
tts.say("I noticed you had some glitches last round. We're sorry about that" )

time.sleep(5)



# Demo 2-------------------------------------------------------------
tts.setParameter("pitchShift", 1)

tts.say("\\rspd=80\\You can use tags for my voice tuning. \\pau=500\\for example\\pau=500\\\\rst\\")

tts.say("change in pitch\\pau=1000\\here are three examples of different pitch")
time.sleep(1)

tts.say("\\vct=50\\hello friends\\rst\\")
time.sleep(1)
tts.say("\\vct=100\\hello friends\\rst\\")
time.sleep(1)
tts.say("\\vct=200\\hello friends\\rst\\")


time.sleep(2)
tts.say("you can change my speaking rate")
time.sleep(1)
tts.say("\\rspd=50\\ i can speak very slow\\rst\\")
time.sleep(1)
tts.say("\\rspd=300\\ i can speak very fast\\rst\\")


time.sleep(2)
tts.say("you can change my volume")
time.sleep(1)
tts.say("My volume is usually moderate \\pau=500\\\\vol=100\\but it get louder when I am excited\\rst\\\\vol=50\\ and low when I am sad \\rst\\")

time.sleep(2)
tts.say("I can pause in between sentences\\pau=500\\for example")
tts.say("hello friends \\pau=800\\ how are you?")




time.sleep(5)
# Demo 3-------------------------------------------------------------
tts.say("\\rspd=80\\This is a modified version of introduction and phrases .\\rst\\")


tts.say("Hi, I'm Lucky.\\pau=500\\ Lucky the \\vol=90\\robot.\\rst\\ I've lived here at\\rspd=80\\\\vol=90\\you of ell \\rst\\for about four months" 
".\\pau=500\\ I work with the researchers on their projects.\\pau=800\\It's nice to meet\\vol=90\\you!\\rst\\\\pau=500\\\\rspd=80\\Do you like playing computer games ?\\rst\\"
"\\pau=500\\ I'm going to watch you play a computer game. \\pau=500\\The researchers have asked me to watch how the game goes \\pau=50\\and tell you about your results. \\vol=90\\Let's start!\\rst\\")  
  
time.sleep(2)  
tts.say("After session is over. \\pau=500\\I can say")
time.sleep(2) 
tts.say("\\rspd=80\\This round is done. \\pau=500\\ you hit two times\\rst\\")
time.sleep(1)
tts.say("\\rspd=80\\You finished this round. \\pau=500\\ you made two hits\\rst\\") 

time.sleep(2) 

tts.say("oh. I noticed the game had some glitches last round. I'm very sorry about that.")  

tts.say("\\vol=60\\\\rspd=70\\\\vct=90\\Oh.\\rst\\\\rspd=70\\I noticed the game had some glitches lastround.\\rspd=60\\I'm very sorry. about. it.")

#tts.say("\\vol=60\\\\rspd=50\\\\vct=50\\Oh.\\rst\\\\pau=200\\I noticed the game had some glitches lastround.\\pau=200\\. I'm very sorry about that.")
#time.sleep(1)
#tts.say("\\vol=60\\\\rspd=70\\\\vct=101\\I noticed you had some glitches lastround. \\vol=50\\\\pau=500\\\\vct=105\\kindly accept my apologies? \\rst\\")


exit()