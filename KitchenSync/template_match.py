import numpy as np

class TemplateMatch():
    """
    Used to find the best locaion of a template along a static data set
    shifts a moving window along a static data set to maximise the pearson r-value
    between the window, and the template. 
    """

    silence_output = False #output progress?
    output_freq = 80000 #how often to output progress

    def __init__(self, template, static_data):
        self.template = template
        self.static_data = static_data

    #Returns the location of the beginning of template along the axis of the static data set
    def match_template_start(self, lower_bound = None, upper_bound = None, decimation = 1, template_decimation = 1):

        #the highest possable template location
        last_attempt = self.static_data.size - self.template.size

        #set default upper and lowe bound values of none
        if upper_bound == None:
            upper_bound = last_attempt
        else:
            upper_bound = min(last_attempt, upper_bound)
        if lower_bound == None:
            lower_bound = 0

        #everything less than the lower bound remains zero
        coeff_list = np.zeros(upper_bound)

        for i in range(lower_bound,  upper_bound ):

            #find the r-value at this point
            coeff_list[i] = self.template_corrcoeff(i, template_decimation)
            
            #print progress if approprate 
            if i % self.output_freq == 0 and not self.silence_output:
                print "Attempt " + str(i) + " Out of " + str(upper_bound) + " best r: " + str(np.max(coeff_list)) + " at " + str(np.argmax(coeff_list))
                  
        #return the argument of maximum correlation
        best_match = np.argmax(coeff_list)
        print "Best R: " + str(coeff_list[best_match])
        return best_match

    #retuns r-value between template and window beginning at start, decimates or returns 0 if approprate
    def template_corrcoeff(self, start, decimation = 1):    
        try:        
            return np.corrcoef(self.template[0::decimation], self.static_data[start:start+self.template.size][0::decimation])[0][1]
        except:
            return 0

    #speedy implementation of the above algorithm, using a 2-pass which downsamples the template and window on the first pass. 
    def faster_find_template_match(self, lower= None, upper=None):#i for itterations
        
        print "First Pass"#decimate temlate and window by 400
        latest_match = self.match_template_start(lower, upper,1,400)
        
        print "Second Pass:"#limit to with 100 samples of the latest match, do not decimate
        latest_match = self.match_template_start(latest_match - 100, latest_match +  100, 1, 1)

        return latest_match
