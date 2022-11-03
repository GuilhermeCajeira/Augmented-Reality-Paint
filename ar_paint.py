#!/usr/bin/env python3

import argparse
from copy import deepcopy
import cv2
import numpy as np
import json
from colorama import Fore, Style
from datetime import datetime
import math


#Definicao de argumentos 
parser = argparse.ArgumentParser(description="Definition of test mode")

parser.add_argument("-j", "--json", help="Full path to json file", required=True)
parser.add_argument("-usp", "--use_shake_prevention", help="Runs the shake prevention code", action="store_true")
args = parser.parse_args()
        
                      
def main():
    limits = json.load(open(args.json))
    min = np.array([limits['B']['min'], limits['G']['min'], limits['R']['min']])
    max = np.array([limits['B']['max'], limits['G']['max'], limits['R']['max']])
    cap = cv2.VideoCapture(0)
    x_list = []
    y_list = []
    center = (0, 0) 
    color = (0, 255, 255)
    thickness = 2
    black_board = np.zeros((600, 800, 3), np.uint8)
    white_board = np.zeros((600, 800, 3), np.uint8)
    white_board.fill(255) 
    date_now = datetime.now()
    date_now_string = date_now.strftime("%a_%b_%d_%H:%M:%S_%Y")
    board = white_board
    board_change = 0
    circle_draw = 0
    shape_draw = 0
    pt1 = (0,0)
    rectangle_draw = 0
    radius = 0
    
    while True:
        _, image = cap.read()
        img = cv2.resize(image, (800, 600))
        img_flipped = cv2.flip(img, 1)
        image_gui = deepcopy(img_flipped)
        img_segmented = cv2.inRange(img_flipped, min, max)
        large_object_mask = np.zeros((600, 800, 1), np.uint8)
        contours, _ = cv2.findContours(img_segmented, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        quadro = np.zeros((600, 800, 3), np.uint8)
        quadro.fill(255)
        quadro_preto = np.zeros((600, 800, 3), np.uint8)
       
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 20000:
                cv2.drawContours(img_flipped, [cnt], -1, (0,255,0), 2)
                cv2.drawContours(large_object_mask, [cnt], -1, (255,255,255), -1)
                # Centroid calculation
                M = cv2.moments(large_object_mask)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # Draw the marker
                cv2.drawMarker(img_flipped, (cx, cy), (0, 0, 255), 0, 15, 3)
                x_list.append(cx)
                y_list.append(cy)
               
                # Draw the line
                if len(x_list) > 2 and circle_draw == 0 and rectangle_draw == 0:
                    points_distance = math.dist((x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]))
                    if args.use_shake_prevention == False: 
                        cv2.line(board, (x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]), color, thickness)
                        if board_change == 1:
                            cv2.line(image_gui, (x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]), color, thickness)
                    if points_distance < 50 and args.use_shake_prevention == True:
                        cv2.line(board, (x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]), color, thickness)
                        if board_change == 1:
                            cv2.line(image_gui, (x_list[-2], y_list[-2]), (x_list[-1], y_list[-1]), color, thickness)
                
                # Draw the circle
                if circle_draw == 1 and rectangle_draw == 0:
                    radius = math.dist(center, (x_list[-1], y_list[-1]))
                    cv2.circle(quadro,center,int(radius), color, thickness)
                    cv2.circle(quadro_preto,center,int(radius), color, thickness)
                    if shape_draw == 1:
                        cv2.circle(board,center,int(radius), color, thickness)
                        circle_draw = 0
                        shape_draw = 0
                        if board_change == 1:
                            cv2.circle(board,center,int(radius), color, thickness)
                            circle_draw = 0
                            shape_draw = 0
                
                # Draw the rectangle            
                if rectangle_draw == 1 and circle_draw == 0:
                    pt2 = (x_list[-1], y_list[-1])
                    cv2.rectangle(quadro, pt1, pt2, color, thickness)
                    cv2.rectangle(quadro_preto, pt1, pt2, color, thickness)
                    if shape_draw == 1:
                        cv2.rectangle(board, pt1, pt2, color, thickness)
                        rectangle_draw = 0
                        shape_draw = 0

                        if board_change == 1:
                            cv2.rectangle(board, pt1, pt2, color, thickness)
                            rectangle_draw = 0
                            shape_draw = 0

        # Images fusion
        show_shape_growing_gui = cv2.bitwise_or(quadro_preto, black_board)   
        show_shape_growing = cv2.bitwise_and(quadro, board)
        gray = cv2.cvtColor(black_board, cv2.COLOR_BGR2GRAY)
        _, img_thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)
        img_thresholded = cv2.cvtColor(img_thresholded, cv2.COLOR_GRAY2BGR)
        image_gui = cv2.bitwise_and(image_gui, img_thresholded)
        image_gui = cv2.bitwise_or(image_gui, show_shape_growing_gui)
        
        if board_change == 1:
            cv2.imshow("Board", image_gui)
       

        # Commands list
        pressed_key = cv2.waitKey(20)   
        if pressed_key == ord('q'):     # Quit the program
            break
        elif pressed_key == ord('e'):   # Draw a circle
            center = (x_list[-1], y_list[-1])
            circle_draw = 1
            rectangle_draw = 0
        elif pressed_key == ord('t'):   # Draw the shape
            shape_draw = 1    
        elif pressed_key == ord('d'):   # Draw a rectangle
            pt1 = (x_list[-1], y_list[-1])
            rectangle_draw = 1  
            circle_draw = 0                  
        elif pressed_key == ord('l'):   # Change board to stream
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
            path = "/home/rafael/Desktop/psr_22-23/Parte07/Drawings/"
            # path = "/home/guilherme/UA/PSR/Augmented-Reality-Paint/"
            cv2.imwrite(path + "Drawing_" + date_now_string + ".png", white_board)
            if board_change == 1:
                cv2.imwrite(path + "Img_Drawing_" + date_now_string + ".png", image_gui)
            print('Saved drawing to ' + "Img_Drawing_" + date_now_string + ".png")
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
        cv2.imshow("Board", show_shape_growing)
        cv2.imshow("Original", img_flipped)
        cv2.imshow("Segmented", img_segmented)
        cv2.imshow("Largest object", large_object_mask)  
      
       
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()