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



#Definição de argumentos 
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
                #Calcular o centroide
                M = cv2.moments(large_object_mask)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.drawMarker(img, (cx, cy), (0, 0, 255), 0, 15, 3)
                x_list.append(cx)
                y_list.append(cy)

       
        pressed_key = cv2.waitKey(20)   
        white_board = np.zeros((600, 800, 3), np.uint8)
        white_board.fill(255)
        
        drawLine(white_board, x_list, y_list, (0,0,0), 5)

    
        cv2.imshow("Whiteboard", white_board)
        cv2.imshow("Original", img)
        cv2.imshow("Segmented", img_segmented)
        cv2.imshow("Largest object", large_object_mask)  
      

        if pressed_key == ord('q'):
            break
        
       
    cap.release()
    cv2.destroyAllWindows()





if __name__ == "__main__":
    main()