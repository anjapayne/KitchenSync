#module converts mp4 to .npy (based on audio) and .dat to .npy (from RHD2000 channel)
import sys, os
import numpy as np
import scipy
from scipy.io import wavfile as wv
from scipy.io.wavfile import read 
import struct
import matplotlib.pyplot as plt

#extracts .wav from .mp4 and returns the file path 
def mp4_to_wav( mp4_path):
    output_path = os.path.splitext(mp4_path)[0] + ".wav"
    os.system("ffmpeg -i %s %s" % (mp4_path,  output_path))
    print('made it through mp4_to_wav')
    return output_path

#converts .wav file to .npy file
def wav_to_npy(wav_path):
    
    output_path = wav_path + ".npy"

    f = open(wav_path, 'r')
    a = read(wav_path) 
    wav = np.array(a[1],dtype=float) 
    #mono
    wav = wav.mean(axis = 1)  
    np.save(output_path, wav)

    return output_path

#waterfall
def mp4_to_npy( mp4_path):
    wav_path = mp4_to_wav(mp4_path)
    numpy_path = wav_to_npy(wav_path)
    return numpy_path
    
#RDH, assumes ADC input, for syncrony
def dat_to_npy( intan_path):
    output_path = intan_path + ".npy"
    file_size = os.path.getsize(intan_path)
    data_buffer = np.zeros(file_size / 2)

    with open(intan_path, 'r') as f:
        n = np.uint16(struct.unpack('H', f.read(2)))[0]   

        for i in range(len(data_buffer)):
           data_buffer[i] = n

    np.save(output_path, data_buffer)
    return output_path

#takes file path input, converts files down the line based in given file extension
def main( file_input):
    ext = os.path.splitext(file_input)[1]

    if ext == ".mp4":
        return np.load(mp4_to_npy(file_input))
    if ext == ".wav":
        return np.load(wav_to_npy(file_input))
    if ext == ".dat":
        return np.load(dat_to_npy(file_input))
    if ext == ".npy":
        return np.load(file_input) #returns the origonal input, no conversion needed

if __name__ == "__main__":
    filepath = sys.argv[1]
    main(filepath)
