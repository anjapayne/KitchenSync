#!/usr/bin/env python
import numpy as np
import sys, os
import DataConverter
import argparse
from synchroniser import Synchroniser
import argparse
import os.path
import wave

def main(audio_data, 
        science_data, 
        frame_count, 
        sample_rate, 
        audio_sample_rate, 
        approx_offset, 
        accuracy, 
        interval = 30):

    #seconds to samples
    approx_offset = approx_offset * sample_rate

    #add 20% to accuracy, for safety
    accuracy = accuracy + accuracy * .2
    #approximate end of video in sample rate
    approx_end = (audio_data.size * (float(sample_rate)/audio_sample_rate)) + approx_offset
    approx_start =  approx_offset
    template_lower_bound = audio_data.size / 2

    #approximate location of the middle point of the audio sample relative to the data acquisition recording 
    center_point = (approx_start + approx_end) / 2

    syncer =  Synchroniser(audio_data, 
        science_data , 
        frame_count,  
        sample_rate, 
        audio_sample_rate , 
        0, #AP added - I think this may be causing errors? 
        #int(center_point - (accuracy * sample_rate)),  Commented out 1.16.17 by AP due to errors being thrown
        int(center_point + (accuracy * sample_rate)), 
        int(template_lower_bound))

    reshift = sample_rate * interval
    print('reshift value is')
    print(reshift)
    
    return syncer.BuildSyncIndex(reshift_interval = sample_rate * interval)

#counts the frames of a video file, or uses the optional -vf argument
def FrameCount(): #I believe this isn't happening, I think it's producing 0. 

    if args['vf']:
        return int(args['vf'])

    #only works if cv2 bindings exist
    try:
        __import__("cv2")
    except ImportError:
        print """
cv2 bindings for python not installed.
Install openCv for python, 
or use the -vf argument to specify the total frame count of your video file.
        """        
        exit()

    if args['v']:
        #####################  This code needs to be replaced
        #####################  Will instead use ffprobe. 
        
        path_to_video = args['v']

        #used to count video frames in file 
        import cv2
        
        #get frame count
        cap =  cv2.VideoCapture(path_to_video)
        print('whats the path?')
        print(cap)
        halp = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        print('whats frame count yield?')
        print(halp)
        length = int(halp)
        print('whats the frame count')
        print(length)
        #return cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT) #this function in cv2 yields 0 
        return 11204        

    if args['b']:
        path_to_video = args['b'] + ".mp4"
        #used to count video frames in file 
        import cv2
        #get frame count
        cap =  cv2.VideoCapture(path_to_video)
        return cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)

    parser.epilog = "No video file specified."
    parser.print_help()
    exit()  

#finds the audio data, based upon the given parameters, and returns it as a numpy array
def audio():
    print "Loading audio Data"
    if args['a']: #use the audio file or numpy file if it exists
        return DataConverter.main(args['a'])
    if args['v']: #extract audio from video data
        return DataConverter.main(args['v'])
    if args['b']:
        npy = args['b'] + ".wav.npy"
        if os.path.isfile(npy):
            return DataConverter.main(npy)
        wav = args['b'] + ".wav"
        if os.path.isfile(wav):
            return DataConverter.main(wav)
    parser.epilog = "No audio file found."
    parser.print_help()
    exit()

#get audio frame rate
def aud_SR():
    base = ""
    if args['b']:
        base = args['b']
    elif args['a']:
        base = os.path.splitext(args['a'])[0]
    elif args['v']:
        base = os.path.splitext(args['v'])[0]
    #get the sample rate
    sr = wave.open(base + ".wav").getframerate()
    print "Audio sample rate (from metadata): " + str(sr)
    return sr 

#get data acquisition channel
def dataAq():
    print "Loading Data Acquisition Input"

    if args['d']: #use the audio file or numpy file if it exists
        return DataConverter.main(args['d'])
    if args['b']:
        npy = args['b'] + ".dat.npy"
        if os.path.isfile(npy):
            return DataConverter.main(npy)
        npy = args['b'] + ".npy"
        if os.path.isfile(npy):
            return DataConverter.main(npy)
        dat = args['b'] + ".dat"
        if os.path.isfile(dat):
            return DataConverter.main(dat)

    parser.epilog = "No data file found."
    parser.print_help()
    exit()

#decides where the output file belongs, and what it is called
def OutFilePath():
    name = ''
    path = ''
    
    if args['o']:
        return args['o']
    if args['d']:
        name = (args['d'].split("/")[-1]).split(".")[0]
        path = args['d'].replace(name, '').split('.')[0]
        return path + name
    if args['b']:
        return args['b']

    
args = {}#lib to hold arguments
parser = argparse.ArgumentParser(prog='main.py',
                                    description="""
Uses a template matching method to construct a sample-to-frame index based upon a common pulse recorded on the audio track of a video file, and on an analog chanel of a data acquisition system.
                                    """)

if __name__ == "__main__":
    parser.add_argument('-b', help='Base path of audio, video, and analog data files. Use  if these files share the same base file name.')
    parser.add_argument('-v', help='Path to the .mp4 video file')
    parser.add_argument('-a', help='Path to the .wav or .npy audio data file')
    parser.add_argument('-d', help='Path to the .npy or .dat analog input data file')
    parser.add_argument('-sr', help='Sampling rate of the analog data file')
    parser.add_argument('-vf', help='Frame count of video file')
    parser.add_argument('-guess', default=0,
                        help="""
Estimated start time difference between recording of video, and data aqusition, in seconds.
If the video was initialized first, this should be a negative number. 
Default: 0 seconds.
                        """)
    parser.add_argument('-conf', help="Confidence, in seconds, of your guess. Default: 30 seconds", default = 30)
    parser.add_argument('-si', help='Shift interval, determines, in seconds, how often the offset is recalculated. Default: 300 seconds', default = 300)
    parser.add_argument('-o', help='Base output file name, defaults to directory containing analog input file. Outputs as .npy and .txt')

    parser.add_argument('test', help='Shows a decimated plot of a subsample of synchronised audio track and analog input data, to confirm synchrony. Uses matplotlib')
    args = vars(parser.parse_args())
    
    aud = audio()#load audio array
    dat = dataAq()#load 
    fc = FrameCount()#video frames
    
    print('frame count is')    
    print(fc)

    afr = aud_SR()#audio frame rate
    if not args['sr']:
        parser.print_help()
        exit()
    sr = int(args['sr'])
    
    guess = int(args['guess'])
    conf = int(args['conf'])
    n = int(args['si']) #recalulation interval

    vIndex =  main(aud, 
                    dat, 
                    fc, 
                    sr, 
                    afr, 
                    guess, 
                    conf, 
                    n)
    
    aud_ind = np.linspace(0, fc, num = aud.size)
    
    base = OutFilePath()
    print "Saving " + base + ".index.npy"
    np.save(base + ".index.npy" , vIndex)
    print "Saving " + base + ".index.txt"
    np.savetxt(base + ".index.txt" , vIndex)
    print "Saving " + base + ".audio.txt"
    np.savetxt(base + ".audio.txt" , aud)
    print "Saving " + base + ".audio.index.txt"
    np.savetxt(base + ".audio.index.txt" , aud_ind)

    if args['test']:
        import matplotlib.pyplot as plt
        print "Plotting Audio Trace"
        plt.plot(aud_ind[0::100], aud[0::100] / np.max(aud), label='Audio Track (downsampled)')
        print "Plotting Synchronised Analog Data"
        plt.plot(vIndex[0::100], dat[0::100] / np.max(dat), label='Synchronised Analog Data (downsampled)')
        plt.xlim([fc / 2 , fc / 2 + 600])
        plt.ylim([-1.25, 1.25])
        plt.legend()
        plt.show()
