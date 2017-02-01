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
    
#RDH, assumes ADC input, for synchrony
def dat_to_npy( intan_path):
    #TODO: Incorporate a means of determining whether the Intan analog data is 
    #more than one channel. If it is, choose the last channel and use that.
    
    
    output_path = intan_path + ".npy"
    file_size = os.path.getsize(intan_path)
    data_buffer = np.zeros(file_size / 2)

    #intan_path_size = sys.getsizeof(intan_path)
    #num_channels = 8
    #num_samples = intan_path_size/(num_channels * 2) #int16 = 2 bytes
    #start_index = num_samples * 7 
    #end_index = intan_path_size
    
    with open(intan_path, 'r') as f:
    #with open(intan_path, 'r') as fin: #added by AP 1.18.17
        #fin.seek(start_index) #added by AP 1.18.17
        #n = np.uint16(struct.unpack('H', f.read(2)))[0]
        #n = np.uint16(struct.unpack('H', fin.read(2)))[0] #added by AP 1.18.17
        #n = struct.unpack('H', f.read(2))   
        #d = np.array(n)
        #print('length of d is')
        #print(len(d))
        
        n = np.fromfile(f, dtype='uint16')
        print('size of n is')
        print(len(n))
        
        #for i in range(len(data_buffer)):
        #   data_buffer[i] = n
        #print('length of buffer is')
        #print(len(data_buffer))
    #np.save(output_path, data_buffer)
    np.save(output_path, n)

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
