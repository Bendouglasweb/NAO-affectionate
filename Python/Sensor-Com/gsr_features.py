import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import time
import sys
import peakutils

# Function calls all sub-functions and returns compiled result
def gen_features(ppg_data,gsr_data,tmp_data,collection_rate,sample_period_ms):
    ppg_peak_mean,ppg_peak_max,ibi_ppg_mean,ibi_ppg_sd = ppg_feature_extraction(ppg_data,
                                                                                collection_rate,
                                                                                sample_period_ms)

    tonic_mean, tonic_slope, phasic_mean, phasic_max, phasic_rate = gsr_feature_extraction(
                    gsr_data)

    tmp_mean,tmp_slope,tmp_sd = tmp_feature_extraction(tmp_data)

    feature_set = []
    feature_set.append(ppg_peak_mean)
    feature_set.append(ppg_peak_max)
    feature_set.append(ibi_ppg_mean)
    feature_set.append(ibi_ppg_sd)
    feature_set.append(tonic_mean)
    feature_set.append(tonic_slope)
    feature_set.append(phasic_mean)
    feature_set.append(phasic_max)
    feature_set.append(phasic_rate)
    feature_set.append(tmp_mean)
    feature_set.append(tmp_slope)
    feature_set.append(tmp_sd)

    return feature_set


# GSR data input to this function is assumed to already be smoothed
def gsr_feature_extraction(gsr_data):

    plots = 0       # 0 = off, 1 = on, 2 = test with no plots

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

    data_length = len(gsr_data)

    if plots == 1:
        fig, ax = plt.subplots()
        line0, = ax.plot(np.zeros(data_length))
        line1, = ax.plot(np.zeros(data_length))
        line2, = ax.plot(np.zeros(data_length))
        line3, = ax.plot(np.zeros(data_length))

        ax.set_ylim(1200)
        plt.gca().invert_yaxis()

        plt.show(block=False)
        fig.canvas.draw()

        line0_data = []
        f = open("Test_data3.txt",'r')
        for x in range(data_length):
            line0_data.append(float(f.readline()))
        f.close()

        line1_data = []
        for x in range(data_length):
            line1_data.append(0)

        line3_data = []
        for x in range(data_length):
            line3_data.append(0)

    elif plots == 2:
        line0_data = []
        f = open("Test_data4.txt",'r')
        for x in range(data_length):
            line0_data.append(float(f.readline()))
        f.close()





    gsr_peaks = []              # Stores locations of peaks
    zones = []                  # "overlay" array that deliniates phasic from tonic areas
                                #   0 = tonic; 1 = phasic
    phasic_peaks = []           # Store indexes of phasic peaks here

    step_size = int(np.floor(window_size/2))   # How much to move the window each time
    data_length = len(gsr_data)

    x_line = np.arange(1,window_size+1)

    line2_data = []
    for x in range(len(gsr_data)):
        line2_data.append(0)

    # Assume tonic unless otherwise proven phasic
    for x in range(data_length):
        zones.append(0)

    pos = window_size
    prev_window = [0,0]         # Previous window [slope,average]
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
        #print "pos:",pos,". State:",state
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_line,gsr_data[
                                                                       pos:pos+window_size])

        cur_window[0] = slope
        cur_window[1] = np.average(gsr_data[pos:pos+window_size])


        if state == 0:
            # Check for inflection point
            if (cur_window[0] > prev_window[0]) and (cur_window[1] > prev_window[1]):
                state = 1
                tonic_info = [pos+step_size, gsr_data[pos+step_size]]
                if plots == 1:
                    line3_data[pos+step_size] = 1200
        elif state == 1:
            for x in range(window_size):
                line2_data[pos+x] = 100
            # Check for peak
            if (cur_window[0] < prev_window[0]) and (cur_window[1] < prev_window[1]):
                # Found peak
                state = 2   # Change to post-peak stage

                # Find peak value in window
                np_argmax = np.argmax(gsr_data[pos:pos+window_size]) + pos
                peak_info = [np_argmax,gsr_data[np_argmax]]

                # Record to line2
                line2_data[peak_info[0]] = 1200
        elif state == 2:
            for x in range(window_size):
                if line2_data[pos+x] == 0:
                    line2_data[pos+x] = 100
            # Check for 3/4 drop
            np_argmax = np.argmax(gsr_data[pos:pos+window_size]) + pos
            #print "Max index is:",np_argmax
            if gsr_data[np_argmax] > peak_info[1]:
                #print "Old peak:",peak_info[0],",",peak_info[1],". New peak:",np_argmax,",",\
                    #gsr_data[np_argmax]
                # Found actual or new max
                line2_data[peak_info[0]] = 100
                line2_data[np_argmax] = 1200
                peak_info[0] = np_argmax
                peak_info[1] = gsr_data[np_argmax]

            if (cur_window[1] - tonic_info[1]) < (peak_info[1]-tonic_info[1]) * .25:
                state = 0
                if plots == 1:
                    line3_data[pos+window_size-1] = 1200
                #print (peak_info[1]-tonic_info[1])/(tonic_info[1])+1
                if (peak_info[1]-tonic_info[1])/(tonic_info[1])+1 < peak_thresh:
                    # Peak didn't mean threshold condition, clear data
                    for x in range(pos-tonic_info[0]+window_size):
                        line2_data[tonic_info[0]+x] = 0
                        if plots == 1:
                            line3_data[tonic_info[0]+x] = 0
                else:
                    # It's good! Add its peak to the register
                    phasic_peaks.append(peak_info[0])





        if state != 0:
            for x in range(window_size):
                zones[pos+x] = 1
        if plots == 1:
            # Plotting
            for x in range(2000):
                line1_data[x] = 0
            line1_data[pos] = 1100
            line1_data[pos+1] = 0
            line1_data[pos+window_size-2] = 1100
            line1_data[pos+window_size-1] = 0

            line0.set_ydata(line0_data)
            line1.set_ydata(line1_data)
            line2.set_ydata(line2_data)
            line3.set_ydata(line3_data)
            ax.draw_artist(ax.patch)
            ax.draw_artist(line0)
            ax.draw_artist(line1)
            ax.draw_artist(line2)
            ax.draw_artist(line3)
            fig.canvas.draw()
            fig.canvas.flush_events()

        # End plotting

        pos += step_size
        prev_window[0] = cur_window[0]
        prev_window[1] = cur_window[1]

        if plots == 1:
            time.sleep(0.20)

        sys.stdout.flush()

        # Break when the end of the data has been reached
        if (pos+step_size) >= data_length:

            if state in {1,2}:
                t_pos = tonic_info[0]
                while t_pos < data_length:
                    line2_data[t_pos] = 0
                    t_pos += 1
                if plots==1:
                    line3_data[tonic_info[0]] = 0

            if plots == 1:
                line2.set_ydata(line2_data)
                ax.draw_artist(line2)
                line3.set_ydata(line3_data)
                ax.draw_artist(line3)
                fig.canvas.draw()
                fig.canvas.flush_events()


            break

    # Data has been processed, zones mapped in line2_data.

    phasic_data = []
    tonic_data = []

    for j in range(data_length):
        if line2_data[j] > 0:
            phasic_data.append(gsr_data[j])
        else:
            tonic_data.append(gsr_data[j])

    if len(tonic_data) > 2:
        tonic_mean = np.mean(tonic_data)
        tonic_slope, intercept, r_value, p_value, std_err = \
            stats.linregress(np.arange(1,len(tonic_data)+1),tonic_data)
    else:
        tonic_mean = 0
        tonic_slope = 0

    if len(phasic_data) > 2:
        phasic_mean = np.mean(phasic_data)
        phasic_max = np.max(phasic_data)
    else:
        phasic_mean = 0
        phasic_max = 0

    if phasic_peaks > 0:
        phasic_rate = float(len(phasic_peaks)) / float(data_length)      # Peaks per data point.
    else:
        phasic_rate = 0


    return tonic_mean,tonic_slope,phasic_mean,phasic_max,phasic_rate

def ppg_feature_extraction(ppg_data,collection_rate,sample_period_ms):

    ppg_peaks = []           # Values of peaks
    ppg_distances = []       # Distances between those peaks

    # Copy ppg data into np array
    np_ppg_data = np.array(ppg_data)

    # Get PPG peaks
    ppg_indexes = peakutils.indexes(np_ppg_data, min_dist=collection_rate/3)

    for i in range(ppg_indexes.size):                        # From index, get actual peaks
        ppg_peaks.append(ppg_data[ppg_indexes[i]])
    for i in range(ppg_indexes.size - 1):               # Calc distance between those peaks
        dist = ppg_indexes[i+1] - ppg_indexes[i]
        ppg_distances.append(dist * sample_period_ms)

    if len(ppg_peaks) > 0:
        ppg_peak_mean = np.mean(ppg_peaks)
        ppg_peak_max = np.max(ppg_peaks)
    else:
        ppg_peak_mean = 0
        ppg_peak_max = 0
    if len(ppg_distances) > 0:
        ibi_ppg_mean = np.mean(ppg_distances)
        ibi_ppg_sd = np.std(ppg_distances)
    else:
        ibi_ppg_mean = 0
        ibi_ppg_sd = 0

    return ppg_peak_mean,ppg_peak_max,ibi_ppg_mean,ibi_ppg_sd

def tmp_feature_extraction(tmp_data):
    x_axis = []
    for x in range(len(tmp_data)):
        x_axis.append(x)

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_axis, tmp_data)

    tmp_mean = np.mean(tmp_data)
    tmp_slope = slope
    tmp_sd = np.std(tmp_data)

    return tmp_mean, tmp_slope, tmp_sd









