#!/usr/bin/env python

import argparse
import cv2
import numpy as np
import copy
from functools import partial
import json

def onTrackbar(value, channel, min_max, window_name, image, limits):
    limits[channel][min_max] = value  # update corresponding value in limits dict

    print('Selected threshold ' + str(value) + ' for limit ' + str(min_max) + ' ' + str(channel))

# def mouseCallback(event, x, y, flags, param):
#     if event == cv2.EVENT_LBUTTONDOWN:
#         print('Mouse event at x=' + str(x) + ' y=' + str(y))


def main():
    # -----------------------------------------------
    # INIT
    # -----------------------------------------------
    window_name_original = 'Original'
    window_name_segmented = 'Segmented'
    capture = cv2.VideoCapture(0)

    cv2.namedWindow(window_name_original,cv2.WINDOW_AUTOSIZE)

    _, image = capture.read()  # get an image from the camera

    limits = {'B': {'min': 0, 'max': 256},
              'G': {'min': 0, 'max': 256},
              'R': {'min': 0, 'max': 256}}

    cv2.createTrackbar('MinB', window_name_original, 0,   256, partial(onTrackbar, channel='B', min_max='min',window_name=window_name_segmented, image=image, limits=limits))
    cv2.createTrackbar('MaxB', window_name_original, 256, 256, partial(onTrackbar, channel='B', min_max='max',window_name=window_name_segmented, image=image, limits=limits))
    cv2.createTrackbar('MinG', window_name_original, 0,   256, partial(onTrackbar, channel='G', min_max='min',window_name=window_name_segmented, image=image, limits=limits))
    cv2.createTrackbar('MaxG', window_name_original, 256, 256, partial(onTrackbar, channel='G', min_max='max',window_name=window_name_segmented, image=image, limits=limits))
    cv2.createTrackbar('MinR', window_name_original, 0,   256, partial(onTrackbar, channel='R', min_max='min',window_name=window_name_segmented, image=image, limits=limits))
    cv2.createTrackbar('MaxR', window_name_original, 256, 256, partial(onTrackbar, channel='R', min_max='max',window_name=window_name_segmented, image=image, limits=limits))

    # -----------------------------------------------
    # EXECUTION
    # -----------------------------------------------
    while True:
        _, image = capture.read()  # get an image from the camera

        if image is None:
            print('Video is over, terminating')
            break                   # video is over

        # image_GUI = copy.deepcopy(image)

        # Processing
        mins = np.array([limits['B']['min'], limits['G']['min'], limits['R']['min']])
        maxs = np.array([limits['B']['max'], limits['G']['max'], limits['R']['max']])
        image_mask = cv2.inRange(image, mins, maxs)
        image_mask = image_mask.astype(bool)  # conversion from numpy from uint8 to bool

        image_processed = copy.deepcopy(image)
        image_processed[np.logical_not(image_mask)] = 0

        cv2.imshow(window_name_original, image) 
        cv2.imshow(window_name_segmented, image_processed) 
        
        # cv2.setMouseCallback(window_name_original, mouseCallback)
        # print('limts = ' + str(limits))

        pressed_key = cv2.waitKey(20)
        if chr(pressed_key) == 'q': # Quite the program
            exit(0)
        elif chr(pressed_key) == 'w': 
            file_name = 'limits.json'
            with open(file_name, 'w') as file_handle:
                print('writing dictionary limits to file ' + file_name)
                json.dump(limits, file_handle) # d is the dicionary
            exit(0)


if __name__ == '__main__':
    main()