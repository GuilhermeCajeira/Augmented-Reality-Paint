#!/usr/bin/env python3

import argparse
from copy import deepcopy
from time import sleep
import cv2
import numpy as np
import json
from colorama import Fore, Style
from datetime import datetime
import math
import os
import time

#Definicao de argumentos 
parser = argparse.ArgumentParser(description="Definition of test mode")

parser.add_argument("-j", "--json", help="Full path to json file")
parser.add_argument("-usp", "--use_shake_prevention", help="Runs the shake prevention code", action="store_true")
args = parser.parse_args()
        
                      
def main():
    limits = json.load(open(args.json))
    min = np.array([limits['B']['min'], limits['G']['min'], limits['R']['min']])
    max = np.array([limits['B']['max'], limits['G']['max'], limits['R']['max']])
    cap = cv2.VideoCapture(0)
    x_list = []
    y_list = [] 
    color = (0, 255, 255)
    thickness = 2
    black_board = np.zeros((600, 800, 3), np.uint8)
    white_board = np.zeros((600, 800, 3), np.uint8)
    white_board.fill(255) 
    date_now = datetime.now()
    date_now_string = date_now.strftime("%a_%b_%d_%H:%M:%S_%Y")
    board = white_board
    board_change = 0
    shapes = 0
    square = 0
    circle = 0
    ellipse = 0
    center = 0


    while True:
        _, image = cap.read()
        img = cv2.resize(image, (800, 600))
        img_flipped = cv2.flip(img, 1)
        image_gui = deepcopy(img_flipped)
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
                    p1 = (x_list[-2], y_list[-2])
                    p2 = (x_list[-1], y_list[-1])
                    # points_distance = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
                    points_distance = math.dist(p1,p2)
                    if args.use_shake_prevention == False:
                        cv2.line(board, (x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]), color, thickness)
                        if board_change == 1:
                            cv2.line(image_gui, (x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]), color, thickness)
                        
                    if points_distance < 50 and args.use_shake_prevention == True:
                        cv2.line(board, (x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]), color, thickness)
          
                   
                    

        gray = cv2.cvtColor(black_board, cv2.COLOR_BGR2GRAY)
        _, img_thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)
        img_thresholded = cv2.cvtColor(img_thresholded, cv2.COLOR_GRAY2BGR)
        image_gui = cv2.bitwise_and(image_gui, img_thresholded)
        image_gui = cv2.bitwise_or(image_gui, black_board)
        if board_change == 1:
            cv2.imshow("Board", image_gui)


        # Commands list
        pressed_key = cv2.waitKey(20)   
        if pressed_key == ord('q'):     # Quit the program
            break
        # elif pressed_key == ord('s'):
        #     shapes = 1
        #     square = 1
        elif pressed_key == ord('c') and shapes == 0:
            shapes = 1
            center = (x_list[-1], y_list[-1])
            # circle = 1
        elif pressed_key != ord('c') and shapes == 1:
            a = (x_list[-1], y_list[-1])
            radius = math.sqrt(((center[0]-a[0])**2)+((center[1]-a[1])**2))
            cv2.circle(board,center,int(radius), color, thickness)
            shapes = 0
            # circle = 0
        
        if shapes == 0:
            if pressed_key == ord('l'):   # Change board to stream
                board_change = 1      
                black_board = np.zeros((600, 800, 3), np.uint8)
                board = black_board
                print("Stream board")
            elif pressed_key == ord('k'):   # Change board to white
                board_change = 0            
                white_board = np.zeros((600, 800, 3), np.uint8)
                white_board.fill(255) 
                board = white_board
                print("White board")    
            elif pressed_key == ord('w'):   # Save the drawing in the drawings folder
                # path = "/home/rafael/Desktop/psr_22-23/Parte07/Drawings/"
                path = '/home/UA/PSR/PSR/Parte7/'
                print('chegou')
                cv2.imwrite(path + "Drawing_" + date_now_string + ".png", white_board)
                if board_change == 1:
                    cv2.imwrite(path + "Img_Drawing_" + date_now_string + ".png", image_gui)
            elif pressed_key == ord('c'):   # Clear the board
                print(Fore.RED + 'Board cleared' + Style.RESET_ALL)
                x_list = []
                y_list = []
                white_board = np.zeros((600, 800, 3), np.uint8)
                white_board.fill(255) 
                board = white_board
                if board_change == 1:
                    black_board = np.zeros((600, 800, 3), np.uint8)
                    board = black_board
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
        cv2.imshow("Board", white_board)
        cv2.imshow("Original", img_flipped)
        cv2.imshow("Segmented", img_segmented)
        cv2.imshow("Largest object", large_object_mask)  
   
      
       
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
