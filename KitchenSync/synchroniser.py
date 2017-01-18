import numpy as np
from template_match import *
from scipy.interpolate import interp1d

#uses interpolation to downsample or upsample to a new sample rate
def resample(array, old_sample_rate , new_sample_rate):
    
    interp = interp1d(np.arange(array.size), array) #throws error "total size of array must be unchanged"
    new_array_size = (float(array.size)/old_sample_rate) * new_sample_rate  
    new_array = np.linspace(0,array.size-1,new_array_size)
    print('new_array size is')
    print(len(new_array))
    new_array = interp(new_array)
    return new_array

class Synchroniser():
    """
    Uses the template match class to collect data for synchronising data sets. 
    calculates the true sampling rate ratios between datasets, and an array of time lags.  
    """

    def __init__(self, audio_data, intan_data , video_frame_count, intan_sample_rate = 20000, audio_sample_rate = 48000, intan_lower_bound = None, intan_upper_bound = None, template_lower_bound = None  ):
        print('intan lower bound is')
        print(intan_lower_bound)
        
        self.frame_count = video_frame_count
        if template_lower_bound == None:
            self.template_lower_bound = audio_data.size / 2
        self.audio_data = audio_data
        self.intan_data = intan_data
        self.template_size = audio_sample_rate * 30 #default 30 seconds
        self.video_frame_count = video_frame_count
        self.intan_sample_rate = intan_sample_rate
        self.audio_sample_rate = audio_sample_rate
        self.intan_lower_bound = intan_lower_bound
        self.intan_upper_bound =  intan_upper_bound
        self.template_lower_bound = template_lower_bound

    #calculates the true relative sampling frequncy between the video and data acquisition
    def calcFreq(self):

        print "Calculating Relative Sampling Frequencies"

        #create first template
        lower = self.template_lower_bound
        upper = self.template_lower_bound + self.template_size
        template = self.audio_data[lower:upper]

        #downsample to the approximate sample rate of the intan data
        print('downsampling to size of intan data')
        template = resample(template, self.audio_sample_rate, self.intan_sample_rate)
        print('resampled size is:')
        print (template.size)
        
        #find the position of the first template       
        tm = TemplateMatch(template, self.intan_data)
        time1 = tm.faster_find_template_match(self.intan_lower_bound, self.intan_upper_bound)

        #find last template, 3 template sizes later
        lower += self.template_size * 3
        upper = lower + self.template_size
        template = self.audio_data[lower:upper]

        print('downsampling again')
        template = resample(template, self.audio_sample_rate, self.intan_sample_rate) #this line throws error
        tm = TemplateMatch(template, self.intan_data)

        #find the position of the last template       
        time2 = tm.faster_find_template_match(self.intan_lower_bound + template.size * 3, self.intan_upper_bound + template.size * 3)
                
        #how far apart were they?
        delta_intan = float(time2 - time1)
        delta_audio = float(self.template_size*3)

        #audio frames per sample, delta_audio / delta_recording
        self.audio_fps =  delta_audio / delta_intan
        #video frames per sample
        self.video_fps = (float(self.video_frame_count) / self.audio_data.size) * self.audio_fps

        #audio to intan offset, used for future calculations
        self.offset = (self.template_lower_bound  * self.audio_fps**-1) - time1

        print "Video to Data Offset: ~" +  '%.2f' % (self.offset / self.intan_sample_rate) + " seconds"
        print "Framerate: ~" +  '%.2f' % (self.video_fps * self.intan_sample_rate) + " FPS"

    #offset calculated every n samples 
    def offset_list(self, n):

        print "downsampling audio to match data"
        self.downsampled_audio = resample(self.audio_data, self.audio_fps, 1)

        index_list = np.arange(0, self.intan_data.size, n)
        offset_list = [self.offset_at_sample(i) for i in index_list]

        # interpolate over the NaN data
        idx = np.flatnonzero(~np.isnan(offset_list))
        for i in range(0, idx[0]):
            offset_list[i]=offset_list[idx[0]]
        for i in range(idx[-1]+1, len(offset_list)):
            offset_list[i]=offset_list[idx[-1]]

        return np.repeat(offset_list, n)[:self.intan_data.size]

    #finds offset at intan sample n, based on the re-sampled audio data
    def offset_at_sample(self, n):   

        template_size = 30 * self.intan_sample_rate #using 30 second templates

        approx_start =  n + self.offset 

        #How far off might we be? (samples)
        max_error = 200

        #data subsample becomes template
        template = self.intan_data[n :n + template_size]
        #audio downsampeled to match template, using calculated framerate ratio
        static_data = self.downsampled_audio

        print "Calculating offset at sample " + str(n) + " of " +  str(static_data.size)

        #return null if there is inseficint data
        lower_bound = approx_start - max_error
        #No data to compair to at this point,
        if lower_bound < 0:
            return np.nan

        upper_bound = lower_bound + 2 * max_error
        if upper_bound > static_data.size:
            return np.nan

        tm = TemplateMatch(template, static_data)
        template_start =  tm.match_template_start(int(lower_bound), int(upper_bound))
        offset = n - template_start

        return offset 

    #video to frame index, offset calculated itterativly
    def BuildSyncIndex(self, reshift_interval):

        #run calculate_index to get initial offset and sample rate ratios
        self.calcFreq()

        #liner spaced index
        index = np.arange(0, self.intan_data.size)
        #add offset list 
        offsets = self.offset_list(reshift_interval)

        index = np.subtract(index, offsets)
        #multiply by video sampling rate relitive to intan sampling rate
        index = np.multiply(index, self.video_fps)

        return index
