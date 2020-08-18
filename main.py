
import cv2
import pytesseract
import numpy
import mss
import sys
import time
import Levenshtein

text_enemy_surrend = 'Enemy team agreed to a surrend with x votes for and x against'
text_ally_surrend_after = 'Your team agreed to a surrender with x votes for and x against'
text_ally_surrend = 'has started a surrender vote. Type /surrender or /nosurrender'
enemy_surrend_max_distance = 10
ally_surrend_max_distance = 8

def find_closest_match(string, text):
    closest_match = -1
    closest_distance = -1
    for i in range(len(string) + len(text)):
        distance = Levenshtein.distance(string[i-len(text) if i-len(text) >= 0 else 0 : i], text)
        if distance < closest_distance or closest_distance < 0:
            closest_match = i
            closest_distance = distance

    print("- Closest match:")
    print(string[closest_match-len(text) if closest_match-len(text) >= 0 else 0 : closest_match])
    return closest_distance

kernel_erode_v = numpy.ones((2,1), numpy.uint8)
kernel_erode_h = numpy.ones((1,2), numpy.uint8)
kernel_dilate = numpy.ones((5,5), numpy.uint8)
kernel_final = numpy.ones((2,1), numpy.uint8)

sct = mss.mss()
monitor = {'left': 10, 'top': 1062, 'width': 680, 'height': 190}
if len(sys.argv) >= 5:
    monitor['left'] = int(sys.argv[1])
    monitor['top'] = int(sys.argv[2])
    monitor['width'] = int(sys.argv[3])
    monitor['height'] = int(sys.argv[4])

print('monitor config:', monitor)

frame_count = 0
t0 = time.time()
fps = 20
while True:
    img = numpy.array(sct.grab(monitor))

    mask = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), (15, 200, 150), (25, 255, 255))
    mask = cv2.erode(mask, kernel_erode_v, iterations=1)
    mask = cv2.erode(mask, kernel_erode_h, iterations=1)
    mask = cv2.dilate(mask, kernel_dilate, iterations=5)

    masked = cv2.bitwise_and(img, img, mask=mask)
    masked = cv2.inRange(cv2.cvtColor(masked, cv2.COLOR_BGR2HSV), (15, 110, 100), (25, 255, 255))
    masked = 255-masked

    eroded = cv2.erode(masked, kernel_final, iterations=1)

    cv2.imshow('raw', img)
    cv2.imshow('mask', mask)
    cv2.imshow('masked', masked)
    cv2.imshow('eroded', eroded)
    cv2.waitKey(1)

    detected_string = pytesseract.image_to_string(eroded, lang='eng')

    print("=== Detected:")
    print(detected_string)

    detected_string = detected_string.replace('\n', ' ').replace('\r', '')

    enemy_surrend_distance = find_closest_match(detected_string, text_enemy_surrend)
    ally_surrend_distance = find_closest_match(detected_string, text_ally_surrend)
    ally_surrend_after_distance = find_closest_match(detected_string, text_ally_surrend_after)

    print("--------", enemy_surrend_distance, ally_surrend_distance, ally_surrend_after_distance)

    if enemy_surrend_distance < enemy_surrend_max_distance and enemy_surrend_distance < ally_surrend_after_distance:
        print("ENEMY SURREND")
        time.sleep(2)
    
    if ally_surrend_distance < ally_surrend_max_distance:
        print("ALLY SURREND")
        time.sleep(2)
    
    frame_count += 1
    if frame_count == fps:
        t1 = time.time()
        fps = fps/(t1 - t0)
        print("FPS:", fps)
        fps = int(fps*2 + 1)
        frame_count = 0
        t0 = t1
