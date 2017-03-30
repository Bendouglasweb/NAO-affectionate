import zmq                          # ZeroMQ - Message Queuing platform
import matplotlib.pyplot as plt
import numpy as np
import thread
import atexit

import glob
import os
import time
from naoqi import ALProxy
import almath

from gsr_features import gen_features

# ---- Design discussion ----

# Why separate functions into multiple, concurrently running scripts?
#   Doing this allows for more parallel processing, as well as separation of duties. We also now can have the
#   functionality split between different machines

# How do the scripts talk to each other?
#   The way that we've chosen to handle this is with a messaging queue. The particular one that we're using is ZeroMQ.
#   This allows each script to send messages to each other that are handled and buffered by ZeroMQ.

# Why ZeroMQ?
#   ZeroMQ is a messaging queue that allows the decoupling of python scripts so each can, kind of,
#   run independently. This also somewhat makes them multithreaded (but each is still dependent on the other)
#   What ZeroMQ effectively does is create a broker between programs that carries messages between them.
#   In our case, "messages" are sets of data. The Bluegiga-Com.py script talks to the bluetooth dongle,
#   which receives data from the RFduino, and sends the data over ZeroMQ to this script.
#   This script then receives the data, replies that we received it, and processes the daa.
#   With the way that the ZeroMQ is setup, the scrips run in lock-step, as each script won't progress without
#   getting a response from the other one. This also means that the com script won't run without the graphing/processing
#   script to communicate with. As a design decision, this is fine because collecting data without having a place to
#   store it is useless.

# Why ZeroMQ over other solutions?
#   ZeroMQ is easy to use, very fast, and designed to be simple. ZeroMQ contained hooks for python and matlab.
#   These points meant that it fit our requirements. Otherwise, the choice was arbitrary.
#   ( Well, they're documentation is also awesome. Seriously, Have you read their manifesto? See:
#                                                                           http://zguide.zeromq.org/page:all#header-8

# ZeroMQ Documentation references:
#   This is a great quick start guide:
#       https://www.digitalocean.com/community/tutorials/how-to-work-with-the-zeromq-messaging-library
#   Here more complete documentation:
#       http://zguide.zeromq.org/page:all

# ---- End of discussion ----

# ---- Settings to change ----

# CHANGE THIS to NAO's IP addess
nao_ip = "192.168.1.136"    # NAO Robot IP Address
nao_port = 9559             # NAO Robot Port
nao_affectionate = 1        # 0 = non affectionate, 1 = affectionate

# Graph signals? 0 = off, 1 = on
enable_graphs = 1

#Skip over NAO functions (i.e., don't try to connect to NAO or run any nao functions)
skip_nao = 0               # 0 = Don't skip now, 1 = skip nao

num_data_points = 2000                      # Number of data points on the plot
collection_rate = 150                       # Hz of sensor data
start_feature_extraction_after = num_data_points/3
update_plot_every = num_data_points/10

# These set the amount of smoothing for each graph. The setting is in number of points to
# average together for a rolling average.
ppg_avg_amount = 10
gsr_avg_amount = 50
tmp_avg_amount = 10

# ---- End of changeable settings

# ZeroMQ Context. ZeroMQ is what handles communication from the python script that recieves
# information from the BlueGiga dongle. That is sent over ZeroMQ, and read by this script.
context = zmq.Context()

# ZeroMQ socket used for Bluegiga com
bg_sock = context.socket(zmq.REP)
bg_sock.bind("tcp://127.0.0.1:5678")           # This is the IP address and port.
bg_sock.RCVTIMEO = 3000            # Timeout for ZeroMQ of 3 seconds

# ZeroMQ socket used for Pong com
pong_sock = context.socket(zmq.REP)
pong_sock.bind("tcp://127.0.0.1:5679")          # This is the IP address and port.
pong_sock.RCVTIMEO = 100                        # Timeout for ZeroMQ

# ---- NAO Robot Elements ----
if skip_nao == 0:
    tts = ALProxy("ALTextToSpeech", nao_ip, nao_port)
    tts.setParameter("speed", 75)
    tts.setParameter("pitchShift", 1.1)

    motionProxy  = ALProxy("ALMotion", nao_ip, nao_port)
    postureProxy = ALProxy("ALRobotPosture", nao_ip, nao_port)
    faceProxy = ALProxy("ALFaceDetection", nao_ip, nao_port)
    tracker = ALProxy("ALTracker", nao_ip, nao_port)

# Simple wrapper function used for multi-threading
def nao_speak(message):
    # postureProxy.goToPosture("Crouch",0.3)
    nao_move("right")
    tts.say(message)
    nao_move("left")

def nao_speak_sorry(message):
    # postureProxy.goToPosture("Crouch",0.2)
    nao_move("bow")
    tts.setParameter("pitchShift", 1.0)
    tts.say(message)
    tts.setParameter("pitchShift", 1.1)
    # postureProxy.goToPosture("Crouch",0.2)
    nao_move("left")

def nao_move(action):
    motionProxy.setStiffnesses("Head", 1.0)
    # effectorName = "Head"
    #
    # # Active Head tracking
    # isEnabled    = True
    # motionProxy.wbEnableEffectorControl(effectorName, isEnabled)
    #
    # if action == "bow":     # Bow
    #     targetCoordinateList = [
    #     [ 00.0, +30.0,  00.0], # target 2
    #     ]
    # elif action == "left":   # Look Left
    #     tracker.stopTracker()
    #     targetCoordinateList = [
    #     [ 00.0, 00.0,  +35.0] # target 2
    #     ]
    # elif action == "right":   # Look Right
    #     targetCoordinateList = [
    #     [ 00.0, 00.0,  -35.0] # target 2
    #     ]
    #     tracker.registerTarget("Face", 0.1)
    #     tracker.track("Face")
    #
    # for targetCoordinate in targetCoordinateList:
    #     targetCoordinate = [target*np.pi/180.0 for target in targetCoordinate]
    #     motionProxy.wbSetEffectorControl(effectorName, targetCoordinate)
    #     time.sleep(2)
    #
    # # Deactivate Head tracking
    # isEnabled = False
    # motionProxy.wbEnableEffectorControl(effectorName, isEnabled)

    if action == "left":
        print("Moving head left")
        names      = ["HeadYaw"]
        angleLists = [30.0*almath.TO_RAD]
        timeLists  = [1.5]
        isAbsolute = True
        motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    elif action == "right":
        names      = ["HeadYaw"]
        angleLists = [-30.0*almath.TO_RAD]
        timeLists  = [1.5]
        isAbsolute = True
        motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    elif action == "bow":

        names      = ["HeadYaw"]
        angleLists = [0*almath.TO_RAD]
        timeLists  = [0.5]
        isAbsolute = True
        motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)

        names      = ["HeadPitch"]
        angleLists = [18.0*almath.TO_RAD]
        timeLists  = [1]
        isAbsolute = True
        motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)
        time.sleep(1.5)

        angleLists = [0*almath.TO_RAD]
        motionProxy.angleInterpolation(names, angleLists, timeLists, isAbsolute)



    motionProxy.setStiffnesses("Head", 0.0)

def nao_intro():
    nao_move("left")
    #motionProxy.wakeUp()
    #postureProxy.goToPosture("Sit",0.3)

    tts.say("Hi, I'm Lucky. Lucky the robot.")
    # tts.say("Hi, I'm Lucky. Lucky the robot. I've lived here at yoo of ell for about four months "
    #         ". I work with the researchers on their projects.")
    # time.sleep(0.8)
    # tts.say("It's nice to meet you! Do you like computer games?")
    # time.sleep(0.8)
    # tts.say("I'm going to watch you play a computer game. The researchers "
    #         "have asked me to watch how the game goes")
    # time.sleep(0.3)
    # tts.say(" and tell you about your results. Let's start!")




    # postureProxy.goToPosture("Crouch",0.3)
    # nao_move("left")

def on_program_exit():
    print("Exiting!")
    motionProxy.rest()


atexit.register(on_program_exit)

# ---- Calculated and declared variables

sample_period_ms = (1/collection_rate) * 1000   # Time between samples in milliseconds

seconds_on_graph = (num_data_points / collection_rate)

ppg_data_smooth = []                        # Smoothed PPG Data
gsr_data_smooth = []                        # Smoothed GSR Data
tmp_data_smooth = []                        # Smoothed TMP Data

# Window data for feature calculation
ppg_window_data = []
gsr_window_data = []
tmp_window_data = []

ppg_avg_array = []                          # Averaging array, used for rolling filter
gsr_avg_array = []                          # Averaging array, used for rolling filter
tmp_avg_array = []                          # Averaging array, used for rolling filter

livedatax = []                              # x-axis, just needed for plot. Never changes

count = 0                                   # Counts up for each data received.
                                            # Used for calculating when to update plot.

# Fill out smoothing arrays. These need to be pre-set to 0s.
for x in range(ppg_avg_amount):
    ppg_avg_array.append(0)

for x in range(gsr_avg_amount):
    gsr_avg_array.append(0)

for x in range(tmp_avg_amount):
    tmp_avg_array.append(0)

# Pre-fill data arrays. These also need to be pre-set to 0.
for x in range(num_data_points):
    ppg_data_smooth.append(0)                       # Fill data with 0s
    gsr_data_smooth.append(0)                       # Fill data with 0s
    tmp_data_smooth.append(0)                       # Fill data with 0s
    livedatax.append(x)                             # Make x-axis

if enable_graphs == 1:

    # Plotting variables.
    fig, (ax, ax1) = plt.subplots(2,sharex=True)                # A figure, which contains an axis.
    # fig, ax = plt.subplots()                                  A figure, which contains an axis.
    ppg_plotline, = ax.plot(np.random.randn(num_data_points))   # Each line is a plot
    gsr_plotline, = ax.plot(np.random.randn(num_data_points))
    tmp_plotline, = ax.plot(np.random.randn(num_data_points))

    ax.set_ylim([0,1100])
    ax1.set_ylim([-1,2])

    plt.gca().invert_yaxis()          # Invert axis so it is displayed how we visually expect it to be
    plt.show(block=False)             # Turn on graph
    fig.canvas.draw()                 # Show figure in graphing window

# Open file for saving data received
# We save our files in the format data_num.txt, where num increments with each recording
# We search through the directory to find the largest numbered file, then create a file one larger
files = glob.glob("./data/recorded_data/data_*")
file_max = 0
for item in files:
    num = int(filter(str.isdigit, item))
    if num > file_max:
        file_max = num

file_max += 1
data_filename = "data/recorded_data/data_" + str(file_max) + ".txt"
feature_filename = "data/recorded_data/feature_" + str(file_max) + ".txt"
data_f = open(data_filename, 'w+')
feature_f = open(feature_filename, 'w+')

# Log start time and formatting
start_time_formatted = time.strftime('%m-%d-%Y %H:%M:%S', time.localtime(time.time()))
data_f.write("Script started at: " + start_time_formatted + ". Data formatted as [PPG,GSR,TMP,"
                                                            "Trial Num,On Instructions]\n")
feature_f.write("Script started at: " + start_time_formatted + ". Data formatted as ")

# ---- Session and Java communication variables ----
# As it turns out, ZeroMQ and Java don't play very well together. Because of this, we're doing
# the not-so-great option of having the game write to a file every time it wants to say
# something. Java writes to a file named "java_status.txt" every time a window changes,
# this includes at the beginning of a session. The log file is overwritten every update,
# and thus always remains as a single line representing the current status. The single line is
# CSV information in this format:
#   1,2,3,4
#       1: Current window number
#       2: Previous window hits
#       3: Previous window misses
#       3: Previous window goal
#
# The Python script checks every so often, that being at least once a second, for an updated
# file and updates as necessary.

current_window = 0
java_filename = "java_state.txt"

# Remove previous trial file if it exists
try:
    os.remove(java_filename)
except:
    pass

print "Start of script."

if skip_nao == 0:
    nao_intro()

# tracker.registerTarget("Face", 0.1)
# tracker.track("Face")
#
# tracker.stopTracker()

time.sleep(2)
log = [0,0,0,0]
while True:
    count += 1
    # First, we attempt to receive data from the Bluegiga-Com script
    try:
        mq_message = bg_sock.recv()                           # Receive message from ZeroMQ socket
    except:
        print "No connection to Bluegiga script. " \
              "Please re/start that one; No need to restart this one."

    try:
        bg_sock.send("Rec")    # Reply that we have recieved that message. The text here is arbitrary.
    except:
        continue
    # Check for updates from Pong
    if count % 25 == 0:
        print("Java loop" + str(count))
        try:
            pong_msg = pong_sock.recv()
        except:

            continue

        try:
            pong_sock.send("Rec")   # Reply that we received the message. Text is arbitrary
            temp = pong_msg.split(",")
            log = []
            for item in temp:
                log.append(int(item))
            print(log)
        except:
            pass



        # pong_msg[0] = current window

        # Check to see if we moved windows
        if log[0] != current_window and log[0] != 0 and False:

            # Only do feature extraction if we have some data to work with
            if (len(ppg_window_data) > 100 and len(gsr_window_data) > 100 and len(
                    tmp_window_data) > 100):
                # Find features for previous window
                features = gen_features(ppg_window_data,gsr_window_data,tmp_window_data,
                                        collection_rate,sample_period_ms)
                # Write features to file
                for feat in features:
                    feature_f.write(str(feat) + ",")

                feature_f.write(str(current_window) + "\n")

            # Clear window arrays for data
            ppg_window_data = []
            gsr_window_data = []
            tmp_window_data = []

            current_window = log[0]
            print "Moved to new window, now on window #" + str(log[0])

            if skip_nao == 0:
                if log[4] == 1: # If glitches

                    if (nao_affectionate == 1):
                        nao_msg = "I noticed you had some glitches last round. We're sorry about" \
                        " that... "
                        if log[2] > 1:
                            nao_msg += "You still managed to hit " + str(log[2]) + " times!"
                        elif log[2] == 1:
                            nao_msg += "You still managed to hit " + str(log[2]) + " time!"
                        elif log[2] == 0:
                            nao_msg += "You did not hit any last round."

                        thread.start_new_thread(nao_speak_sorry,(nao_msg,))

                    else:
                        nao_msg = "You've finished this round!"
                        if log[2] > 1:
                            nao_msg += " ...Last round you hit " + str(log[2]) + " times!"
                        elif log[2] == 1:
                            nao_msg += " ...Last round you hit " + str(log[2]) + " time!"
                        elif log[2] == 0:
                            nao_msg += "You did not hit any last round."


                        thread.start_new_thread(nao_speak,(nao_msg,))

                else:
                    if log[0] == 1:
                        nao_msg = "Let's begin!"
                    else:
                        nao_msg = "You've finished this round!"
                        if log[2] > 1:
                            nao_msg += " ...Last round you hit " + str(log[2]) + " times!"
                        elif log[2] == 1:
                            nao_msg += " ...Last round you hit " + str(log[2]) + " time!"
                        elif log[2] == 0:
                            nao_msg += "You did not hit any last round."

                    thread.start_new_thread(nao_speak,(nao_msg,))




    # The ZeroMQ message comes in as a string. We expect this to be a series of 18 values, each
    # separated by a comma. This splits that string into a iterable python list so we can separate
    # it.
    # The data should be formatted at 18 chars/bytes, organized in 9 pairs.
    # Each value (PPG/GSR/TMP) is a pair of chars. 3 values * 2 bytes * 3 sets of data = 18 bytes.

    # Each value from the arduino is an integer value between 0 and 1023;
    # 1023 contains 10 bits, which takes two bytes to represent.
    # The RFduino can only send one byte at a time, so we have to split up the 2 byte sized
    # integers into single bytes, transmit them, then reconstruct them on this side.

    # Data is organized PPG,GSR,TMP,PPG,GSR,TMP,PPG,GSR,TMP
    data = mq_message.split(',')

    # Each message should contain three sets of data (each set = 1 PPG, 1 GSR, 1 TMP).
    # This separates and adds all data to appropriate locations
    for i in range(3):

        PPG = int(data[i*6  ])*256 + int(data[i*6+1])   # Reconstruct PPG to integer from two bytes
        GSR = int(data[i*6+2])*256 + int(data[i*6+3])   # " same with GSR
        TMP = int(data[i*6+4])*256 + int(data[i*6+5])   # " same with TMP

        # Write those values to a file
        data_f.write(str(PPG) + "," + str(GSR) + "," + str(TMP) + "," + str(current_window) +
                     "," + str(log[1]) + "\n")

        # Shift averaging arrays
        for x in range(ppg_avg_amount-1):
            ppg_avg_array[x] = ppg_avg_array[x+1]

        for x in range(gsr_avg_amount-1):
            gsr_avg_array[x] = gsr_avg_array[x+1]

        for x in range(ppg_avg_amount-1):
            ppg_avg_array[x] = ppg_avg_array[x+1]

        # Append new data to array
        ppg_avg_array[ppg_avg_amount-1] = PPG
        gsr_avg_array[gsr_avg_amount-1] = GSR
        tmp_avg_array[tmp_avg_amount-1] = TMP

        # Shift plotting arrays
        for x in range(num_data_points-1):
            ppg_data_smooth[x] = ppg_data_smooth[x+1]
            gsr_data_smooth[x] = gsr_data_smooth[x+1]
            tmp_data_smooth[x] = tmp_data_smooth[x+1]

        # Push new average onto plotting arrays
        ppg_data_smooth[num_data_points-1] = np.average(ppg_avg_array)
        gsr_data_smooth[num_data_points-1] = np.average(gsr_avg_array)
        tmp_data_smooth[num_data_points-1] = np.average(tmp_avg_array)

        # Append data into window arrays
        ppg_window_data.append(PPG)
        gsr_window_data.append(GSR)
        tmp_window_data.append(TMP)

    count += 1

    if (count % (collection_rate/3) == 0):
        # Make sure file data was flushed to disk once a second
        data_f.flush()
        feature_f.flush()

    if (count % 16) == 0:                    # Update the plot only every few data points

        if enable_graphs == 1:

            # We go through these weird steps of updating the plot
            # because they make matplotlib run faster.

            ppg_plotline.set_ydata(ppg_data_smooth)        # Update PPG data for plot
            gsr_plotline.set_ydata(gsr_data_smooth)        # Update GSR data for plot
            tmp_plotline.set_ydata(tmp_data_smooth)        # Update TMP data for plot

    #       line.set_xdata(livedatax)
            ax.draw_artist(ax.patch)
            ax.draw_artist(ppg_plotline)
            ax.draw_artist(gsr_plotline)
            ax.draw_artist(tmp_plotline)

            ax1.draw_artist(ax1.patch)

            fig.canvas.draw()
            fig.canvas.flush_events()

































# # ---- Generate GSR features ----
#
#             # The general strategy that we're aiming for is to separate the phasic areas from the
#             # non-phasic areas. To do this, we:
#             #   1) Identify peaks using peak detection algorithm
#             #   2) Filter out any peaks that don't show enough of a change
#             #       - This is to separate out noise and "false events"
#             #   3) For each peak, find its starting and ending area. We do this by:
#             #       - Starting our search a defined period to the left,
#             #       - Move to the right until a 'start' threshold is reached
#             #       - Continue moving until it drops below 'end' threshold
#             #   4) Generate a 0/1 array that labels each datapoint as either tonic or phasic
#             #   5) Calculate features
#
#
#             #               --- Visual Description of labels on a GSR signal ---
#             #
#             # |<--------(A) Left Window Search Area--------->|
#             # |<------(B) Left area to mean----------->|    *|*
#             # |                                        |  ** | **
#             # |                                        |**   |    **
#             # |                                       *|     |       **
#             # |                                       *|     |           **
#             # |                                      * |     |               **
#             # |                                      * |     |                  **
#             # |                                     *  |     |                      **
#             # |                                    *   |     |                         **
#             # |                                   *    |     |                            **
#             # |                                  *     |     |                               **
#             # |                                 *      |     |                                  **
#             # |                                *       |     |                                    **
#             # |                               *        |     |                                      **
#             # |                              *         |     |                                        **
#             # |                             *          |     |                                          **
#             # |                           *            |   Peak                                            **
#             # |                         *              |     |                                              **
#             # |                       *                |     |                                                **
#             # |                     *                  |     |-------- Phasic Threshold End --------------------**
#             # |                  *                     |     |                                                    **
#             # |               * ----Phasic Threshold Start---|                                                       ***
#             # |            *                           |     |
#             # |**********                              |     |
#             #
#             #
#             # A: This is a window from the peak to left_window_search number of samples to the left of that peak
#             # B: This is what percentage of that window, starting at the left, that we use to generate a mean.
#             #       - This mean is used for the filtering peaks. I.e., a peak must be peak_threshold greater than this
#             #       - mean to be considered.
#             #
#             #
#
#
#             left_window_search  = collection_rate*2     # Window to consider left of peak
#             peak_threshold = 0.2                        # Minimum % difference in peak from the mean to the left of peak
#             percent_of_left_for_tonic = 0.8             # Starting from the left side of the window to the left of the peak,
#                                                         # how much do we consider for the mean?
#             phasic_threshold_start = 1.2                # Threshold % to begin consideration of phasic area
#             phasic_threshold_end = 0.5                  # Threshold data needs to drop from peak
#
#             np_gsr_data = np.array(gsr_data_smooth)
#
#
#
#             # Get initial indexes of peaks
#             gsr_indexes = peakutils.indexes(np_gsr_data, min_dist=collection_rate/4)    # Find indexes
#
#             #gsr_indexes = signal.find_peaks_cwt(np_gsr_data,np.arange(1,50))
#
#             gsr_indexes_old = gsr_indexes[:]
#             gsr_indexes_temp = []
#
#             # First, apply a threshold to find "real" events; i.e., those that exceed a % increase threshold
#             # Peaks must be peak_threshold % greater than the mean to the left
#
#             for index in gsr_indexes:
#                 if index > left_window_search:     # We need enough data before it to analyze.
#                     start_mean = index-left_window_search
#
#                     end_mean = index - int(np.floor((left_window_search * (1-percent_of_left_for_tonic))))
#                     left_window_tonic_mean = np.mean(gsr_data_smooth[start_mean:end_mean])
#                     if ((gsr_data_smooth[index] - left_window_tonic_mean) / left_window_tonic_mean) > peak_threshold:
#                         gsr_indexes_temp.append(index)          # Okay, we'll consider it.
#
#             gsr_indexes = gsr_indexes_temp[:]       # Copy temp
#             gsr_indexes_temp = []                   # Clear temp
#
#             gsr_peaks = []
#
#             for x in gsr_indexes:
#                 gsr_peaks.append(gsr_data_smooth[x])
#
#
#             # Now we have the peaks; Identify Phasic and Tonic areas.
#
#             zone_labels = []                        # 0 = tonic; 1 = phasic
#             for x in range(num_data_points):
#                 zone_labels.append(0)
#
#             for index in gsr_indexes:
#                 # First get left window tonic mean
#                 start_mean = index - left_window_search
#                 end_mean = index - int(np.floor((left_window_search * (1-percent_of_left_for_tonic))))
#                 left_window_tonic_mean = np.mean(gsr_data_smooth[start_mean:end_mean])
#
#                 # We identify the phasic area by "sliding" through, checking for threshold conditions as we do it
#
#                 # Now find beginning of phasic area
#                 loc = index - left_window_search         # Starting location
#                 while (gsr_data_smooth[loc]) < (left_window_tonic_mean * phasic_threshold_start):
#                     loc += 1
#
#                 # Loc should now be positioned at the beginning of the phasic area.
#
#                 # Move to peak
#                 while (loc < index):
#                     zone_labels[loc] = 1
#                     loc += 1
#
#                 # Find end of phasic area
#                 while (gsr_data_smooth[loc] > (gsr_data_smooth[index] * phasic_threshold_end)):
#                     zone_labels[loc] = 1
#                     loc += 1
#                     if loc >= num_data_points:          # Reached end of data
#                         break
#
#             tonic_data = []
#             phasic_data = []
#             for i in range(num_data_points):
#                 if zone_labels[i] == 0:         # Tonic data
#                     tonic_data.append(gsr_data_smooth[i])
#                 else:                           # Phasic data
#                     phasic_data.append(gsr_data_smooth[i])
#
#             tonic_start = -1
#             tonic_end = -1
#             # Find start of tonic data for total slope
#             for i in range(num_data_points):
#                 if zone_labels[i] == 0:
#                     tonic_start = i
#                     break
#
#             # Find end of tonic data for total slope by searching from the end
#             for i in range(0,num_data_points,-1):
#                 if zone_labels[i] == 0:
#                     tonic_end = i
#                     break
#
#             temp_x = []
#             for i in range(len(tonic_data)):
#                 temp_x.append(i)
#
#             slope, intercept, r_value, p_value, std_err = stats.linregress(temp_x,tonic_data)
#
#             tonic_mean = slope
#             if (tonic_start != -1 and tonic_end != -1):
#                 tonic_slope = (gsr_data_smooth[tonic_end] - gsr_data_smooth[tonic_start]) / (tonic_end - tonic_start)
#             else:
#                 tonic_slope = 0
#             if (len(phasic_data) > 0):
#                 phasic_mean = np.mean(phasic_data)
#                 phasic_max = np.max(phasic_data)
#             else:
#                 phasic_mean = 0
#                 phasic_max = 0
#             phasic_rate = (len(gsr_indexes) / num_data_points) * (sample_period_ms / (1000 * 60))
#
#             feature_set.append(tonic_mean)              # TonicMean
#             feature_set.append(tonic_slope)             # TonicSlope
#             feature_set.append(phasic_mean)             # PhasicMean
#             feature_set.append(phasic_max)              # PhasicMax
#             feature_set.append(phasic_rate)             # PhasicRate
#
#             gsr_peak_graph = []
#             for x in range (num_data_points):
#                 gsr_peak_graph.append(0)
#             for x in gsr_indexes_old:
#                 gsr_peak_graph[x] = 1023
#
#             gsr_peak_graph_2 = []
#             for x in range (num_data_points):
#                 gsr_peak_graph_2.append(0)
#             for x in gsr_indexes:
#                 gsr_peak_g              