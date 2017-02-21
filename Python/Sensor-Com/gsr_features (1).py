import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import time
import sys

window_size = 50
inf_slope_thresh = 1.1
inf_avg_thresh = 1.1
peak_thresh = 1.2

# This function calculates and returns all features desired for gsr.
# The algorithmic process essentially is a window that steps through the signal, attempting to
# determine where phasic and tonic areas area. Once these are determined, calculating the
# features are simple math operatiions

# Window stepping details:
#   Step through data until and upwards infection point is found. This is defined as:
#       A) Slope of next window is at least X % larger than previous window slope
#       B) Average of window is larger than average of previous window
#   Once an inflection point is found, this point is defined as the beginning of a phasic area.
#   Continue iterating until a peak is found. A peak is defined as:
#
#   After the peak, continue iterating until a "3/4" drop point is found. This is when the
#   signal drops to 3/4 of the value of the amplitude of the peak.


fig, ax = plt.subplots()
line0, = ax.plot(np.zeros(2000))
line1, = ax.plot(np.zeros(2000))
line2, = ax.plot(np.zeros(2000))

ax.set_ylim(1200)
plt.gca().invert_yaxis()

plt.show(block=False)
fig.canvas.draw()

line0_data = []
f = open("Test_data.txt",'r')
for x in range(2000):
    line0_data.append(float(f.readline()))
f.close()

line1_data = []
for x in range(2000):
    line1_data.append(0)

line2_data = []
for x in range(2000):
    line2_data.append(0)




# GSR data input to this function is assumed to already be smoothed
def gsr_feature_extraction(gsr_data):
    gsr_peaks = []              # Stores locations of peaks
    zones = []                  # "overlay" array that deliniates phasic from tonic areas
                                #   0 = tonic; 1 = phasic

    step_size = int(np.floor(window_size/2))   # How much to move the window each time
    data_length = len(gsr_data)

    x_line = np.arange(1,window_size+1)

    # Assume tonic unless otherwise proven phasic
    for x in range(data_length):
        zones.append(0)

    pos = window_size
    prev_window = [0,0]         # Previois window [slope,average]
    cur_window = [0,0]          # Current window [slope,average]

    state = 0                   # "State" of the algorithm at the current window
                                #   0: in tonic area, searching for inflection point
                                #   1: after inflection, before peak
                                #   2: after peak, before end


    # Get first window values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_line,gsr_data[0:window_size])
    prev_window[0] = slope
    prev_window[1] = np.average(gsr_data[0:window_size])

    # Main loop. Breaks at end of data
    while True:

        # Get current window
        print "pos:",pos,". State:",state
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_line,gsr_data[
                                                                       pos:pos+window_size])

        cur_window[0] = slope
        cur_window[1] = np.average(gsr_data[pos:pos+window_size])

        #print prev_window," | ",cur_window

        if state == 0:
            # Check for inflection point
            if (cur_window[0] > prev_window[0]) and (cur_window[1] > prev_window[1]):
                state = 1
                tonic_info = [pos, gsr_data[pos]]
        elif state == 1:
            for x in range(window_size):
                line2_data[pos+x] = 100
            # Check for peak
            if (cur_window[0] < prev_window[0]) and (cur_window[1] < prev_window[1]):
                state = 2
                peak_info = [pos, gsr_data[pos]]
        elif state == 2:
            for x in range(window_size):
                line2_data[pos+x] = 100
            # Check for 3/4 drop
            if (cur_window[1] - tonic_info[1]) < (peak_info[1]-tonic_info[1]) * .25:
                state = 0

                if (peak_info[1]-tonic_info[0])/(tonic_info[0]) < peak_thresh:
                    for x in range(pos-tonic_info[0]):
                        line2_data[tonic_info[0]+x] = 0





        if state != 0:
            for x in range(window_size):
                zones[pos+x] = 1

        # Plotting
        for x in range(2000):
            line1_data[x] = 0
        line1_data[pos] = 1100
        line1_data[pos+1] = 0
        line1_data[pos+window_size] = 1100
        line1_data[pos+window_size+1] = 0

        line0.set_ydata(line0_data)
        line1.set_ydata(line1_data)
        line2.set_ydata(line2_data)
        ax.draw_artist(ax.patch)
        ax.draw_artist(line0)
        ax.draw_artist(line1)
        ax.draw_artist(line2)
        fig.canvas.draw()
        fig.canvas.flush_events()

        # End plotting

        pos += step_size
        prev_window[0] = cur_window[0]
        prev_window[1] = cur_window[1]

        time.sleep(0.5)

        sys.stdout.flush()

        if (pos+window_size) >= data_length:
            break




gsr_feature_extraction(line0_data)



