import sys
import numpy as np
import matplotlib.pyplot as plt

"""
This script can be used to test the validity of a generated sample to frame index by recording a pulsing LED as both a voltage (by and acquisition system) and as light (by a camcorder), while recording 
a synchrony signal as an audio on the camcorder, and as voltage on a separate channel of an acquisition system.

The LED brightness must be stored in a numpy array, using whatever software package will be used in the final analysis.
"""

#finds the onset of each pulse
def find_pulses(X):

    #detection threshold is 1.5 standard deviations
    thresh = 1.5 * np.std(X)

    #filtering
    X[np.where(X <  thresh)] = 0
    X[np.where(X >= thresh)] = 1

    #return index of pulse onsets 
    return np.where(np.diff(X) == 1)[0] + 1

def main(video, aqisition, index):

    print "detecting video pulses with threshold 1.5 x STD"
    video_pulses = find_pulses(video)
   
    print "detecting data aquisiton pulses with threshold 1.5 x STD"
    aq_pulses = index[find_pulses(aqisition)]

    #differences between detection times
    latency =  aq_pulses - video_pulses
    
    print "calculating correlation coeffeciant of aligned traces"
    R = r(video, aqisition, index)

    #latency mean and standard deviation
    u  = np.mean(latency)
    s = np.std(latency)

    #range
    rng = np.max(latency) - np.min(latency)

    print ""
    print ""
    print "     Stats:               "
    print "_______________________________________"
    print "Mean Latency :  " + str(u) + " (frames)"
    print "Latency STD  :  " + str(s) + " (frames)"
    print "Range        :  " + str(rng)
    print "Correlation  :  " + str(R)
    print ""
    print ""

    plt.suptitle("Pulse Detection Latency Historigram")
    plt.xlabel("Pulse Detection Latency (Video to Aquisition)")
    plt.ylabel("Frequency")
    plt.hist(latency)
    plt.show()

#find upsample correlation value
def r(video, aqisition, index):

    #upsample the video, interpolating using the index
    video = np.interp(index, np.arange(video.size), video)

    #return the corrcoef
    return np.corrcoef(aqisition, video)[0,1]
    
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "<path_to_video_data> <path_to_aqisition_data> <path_to_generated_index>"
        print "See help.txt for more info"

    #video trace
    print "Loading Video Data"
    v = np.load(sys.argv[1])

    #data aquisition trace
    print "Loading Aquisiton Data"
    d =  np.load(sys.argv[2])

    #generated index
    print "Loading Generated Index"
    i =  np.load(sys.argv[3]) + 8

    print ""
    main(v,d,i)
