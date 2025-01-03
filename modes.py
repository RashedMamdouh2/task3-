import numpy as np
from PyQt5.QtWidgets import QSlider, QLabel, QVBoxLayout,QGridLayout
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import Qt
from scipy.signal import spectrogram


class modes:
    def __init__(self, signal, band_edges,window):

        if signal is not None:
            self.time = signal.time_data
            self.original_signal_magnitude = signal.amplitude_data
        self.sampling_rate = 2000  # Hz
        self.window=window

        self.reconstructed_signal = None

        self.gain = None
        self.band_edges = list(band_edges.values())

    def slider_creator(self, range_of_slider, mode_name="Uniform Mode"):
        number_of_slider = 10 if mode_name == "Uniform Mode" else 4
        band_layout = QGridLayout()
        self.gain = [1] * number_of_slider

        for i in range(number_of_slider):
            slider = QSlider(Qt.Vertical)
            slider.setMaximumSize(QtCore.QSize(16777215, 150))
            slider.setOrientation(QtCore.Qt.Vertical)
            slider.setMinimum(1)
            slider.setMaximum(100)
            slider.setValue(50)

            slider.valueChanged.connect(lambda value, idx=i: self.apply_gain(value, idx))


            label = QLabel(f"Band {i + 1}")
            # label.setAlignment(Qt.AlignCenter)

            label.setMaximumSize(QtCore.QSize(16777215, 20))
            label.setObjectName("slider_1_label")


            band_layout.addWidget(label,3,i,1,1)
            band_layout.addWidget(slider,2,i,1,1)
        return band_layout

    def compute_fft(self):
        fft_result, frequencies =np.fft.fft(self.original_signal_magnitude), np.fft.fftfreq(len(self.original_signal_magnitude),d=1 / self.sampling_rate)
        positive_freqs = frequencies[:len(frequencies) // 2]
        magnitude=np.abs(fft_result)
        positive_magnitude = magnitude[:len(magnitude) // 2]
        signal=[positive_freqs,positive_magnitude]
        self.window.frequencyDomainPlot.add_signal(signal,start=False,color='r')

        return positive_magnitude, positive_freqs


    def apply_gain(self,slider_value,slider_idx):
        slider_value = slider_value / 50
        fft_result, frequencies = self.compute_fft()
        modified_fft = fft_result.copy()
        # f_max = self.sampling_rate / 2
        low, high = self.band_edges[slider_idx][0],self.band_edges[slider_idx][1]
        band_mask = (abs(frequencies) >= low) & (abs(frequencies) < high)
        self.gain[slider_idx]= slider_value
        modified_fft[band_mask] *= slider_value
        self.reconstruct_signal(modified_fft,frequencies)


    def reconstruct_signal(self, modified_fft,frequencies):
        if self.original_signal_magnitude is None:
            return

        self.reconstructed_signal = np.fft.ifft(modified_fft).real
        self.window.equalizedGraph.reconstruct_signal_on_equalized_plot(self.reconstructed_signal)
        # self.window.equalizedGraph.add_signal(np.array([self.time, self.reconstructed_signal]))

        positive_freqs = frequencies[:len(frequencies) // 2]
        magnitude = np.abs(modified_fft)
        positive_magnitude = magnitude[:len(magnitude) // 2]
        signal = [positive_freqs, positive_magnitude]
        self.window.frequencyDomainPlot.remove_old_curve()#old ui
        self.window.frequencyDomainPlot.add_signal(signal=signal,start=False,color='r')#old ui


                             
    def plot_spectrogram(self, signal, canvas):
        """
        Plot spectrogram using Matplotlib.
        """
        f, t, Sxx = spectrogram(signal, fs=self.sampling_rate, nperseg=128, noverlap=64)
        Sxx_db = 10 * np.log10(Sxx + 1e-10)  # Add small value to avoid log(0)

        if canvas.no_label:
            canvas.no_label = False
            canvas.vmin, canvas.vmax = np.min(Sxx_db), np.max(Sxx_db)

        canvas.axes.clear()
        cax = canvas.axes.pcolormesh(t, f, Sxx_db, shading='gouraud', cmap='plasma', vmin=canvas.vmin, vmax=canvas.vmax)
        canvas.axes.set_xlabel("Time (s)")
        canvas.axes.set_ylabel("Frequency (Hz)")
        canvas.axes.set_title("Spectrogram")

        if not hasattr(canvas, 'colorbar') or canvas.colorbar is None:
            canvas.colorbar = canvas.figure.colorbar(cax, ax=canvas.axes)
            canvas.colorbar.set_label("Power (dB)")
                
        else:
                # Update the color bar's content
            canvas.colorbar.update_normal(cax)

        canvas.draw()