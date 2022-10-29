#!/usr/bin/env python


import argparse
from csv import list_dialects
from re import L
import cv2
import numpy as np
# import copy
from functools import partial
import json
from colorama import Fore, Back, Style
from copy import deepcopy


#Definicao de argumentos 
parser = argparse.ArgumentParser(description="Definition of test mode")

parser.add_argument("-j", "--json", help="Full path to json file")
args = parser.parse_args()

def drawLine(image, x, y, color, thickness):
        for xi, yi in zip(x, y):
            cv2.line(image, (xi, yi), (xi, yi), color, thickness)
            if len(x) > 2:
        
                idx = list(range(0, len(x)))
                for idx1, idx2 in zip(idx[:-1], idx[1:]):
                    x1 = x[idx1]
                    y1 = y[idx1]
                    x2 = x[idx2]
                    y2 = y[idx2]
                    cv2.line(image, (x1, y1), (x2, y2), color, thickness)

    
def main():
    limits = json.load(open(args.json))
    min = np.array([limits['B']['min'], limits['G']['min'], limits['R']['min']])
    max = np.array([limits['B']['max'], limits['G']['max'], limits['R']['max']])
    cap = cv2.VideoCapture(0)
    x_list = []
    y_list = []  

    pencil_color = (0,0,0)
    thickness = 5
    # global xs, ys
    # global options 
    # options = {'image': None, 'xs': [], 'ys': [], 'pencil_color': (0,0,0)}
    
    while True:
        _, image = cap.read()
        img = cv2.resize(image, (800, 600))
        img_segmented = cv2.inRange(img, min, max)
        large_object_mask = np.zeros((600, 800, 1), np.uint8)
        _, contours, _ = cv2.findContours(img_segmented, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
          
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            if area > 20000:
                cv2.drawContours(img, [cnt], -1, (0,255,0), 2)
                cv2.drawContours(large_object_mask, [cnt], -1, (255,255,255), -1)
                #Calcular o centroide
                M = cv2.moments(large_object_mask)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.drawMarker(img, (cx, cy), (0, 0, 255), 0, 15, 3)
                x_list.append(cx)
                y_list.append(cy)

        white_board = np.zeros((600, 800, 3), np.uint8)
        white_board.fill(255)

        drawLine(white_board, x_list, y_list, pencil_color, thickness)

    
        cv2.imshow("Whiteboard", white_board)
        cv2.imshow("Original", img)
        cv2.imshow("Segmented", img_segmented)
        cv2.imshow("Largest object", large_object_mask)  
      
        pressed_key = cv2.waitKey(20)
        if pressed_key == ord('q'):     # Quite the program
            break
        elif pressed_key == ord('c'):   # Clear the drawing
            print(Fore.RED + 'You pressed c' + Style.RESET_ALL)
            x_list = []
            y_list = []
        elif pressed_key == ord('r'):   # Draw with red color
            pencil_color = (0,0,255)
            print('Pencil color ' + Style.BRIGHT + Fore.RED + 'red ' + Style.RESET_ALL)
        elif pressed_key == ord('g'):   # Draw with green color
            pencil_color = (0,255,0)
            print('Pencil color ' + Style.BRIGHT + Fore.GREEN + 'green ' + Style.RESET_ALL)
        elif pressed_key == ord('b'):   # Draw with blue color
            pencil_color = (255,0,0)
            print('Pencil color ' + Style.BRIGHT + Fore.BLUE + 'blue ' + Style.RESET_ALL)
        elif pressed_key == ord('+'):
            thickness += 1
            print('Pencil size increased to ' + str(thickness))
        elif pressed_key == ord('-'):
            thickness -= 1
            print('Pencil size decreased to ' + str(thickness))
        
       
    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()