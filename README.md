------------
Kitchen Sync
------------

Kitchen Sync is a tool which takes advantage of a common signal recorded on both the audio track of a video file, and on an auxiliary input of a data acquisition system in order to generate a “sample to frame” index linking these two systems together. This allows data recorded on an electrphysiology data acquisition system to be synchronized with data recorded on a camcorder. 

Experiment Setup
----------------

Kitchen Sync uses a common signal recorded as sound (by the camcorder) and by voltage (by the data acquisition system) to generate a sample-to-frame index. Therefor, a signal must be generated, and recorded on moth systems simultaneously. 

Included in supplementary/Arduiono is Sync_Pulser, an Arduino Sketch who generates an audible structured, but random “tone” on an analog output pinof an Arduino controller. For more information on uploading Arduino programs, visit [Arduino.cc : first sketch.](http://arduino.cc/en/Tutorial/Sketch/)

Sync_Pulser will generate a synchrony signal on analog pin5 of your Arduino Micro-controller. This pin must be attached to both an auxiliary input on you at acquisition system, and the “Tip” and “Ring” of the audio input of the camcorder, via an modified microphone cable.  If possible, the auxiliary input, the sleeve of the microphone jack, and the Arduino should all share a common ground. See below of an example wiring diagram using an intan RHD200 evaluation board.

![Wiring Diagram][supplementary/Arduino/Arduino_Wiring_Diagram.tiff]

**During the experiment, be sure that you are recording from the axillary input channel, and the microphone input of the camcorder.**

Preparing Data
--------------

To generate a sample to frame index, Kitchen Sync needs a .MP4 video file with the synchrony signal recorded on the audio track, and a file containing the data from the auxiliary input channel which the synchrony signals was recorded on, as well as the sampling rate of data acquisition. The auxiliary data can be a “one file per signal type” (.dat) file, a flat binary file of 16 bit integers per channel. No bit-to-volt conversion is needed. Kitchen Sync will also accept “pickeled” numpy array files (.npy) containing the same data. If the audio is decoupled from the video file, you may pass in the audio as a .wav or .npy file. If the video file is not available, you may specify the total duration, in frames, of the video. 

Running Kitchen Sync
--------------------

Kitchen Sync can be ran from the directory containing KitchenSync.zip. The simplest way to run this program, assuming the video and auxiliary input data files share the same base filename (e.g. “trial1_exploration.MP4”,  “trial1_exploration.dat”) is like so: 

'$ python KitchenSync.zip -b  trial1_exploration -sr 20000'

where -sr 20000 denotes the sampling frequency of data acquisition. 
This will generate two files,  trial1_exploration.index.npy and  trial1_exploration.index.txt.

Optional Arguments
------------------

  test          Shows a decimated plot of a subsample of synchronized audio
                track and analog input data, to confirm synchrony. Uses
                matplotlib
  -h, --help    show this help message and exit
  -b B          Base path of audio, video, and analog data files. Use if these
                files share the same base file name.
  -v V          Path to the .mp4 video file
  -a A          Path to the .wav or .npy audio data file
  -d D          Path to the .npy or .dat analog input data file
  -sr SR        Sampling rate of the analog data file
  -vf VF        Frame count of video file
  -guess GUESS  Estimated start time difference between recording of video, and
                data acquisition, in seconds. If the video was initialized first,
                this should be a negative number. Default: 0 seconds.
  -conf CONF    Confidence, in seconds, of your guess. Default: 30 seconds
  -si SI        Shift interval, determines, in seconds, how often the offset
                is recalculated. Default: 300 seconds
  -o O    deo_index

This command uses  trial1.mp4 and  analog0.npy to generate trial1_video_index.npy and  trial1_video_index.txt. The delay between initializing data acquisition and video was assumed to be about 120 seconds, give or take 60 seconds. 

Example:
'$ python KitchenSync.zip -v trial1.mp4 -d analog0.npy -sr 15000 -guess 120 -conf 60 -o trial1_video_index'

This command uses  trial1.mp4 and  analog0.npy to generate trial1_video_index.npy and  trial1_video_index.txt. The delay between initializing data acquisition and video was assumed to be about 120 seconds, give or take 60 seconds. 

Usage of Generated Index
------------------------

The generated index file can be used to align samples along the timescale of a video file. Imaging “computer_vision” is a python module that can determine the linear position of an animal in a simple maze, and load in these positions as an array of values. Also, image that “eegReader” is a module that can load in eeg data from an acquisition file as an array of values. The following python script would use “trial1.index.npy” to align the EEG data to the data extracted from a video file:


'''python
    #usr/bin/bash/python

    import computer_vision
    import eegReader
    import numpy as np
    import matplotlib.pyplot as plt

    #loads a list of linear position values per frame
    ratPosition = computer_vision.getLinearPosition(“trial1.MP4”) 

    #loads in a single channel of EEG data as an array
    eeg = eegReader.read(“channel1.dat”)

    #loads in the sample to frame index
    index = np.load(“trial1.index.npy”)

    #plot the position data
    plt.plot(position)

    #plot the EEG data alongside the position data
    plt.plot(index, eeg)

    #show the figure
    plt.show()
'''

A Note on Accuracy
------------------

This algorithm synchronizes the data acquisition system along the time scale of the video file's audio track. The assumption is that the audio track is adequately synchronized to the video recorded, allowing us to place data acquisition samples along the timescale of the video. It is reasonable to expect consumer grade camcorders to have at least a “lip synchrony”  level of accuracy between the audio track and recorded video frames. However, those performing video analysis should take into account some of the general limitations of camcorder technology. 

One limitation in using low cost video equipment is the way CMOS senors typically found in digital camcorders record images. A single frame recoded by a CMOS sensor chip does not represent a single snapshot in time. Images are recorded by a “rolling shutter”, the sensor chip scans the image row-by-row (typically) or column-by-column.  Each scanline of pixels is exposed at different times. This is why fast moving objects are often skewed, or flashing lights are sometimes visible in only part of a video frame.  The rolling shutter effect is a well known issue, and is generally considered a compromise made by those who choose to record using CMOS image sensor cameras as apposed to more expensive CCD cameras. 

When recording objects who move or change rapidly, we do not expect to know precisely when an event occurred at any given part of the recorded frame. Without some mechanism of compensating for the rolling shutter, the best any method of synchrony can do is to align the recorded data along the timescale of the video file, similarly to how samples of an audio track are aligned along the time scale of recorded images in a movie. 

The extent of issues caused by the rolling shutter depends on a number of application specific factors, such as the frame rate, resolution, exposure time, the velocity of the subject, the nature of the video analysts performed, and the needed level of precision. This is a general, well know problem in the computer vision field, but should be noted whenever performing any video analysts. However, in most applications this should not be a major issue. 

Testing
-------

It is recommended that you test your hardware/software combination before conducting your experiment. You may perform whatever test you feel is appropriate. Included in the suplementary directory is Alingment_Tester, who's readme file provides a simple experiment that can be used to confirm that your software setup is able to achieve a reasonable level of alignment. 
