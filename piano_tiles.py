# Play piano tiles by using open-cv2 and pyautogui

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab as ig
import time

# TODO --- figure out a better way to determine the game window on the screen
image_res = {'x': 400.0, 'y': 140.0}
window_x = 1490
window_y = 585
pyautogui.PAUSE = 0.0325


# take in the frame, convert it to grayscale, and find all the contours or shapes
# convert back to RGB and the pass the frame so we can find the tile we need to click
def process_frame(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(frame, 150, 255, 50)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    frame, black_tile = find_black_tile(frame, contours)
    move_mouse(black_tile)
    return frame


# find the tile that needs to be clicked
# takes in the current frame, and the contours in that frame
def find_black_tile(frame, contours):
    black_tile_center = (0, 0)
    # loops through every contour and determines the area so we can rule out any shapes
    # that may be false positives (i.e. an edge of the game board that isn't an actual tile)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        display_color = (0, 0, 255)
        x, y, w, h = cv2.boundingRect(cnt)
        if 12000 < area < 65000:
            center_point = (x + w // 2, (y + h // 2) + 55)
            center_color = frame[center_point[1], center_point[0]]
            # exit the program if we win the game or if we see the failure screen
            if [167, 167, 167] in center_color or [82, 82, 82] in center_color:
                exit(0)
            # if the center color of the contour is black, we've found our tile
            if [17, 17, 17] in center_color:
                display_color = (0, 255, 0)
                black_tile_center = center_point
                cv2.circle(frame, center_point, 3, display_color, 1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), display_color, 1)
    return [frame, black_tile_center]


# move the mouse to the screen coordinates by add the game window offset to the coordinates of the center of the tile
def move_mouse(frame_points):
    screen_points = (frame_points[0] + window_x, frame_points[1] + window_y)
    pyautogui.click(screen_points[0], screen_points[1], interval=0.001)


# capture frames from our computer screen that will be used for processing
def screen_record():
    last_time = time.time()
    while True:
        frame = np.array(ig.grab(bbox=(window_x, window_y, window_x + image_res['x'], window_y + image_res['y'])))
        # print('Loop took {} seconds'.format(time.time()-last_time))
        processed_frame = process_frame(frame)
        cv2.imshow("raw_frame", frame)
        cv2.imshow("processed_frame", processed_frame)
        last_time = time.time()
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    screen_record()
