from MySignal import Signal
import pyqtgraph as pg
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, QSize
import numpy as np
import sys
from PyQt5.QtWidgets import QWidget


def set_icon(button, icon_path):
    pixmap = QPixmap(icon_path)
    button.setIcon(QIcon(pixmap))
    button.setIconSize(QSize(30, 30))
    button.setFixedSize(30, 30)
    button.setStyleSheet("border: none; background-color: none;")


class Graph():
    current_index = 0
    current_index_increment = 10

    timer = QTimer()
    timer.setInterval(100)  # Update every 100ms

    def __init__(self, centralWidget,is_frequency_domain=False):
        super().__init__()
        self.plot_widget = pg.PlotWidget(centralWidget)
        self.signal = None
        self.current_index = 0
        self.current_index_increment = 10
        self.is_paused = False
        self.is_off = False
        self.curve = None
        self.window_size = 100
        self.is_frequency_domain=is_frequency_domain
        if not self.is_frequency_domain:
            Graph.timer.timeout.connect(self.update_plot)

    def add_signal(self, signal,start=True, color=None):
        color = "b" if color is None else color
        self.signal = signal

        if start:
            self.curve = self.plot_widget.plot(signal[0][:1], signal[1][:1], pen=color)
        else :

            self.curve = self.plot_widget.plot(signal[0][:len(signal[0])], signal[1][:len(signal[0])], pen=color)
        self.set_plot_limits()
        if start:
            self.timer.start()

    def update_plot(self):

        if Graph.current_index < len(self.signal[0]):
            self.curve.setData(self.signal[0][:Graph.current_index], self.signal[1][:Graph.current_index])
        Graph.current_index += Graph.current_index_increment

        time = self.signal[0]
        start_index = max(0, Graph.current_index - self.window_size)
        self.plot_widget.setXRange(time[start_index], time[Graph.current_index], padding=1)
        self.plot_widget.setLimits(xMax=time[Graph.current_index])

    def play_pause(self):
        if self.is_paused:
            Graph.timer.start()
            # set_icon(self.play_pause_button, "icons/pause.png")
        else:
            Graph.timer.stop()
            # set_icon(self.play_pause_button, "icons/play.png")
        self.is_paused = not self.is_paused

    def rewind_signal(self):
        if len(self.signal) > 0:
            Graph.current_index = 0
            if self.is_paused:
                # set_icon(self.play_pause_button, "icons/pause.png")
                pass
            self.timer.start()

    def off_signal(self):
        self.timer.stop()

        self.current_index = 0
        # set_icon(self.play_pause_button, "icons/play.png")
        self.is_paused = False

        self.graph_1.setLimits(xMin=0, xMax=2, yMin=-2, yMax=2)

    def zoom_in(self):

        x_range = self.plot_widget.viewRange()[0]
        y_range = self.plot_widget.viewRange()[1]

        self.plot_widget.setXRange(x_range[0] + 0.1 * (x_range[1] - x_range[0]),
                                   x_range[1] - 0.1 * (x_range[1] - x_range[0]), padding=0)
        self.plot_widget.setYRange(y_range[0] + 0.1 * (y_range[1] - y_range[0]),
                                   y_range[1] - 0.1 * (y_range[1] - y_range[0]), padding=0)

    def zoom_out(self):

        x_range = self.plot_widget.viewRange()[0]
        y_range = self.plot_widget.viewRange()[1]

        self.plot_widget.setXRange(x_range[0] - 0.1 * (x_range[1] - x_range[0]),
                                   x_range[1] + 0.1 * (x_range[1] - x_range[0]), padding=0)
        self.plot_widget.setYRange(y_range[0] - 0.1 * (y_range[1] - y_range[0]),
                                   y_range[1] + 0.1 * (y_range[1] - y_range[0]), padding=0)

    def set_plot_limits(self):
        """Set the plot limits based on the loaded data."""
        if self.signal:
            x_max = self.signal[0][-1]

            y_min = min(self.signal[1])
            y_max = max(self.signal[1])

            y_min = y_min - y_min * 0.05 if y_min > 0 else y_min + y_min * 0.05

            self.plot_widget.setLimits(
                xMin=0, xMax=x_max + 10,
                yMin=y_min, yMax=y_max + y_max * 0.05
            )
    def reconstruct_signal_on_equalized_plot(self,re_signal):
        self.remove_old_curve()
        self.signal[1]=re_signal
        if Graph.current_index < len(self.signal[0]):
            self.curve =self.plot_widget.plot(self.signal[0][:Graph.current_index],re_signal[:Graph.current_index],pen=(0, 0, 255))
            self.set_plot_limits()

    def remove_old_curve(self):
        self.curve= self.plot_widget.removeItem(self.curve)

    def speed_signal(self, speed_button):
        if self.current_index_increment == 10:
            self.current_index_increment = 20
            speed_button.setText("2X")
        elif self.current_index_increment == 20:
            self.current_index_increment = 40
            speed_button.setText("4X")
        elif self.current_index_increment == 40:
            self.current_index_increment = 80
            speed_button.setText("8X")
        else:
            self.current_index_increment = 10
            speed_button.setText("1X")
