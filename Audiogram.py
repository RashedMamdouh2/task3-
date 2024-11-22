import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile

class Audiogram:
    def __init__(self):
        pass
    def fourierTansformWave(self, audio=[], sampfreq=440010):
        try:
            audio = audio[:,0]
        except:
            audio = audio[:]
        #  Fourier transform 
        fourier_transform_magnitude = rfft(audio)
        fourier_transform_freq = rfftfreq(len(audio), 1 / sampfreq)
        fourier_transform_dB = 20 * np.log10(fourier_transform_magnitude + 1e-6)
    
        return fourier_transform_dB , fourier_transform_freq

    #  modify wave magnitude  
    def modify_wave (self, magnitude  , freq , start_index , end_index , new_magnitude  ) : 
        for i in range ( len(magnitude)):
            if  freq[i] >= start_index:
                if freq[i] < end_index:
                    freq[i] = new_magnitude

        return magnitude 

    # Select standard audiogram frequencies and get their indices in the Fourier transform result
    def get_audiogram_data(self, fourier_dB, fourier_freq):
        audiogram_frequencies = [250, 500, 1000, 2000, 4000, 8000]  # Standard audiogram frequencies
        audiogram_dB = []

        for freq in audiogram_frequencies:
            # Find the closest frequency in the Fourier transform
            idx = np.argmin(np.abs(fourier_freq - freq))
            audiogram_dB.append(fourier_dB[idx])
            

        return audiogram_frequencies, audiogram_dB
        
    def plotAudiogram(self, data, sampling_rate, canvas):
      
        # sampling_rate, data = wavfile.read('lion.wav')
       
        fourier_transform_magnitude , fourier_transform_freq = self.fourierTansformWave(audio=data , sampfreq=sampling_rate)

     
        audiogram_frequencies, left_ear  = self.get_audiogram_data(fourier_transform_magnitude, fourier_transform_freq)

        refrance = [250, 500, 1000, 2000, 4000, 8000 ]
        left_ref = [20, 20, 20, 35, 70 , 80 ]
        right_ref = [15, 20, 25, 40, 65, 75 ]

        # Plot the audiogram
        canvas.figure(figsize=(8, 6))

        # Plot thresholds for left and right ear
        canvas.plot(audiogram_frequencies, left_ear, 'x-', label="orignal signal", color='black')
        canvas.plot(refrance, left_ref, 'o-', label="Left Ear", color='blue')
        canvas.plot(refrance, right_ref, 's-', label="Right Ear", color='red')
        # Invert the y-axis (lower dB indicates better hearing)
        canvas.gca().invert_yaxis()

        # Labeling
        canvas.title("Audiogram")
        canvas.xlabel("Frequency (Hz)")
        canvas.ylabel("Hearing Threshold (dB HL)")
        canvas.xticks(audiogram_frequencies)  # Show only the test frequencies on the x-axis
        canvas.yticks(range(-10, 150, 10))  # Typical dB range for audiograms
        canvas.grid(True)
        canvas.legend()
        canvas.show()
