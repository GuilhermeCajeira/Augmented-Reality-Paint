#!/usr/bin/env python3


import argparse
from csv import list_dialects
from re import L
import cv2
import numpy as np
import copy
from functools import partial
import json
from colorama import Fore, Style
from datetime import datetime, date
import os



#Definição de argumentos 
parser = argparse.ArgumentParser(description="Definition of test mode")

parser.add_argument("-j", "--json", help="Full path to json file")
args = parser.parse_args()
        
                      
def main():
    limits = json.load(open(args.json))
    min = np.array([limits['B']['min'], limits['G']['min'], limits['R']['min']])
    max = np.array([limits['B']['max'], limits['G']['max'], limits['R']['max']])
    cap = cv2.VideoCapture(0)
    x_list = []
    y_list = [] 
    color = (0, 0, 0)
    thickness = 2
    white_board = np.zeros((600, 800, 3), np.uint8)
    white_board.fill(255) 
    date_now = datetime.now()
    date_now_string = date_now.strftime("%a_%b_%d_%H:%M:%S_%Y")
          
    while True:
        _, image = cap.read()
        img = cv2.resize(image, (800, 600))
        img_segmented = cv2.inRange(img, min, max)
        large_object_mask = np.zeros((600, 800, 1), np.uint8)
        contours, _ = cv2.findContours(img_segmented, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 20000:
                cv2.drawContours(img, [cnt], -1, (0,255,0), 2)
                cv2.drawContours(large_object_mask, [cnt], -1, (255,255,255), -1)
                # Centroid calculation
                M = cv2.moments(large_object_mask)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # Draw the marker
                cv2.drawMarker(img, (cx, cy), (0, 0, 255), 0, 15, 3)
                x_list.append(cx)
                y_list.append(cy)
                # Draw the line
                if len(x_list) > 2:
                    cv2.line(white_board, (x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]), color, thickness)
       
       
        # Commands list
        pressed_key = cv2.waitKey(20)   
        if pressed_key == ord('q'):     # Quit the program
            break
        elif pressed_key == ord('w'):   # Save the drawing in the drawings folder
            path = "/home/rafael/Desktop/psr_22-23/Parte07/Drawings/"
            cv2.imwrite(path + "Drawing_" + date_now_string + ".png", white_board)
        elif pressed_key == ord('c'):   # Clear the board
            print(Fore.RED + 'Board cleared' + Style.RESET_ALL)
            x_list = []
            y_list = []
            white_board = np.zeros((600, 800, 3), np.uint8)
            white_board.fill(255) 
        elif pressed_key == ord('r'):   # Draw with red color
            color = (0,0,255)
            print('Pencil color ' + Style.BRIGHT + Fore.RED + 'red ' + Style.RESET_ALL)
        elif pressed_key == ord('g'):   # Draw with green color
            color = (0,255,0)
            print('Pencil color ' + Style.BRIGHT + Fore.GREEN + 'green ' + Style.RESET_ALL)
        elif pressed_key == ord('b'):   # Draw with blue color
            color = (255,0,0)
            print('Pencil color ' + Style.BRIGHT + Fore.BLUE + 'blue ' + Style.RESET_ALL)
        elif pressed_key == ord('+'):   # Increase pencil thickness
            thickness += 1
            print('Pencil size increased to ' + str(thickness))
        elif pressed_key == ord('-'):   # Decrease pencil thickness
            thickness -= 1
            limit = 'Pencil size decreased to ' + str(thickness) 
            if thickness < 1 :
                thickness = 1
                limit = 'Cant decrease more'
            print(limit)

        # Visualization
        cv2.imshow("Whiteboard", white_board)
        cv2.imshow("Original", img)
        cv2.imshow("Segmented", img_segmented)
        cv2.imshow("Largest object", large_object_mask)  
      
       
    cap.release()
    cv2.destroyAllWindows()





if __name__ == "__main__":
    main()