
import cv2
import pytesseract
import numpy
import mss
import sys
import time
import Levenshtein
import playsound
from pynput.keyboard import Controller, Key

text_enemy_surrend = 'Enemy team agreed to a surrender with x votes for and x against'
text_ally_surrend_after = 'Your team agreed to a surrender with x votes for and x against'
text_ally_surrend = 'has started a surrender vote. Type /surrender or /nosurrender'
enemy_surrend_max_distance = 10
ally_surrend_max_distance = 8
sound_repetitions = 8


def press_key(key):
    kb.press(key)
    time.sleep(0.03)
    kb.release(key)
    time.sleep(0.03)


def find_closest_match(string, text):
    closest_match = -1
    closest_distance = -1
    for i in range(len(string) + len(text)):
        distance = Levenshtein.distance(string[i-len(text) if i-len(text) >= 0 else 0: i], text)
        if distance < closest_distance or closest_distance < 0:
            closest_match = i
            closest_distance = distance

    return closest_distance


kb = Controller()

kernel_erode_v = numpy.ones((2, 1), numpy.uint8)
kernel_erode_h = numpy.ones((1, 2), numpy.uint8)
kernel_dilate = numpy.ones((5, 5), numpy.uint8)
kernel_final = numpy.ones((2, 1), numpy.uint8)

auto_surrend = False

sct = mss.mss()
monitor = {'left': 0, 'top': 0, 'width': 0, 'height': 0}
if len(sys.argv) >= 6:
    monitor['left'] = int(sys.argv[1])
    monitor['top'] = int(sys.argv[2])
    monitor['width'] = int(sys.argv[3])
    monitor['height'] = int(sys.argv[4])
    if sys.argv[5] == 'yes':
        auto_surrend = True
else:
    print('Usage:')
    print(sys.argv[0], '<left> <top> <width> <height> <auto_surrend>')
    print('Example:')
    print(sys.argv[0], '10 1062 680 190 yes')
    exit()

print('monitor config:', monitor)
print('auto_surrend:', auto_surrend)

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

    filtered = cv2.erode(masked, kernel_final, iterations=1)

    cv2.imshow('preview', img)
    #cv2.imshow('mask', mask)
    #cv2.imshow('masked', masked)
    cv2.imshow('filtered', filtered)
    cv2.waitKey(1)

    detected_string = pytesseract.image_to_string(filtered, lang='eng')

    print('=== Detected:')
    print(detected_string)
    print('===')

    detected_string = detected_string.replace('\n', ' ').replace('\r', '')

    enemy_surrend_distance = find_closest_match(detected_string, text_enemy_surrend)
    ally_surrend_distance = find_closest_match(detected_string, text_ally_surrend)
    ally_surrend_after_distance = find_closest_match(detected_string, text_ally_surrend_after)

    print('enemy_surrend_distance:', enemy_surrend_distance, ', ally_surrend_distance:', ally_surrend_distance, ', ally_surrend_after_distance:', ally_surrend_after_distance)

    if enemy_surrend_distance < enemy_surrend_max_distance and enemy_surrend_distance <= (ally_surrend_after_distance-1):
        for i in range(sound_repetitions):
            print('ENEMY SURREND')
            playsound.playsound('annoying_alarm_clock_sound.wav')

            if auto_surrend:
                press_key(Key.enter)
                press_key('/')
                press_key('f')
                press_key('f')
                press_key(Key.enter)
        exit()
    elif ally_surrend_distance < ally_surrend_max_distance:
        print('ALLY SURREND')

    frame_count += 1
    if frame_count == fps:
        t1 = time.time()
        fps = fps/(t1 - t0)
        print("FPS:", fps)
        fps = int(fps*2 + 1)
        frame_count = 0
        t0 = t1
