
import sys

import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog
import ui  # This assumes the Ui_MainWindow class is in the `ui` module
# from newui import Ui_MainWindow  # This assumes the Ui_MainWindow class is in the `ui` module
from qt_material import apply_stylesheet
import modes
import MySignal#change the name later
from Audiogram import Audiogram

available_frequencies = {
    'Uniform Mode': {1:[100, 1000],
                    2:[100, 1000],
                    3:[100, 1000],
                    4:[100, 1000],
                    5:[100, 1000],
                    6:[100, 1000],
                    7:[100, 1000],
                    8:[100, 1000],
                    9:[100, 1000],
                    10:[100, 1000]
                     },#max frequency /10
    'Music': {"Guitar": [40, 400],
              "Flute": [400, 800],
              "Violin ": [950, 4000],
              "Xylophone": [5000, 14000]},
    'Animal Sounds': {"Dog": [0, 450],
                      "Wolf": [450, 1100],
                      "Crow": [1100, 3000],
                      "Bat": [3000, 9000]},
    'ECG Abnormalities': {"Normal": [0, 35],
                          "Arithmia_1 ": [48, 52],
                          "Arithmia_2": [55, 94],
                          "Arithmia_3": [95, 155]}}

class MainWindow(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.myaudiogram = Audiogram()
        self.modeComboBox.currentIndexChanged.connect(self.choose_mode)
        self.current_mode_name = 'Uniform Mode'#default
        self.current_mode_obj = None
        self.signal_file_path=''
        self.sliders_layout=None
        self.loadButton.clicked.connect(self.get_file_path)
        self.current_signal=None
        self.equalized_signal=None
        self.current_band_edges=MySignal.available_frequencies[self.current_mode_name]
        self.frequency_domain=None
        self.saveButton.clicked.connect(self.save_signal)
        self.playButton.clicked.connect(self.originalGraph.play_pause)
        self.resetButton.clicked.connect(self.originalGraph.rewind_signal)
        self.zoomInButton.clicked.connect(self.originalGraph.zoom_in)
        self.zoomOutButton.clicked.connect(self.originalGraph.zoom_in)

    def save_signal(self):#save button
        self.choose_mode()
        self.current_signal=MySignal.Signal(mode=self.current_mode_name, file_path=self.signal_file_path)
        self.equalized_signal=self.current_signal
        self.originalGraph.add_signal(signal=np.array([self.current_signal.time_data,self.current_signal.amplitude_data]))
        self.equalizedGraph.add_signal(signal=np.array([self.equalized_signal.time_data,self.equalized_signal.amplitude_data]))
        if self.current_mode_obj is not None:
             print("spect")
             self.current_mode_obj.plot_spectrogram(self.current_signal.amplitude_data, self.originalSpectrugram)
             self.current_mode_obj.plot_spectrogram(self.equalized_signal.amplitude_data, self.equalizedSpecrtugram)
            #  self.myaudiogram.plotAudiogram(self.equalized_signal.amplitude_data, self.equalized_signal.sampling_rate,self.frequencyDomainPlot)
        self.choose_mode()
        if self.current_mode_name=='Uniform Mode':
            frequencies=self.current_mode_obj.compute_fft()[1]
            max_freq=np.max(frequencies)
            start,end=0,max_freq/10
            for i in range (1, 11):
                available_frequencies["Uniform Mode"][i]=[start,end]
                start+=max_freq/10
                end+=max_freq/10
            # for i in range (11):
            #     print(f"available_frequencies[uniform Mode][{i}] {available_frequencies['Uniform Mode'][i]}")








    def get_file_path(self):#load button
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*);;Text Files (*.txt)")

        if file_path:
            self.signal_file_path=file_path



    def switch_sliders(self):
        while self.gridLayout_7.count():
            child = self.gridLayout_7.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.sliders_layout is not None and self.sliders_layout.count():
            child = self.sliders_layout.takeAt(0)
            if child is not None and child.widget() :
                child.widget().deleteLater()
    def choose_mode(self):#ChomboBox

        self.current_mode_name = self.modeComboBox.currentText()

        self.current_mode_obj=modes.modes(signal=self.current_signal,band_edges=available_frequencies[self.current_mode_name],window=self)
        if self.current_signal is not None :
            self.current_mode_obj.compute_fft()
        # self.current_mode_obj.apply_gain()
        # self.frequency_domain=self.current_mode_obj.
        # self.frequencyDomainPlot.add_signal()
        self.switch_sliders()
        self.gridLayout_12.removeItem(self.gridLayout_7)
        self.gridLayout_12.removeItem(self.sliders_layout)
        self.sliders_layout=self.current_mode_obj.slider_creator(mode_name=self.current_mode_name,range_of_slider=[0,1])


        self.gridLayout_12.addLayout(self.sliders_layout,7,2,1,2)





app = QApplication(sys.argv)
window = MainWindow()
apply_stylesheet(app, theme='dark_teal.xml')
window.show()
sys.exit(app.exec_())