#!/usr/bin/env python


import argparse
from ast import For
import cv2
import numpy as np
import copy
from functools import partial
import json
from colorama import Fore, Style
from pprint import pprint


# def bMin(b_min):
#     pass
# def bMax(b_max):
#     pass
# def gMin(g_min):
#     pass
# def gMax(g_max):
#     pass
# def rMin(r_min):
#     pass
# def rMax(r_max):
#     pass

def onTrackbar(value, channel, min_max, limits):
    limits[channel][min_max] = value  # update corresponding value in limits dict

    print('Selected threshold ' + str(value) + ' for limit ' + str(min_max) + ' ' + str(channel))
   


def main(): 

    #window for trackbars 
    window_name_original = 'Original'
    window_name_segmented = 'Segmented'
    cv2.namedWindow(window_name_original,cv2.WINDOW_AUTOSIZE)


    #trackbars
    # cv2.createTrackbar("Blue_min", window_name_original, 0, 255, bMin)
    # cv2.createTrackbar("Blue_max", window_name_original, 255, 255, bMax)
    # cv2.createTrackbar("Green_min", window_name_original, 0, 255, gMin)
    # cv2.createTrackbar("Green_max", window_name_original, 255, 255, gMax)
    # cv2.createTrackbar("Red_min", window_name_original, 0, 255, rMin)
    # cv2.createTrackbar("Red_max", window_name_original, 255, 255, rMax)

    limits = {'B': {'min': 0, 'max': 256},
              'G': {'min': 0, 'max': 256},
              'R': {'min': 0, 'max': 256}}

    cv2.createTrackbar('MinB', window_name_original, 0,   256, partial(onTrackbar, channel='B', min_max='min', limits=limits))
    cv2.createTrackbar('MaxB', window_name_original, 256, 256, partial(onTrackbar, channel='B', min_max='max', limits=limits))
    cv2.createTrackbar('MinG', window_name_original, 0,   256, partial(onTrackbar, channel='G', min_max='min', limits=limits))
    cv2.createTrackbar('MaxG', window_name_original, 256, 256, partial(onTrackbar, channel='G', min_max='max', limits=limits))
    cv2.createTrackbar('MinR', window_name_original, 0,   256, partial(onTrackbar, channel='R', min_max='min', limits=limits))
    cv2.createTrackbar('MaxR', window_name_original, 256, 256, partial(onTrackbar, channel='R', min_max='max', limits=limits))

    cap = cv2.VideoCapture(0)

    while True:
        _, image = cap.read()

        if image is None:
            print('Video is over, terminating')
            break                   # video is over

        # b_min = cv2.getTrackbarPos("Blue_min", window_name_original)
        # b_max = cv2.getTrackbarPos("Blue_max", window_name_original)
        # g_min = cv2.getTrackbarPos("Green_min", window_name_original)
        # g_max = cv2.getTrackbarPos("Green_max", window_name_original)
        # r_min = cv2.getTrackbarPos("Red_min", window_name_original)
        # r_max = cv2.getTrackbarPos("Red_max", window_name_original)
        # image_segmented = cv2.inRange(image,(b_min, g_min, r_min),(b_max, g_max, r_max))      
        mins = np.array([limits['B']['min'], limits['G']['min'], limits['R']['min']])
        maxs = np.array([limits['B']['max'], limits['G']['max'], limits['R']['max']])
        image_segmented = cv2.inRange(image, mins, maxs)
        
        cv2.imshow(window_name_original, image)
        cv2.imshow(window_name_segmented, image_segmented)

        # limits = {'B': {'min': b_min, 'max': b_max},
        #                 'G': {'min': g_min, 'max': g_max},
        #                 'R': {'min': r_min, 'max': r_max}}
        
        pressed_key = cv2.waitKey(20)
        if pressed_key == ord('q'):
            break
        if pressed_key == ord('w'):
            file_name = 'limits.json'
            with open(file_name, "w") as file_handle:
                json.dump(limits, file_handle) 
            print('Writing color limits to file ' + file_name)
            pprint(limits)
            break
     
        
  
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


