# the libraries
import PySimpleGUI as sg
from tkinter import *
import cv2 as cv
import os
import numpy as np
import time
import threading
import csv
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global Variables
width, height = 1920, 1080
frame_size = width * height * 3 // 2
current_frame = 0
stop = False
n_frames = 0

window1 = None
window2 = None

XforYforAvg = []
XforUforAvg = []
XforVforAvg = []
xforYforVar = []
xforUforVar = []
xforVforVar = []

# Function to play frame by frame
def play(f, window):
    global current_frame
    for i in range(n_frames - current_frame):
        if (stop):
            break
        updateWindow(f, window)
        current_frame += 1
        time.sleep(1)

# Function to check the frame
def checkFrame():
    global current_frame
    if (current_frame >= n_frames):
        current_frame = 0
    elif (current_frame < 0):
        current_frame = n_frames - 1

# Function to update the Window
def updateWindow(f, window):
    checkFrame()
    updateHistogram(f, window)
    updateFrame(f, window)

# Function to update the frame
def updateFrame(f, window):
    f.seek(current_frame * frame_size)
    yuv = np.frombuffer(f.read(frame_size), dtype=np.uint8).reshape((height * 3 // 2, width))
    bgr = cv.cvtColor(yuv, cv.COLOR_YUV2BGR_I420)
    data = cv.imencode('.png',bgr)[1].tobytes()
    window['video'].update(data=data, visible=True, subsample=2)

# Function to read the histogram data file
def readHistogramFile(string_name):
    file = open(string_name,'r', encoding='utf-8-sig')
    type(file)
    csvreader = csv.reader(file)
    dataSet = []
    for row in csvreader:
        dataSet.append(row)
    dataSet
    file.close

    dataSet_final = [list(map(int, i)) for i in dataSet]
    return dataSet_final

# Function to load the histogram data
def loadHistograms():
    global XforYforAvg
    global XforUforAvg
    global XforVforAvg
    global XforYforVar
    global XforUforVar
    global XforVforVar

    XforYforAvg = readHistogramFile('AVERAGE_HISTOGRAM_Y.csv')
    XforUforAvg = readHistogramFile('AVERAGE_HISTOGRAM_U.csv')
    XforVforAvg = readHistogramFile('AVERAGE_HISTOGRAM_V.csv')

    XforYforVar = readHistogramFile('VARIANCE_HISTOGRAM_Y.csv')
    XforUforVar = readHistogramFile('VARIANCE_HISTOGRAM_U.csv')
    XforVforVar = readHistogramFile('VARIANCE_HISTOGRAM_V.csv')

# Function to update the histogram
def updateHistogram(f, window):
    y = []
    for i in range(0, 16):
        y.append(str(i + 1))

    fig, ax = plt.subplots(figsize = (16,9))  
    fig.suptitle('Frame ' + str(current_frame), fontsize = 22)  
    x = [str(z) for z in y]
    barWidth =.25
    bar1 = np.arange(len(y))
    bar2 = [x + barWidth for x in bar1]
    bar3 = [x + barWidth for x in bar2]
    
    plt.subplot(1,2,1)
    plt.bar(bar1,XforYforAvg[current_frame], color = 'g', width = barWidth, edgecolor = 'grey', label = 'Y')
    plt.bar(bar2,XforUforAvg[current_frame], color = 'b', width = barWidth, edgecolor = 'grey', label = 'U')
    plt.bar(bar3,XforVforAvg[current_frame], color = 'r', width = barWidth, edgecolor = 'grey', label = 'V')
    plt.title('8x8 Average 16 Bins', fontsize = 20)
    plt.xlabel('Bins', fontweight = 'bold', fontsize = 16)
    plt.xticks(fontsize = 14)
    plt.yticks(fontsize = 14)
    plt.ticklabel_format(useOffset=False, style='plain')
    plt.legend(fontsize = 14)

    plt.subplot(1,2,2)
    plt.bar(bar1,XforYforVar[current_frame], color = 'g', width = barWidth, edgecolor = 'grey', label = 'Y')
    plt.bar(bar2,XforUforVar[current_frame], color = 'b', width = barWidth, edgecolor = 'grey', label = 'U')
    plt.bar(bar3,XforVforVar[current_frame], color = 'r', width = barWidth, edgecolor = 'grey', label = 'V')
    plt.title('8x8 Variance 16 Bins', fontsize = 20)
    plt.xlabel('Bins', fontweight = 'bold', fontsize = 16)
    plt.xticks(fontsize = 14)
    plt.yticks(fontsize = 14)
    plt.ticklabel_format(useOffset=False, style='plain')
    plt.legend(fontsize = 14)

    figure = plt.gcf()
    figure.canvas.draw()
    image = np.frombuffer(figure.canvas.tostring_rgb(), dtype=np.uint8).reshape(figure.canvas.get_width_height()[::-1] + (3,))
    data = cv.imencode('.png',image)[1].tobytes()
    window['histogram'].update(data=data, visible=True, subsample=2)

###########################################################################

# the color of the background
sg.theme("DarkTeal")

# loads histogram files
loadHistograms()

# the layout/design of the window
layout = [
        [sg.Text('Interface')],
        [sg.Multiline(size=(80,10))],
        [sg.Button('Open'), sg.Button('Exit')],
        ]

# When window1 is opened the title of the interface and layout is displayed
window1 = sg.Window('Interface', layout, element_justification = 'c')

# While window1 is open then the following will occur based on what the user clicks
while True:

    # Opens window1 and activates the buttons
    event, values = window1.read()

    # If the user closes Window1 or click the 'Exit' button the window closes
    if event in (sg.WIN_CLOSED, 'Exit') or event == 'Exit':
        exit()

    # If the user clicks the 'Open' button the following occurs
    elif event == 'Open':

        # when the open button is clicked then a popup will appear to prompt the user to choose a YUV file
        file_path = sg.PopupGetFile('Please enter a file name')

        # Checks to see if the file that the user entered exists
        if file_path != None and os.path.exists(file_path):

            # window1 gets hidden
            window1.Hide()

            # Gets the file size 
            file_size = os.path.getsize(file_path)

            # Calculates the number of frames
            n_frames = file_size // (frame_size)

            # Opens the YUv file 
            f = open(file_path, 'rb')
            
            # the layout/design of the window
            layout2 = [
            [sg.Image(key='video'), sg.Image(key='histogram')],
                [sg.Button('<<'),
                sg.Button('Play'),
                sg.Button('Pause'),
                sg.Button('>>')]
            ]

            # When window2 is opened the title of the interface and layout is displayed
            window2 = sg.Window('Video Interface', layout2, finalize=True, element_justification = 'c')

            # For displaying the video and histogram on the first frame
            updateWindow(f, window2)

            # While window2 is open then the following will occur based on what the user clicks
            while True:
                
                # Opens window2 and activates the buttons
                event, values = window2.Read()

                # If the user closes Window2 or click the 'Exit' button the window closes and window1 opens again
                if event in (sg.WIN_CLOSED, 'Exit'):
                    window2.Close()  
                    window1.UnHide()  
                    break
                
                # When the user clicks the button ">>" it skips to the next frame
                elif event == '>>':
                    current_frame += 1
                    updateWindow(f, window2)

                # When the user clicks the button "Play" the video will go through the frames
                elif event == 'Play':
                    stop = False
                    threading.Thread(target=play, args=(f, window2)).start()             

                # When the user clicks the button "Pause" the video will stop on a frame
                elif event == 'Pause':
                    stop = True

                # When the user clicks the button "<<" it skips to the previous frame
                elif event == '<<':
                    current_frame -= 1
                    updateWindow(f, window2)

        # If the file does not exist a message will appear
        elif not(os.path.exists(file_path)):
            sg.Popup('File does not exist!')
