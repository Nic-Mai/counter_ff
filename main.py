
import cv2
import pytesseract
import numpy
import mss
import sys
import time
import playsound
from pynput.keyboard import Controller, Key
import requests
import threading

text_enemy_surrend = 'Enemy team agreed to a surrender with x votes for and x against'
text_ally_surrend_after = 'Your team agreed to a surrender with x votes for and x against'
text_ally_surrend = 'has started a surrender vote. Type /surrender or /nosurrender'
enemy_surrend_max_distance = 10
ally_surrend_max_distance = 8
alarm_repetitions = 4


kb = Controller()

kernel_erode_v = numpy.ones((2, 1), numpy.uint8)
kernel_erode_h = numpy.ones((1, 2), numpy.uint8)
kernel_dilate = numpy.ones((5, 5), numpy.uint8)
kernel_final = numpy.ones((2, 1), numpy.uint8)

auto_surrend = False
bot_url = None
bot_token = None

sct = mss.mss()
monitor = {'left': 0, 'top': 0, 'width': 0, 'height': 0}
if len(sys.argv) >= 6 and sys.argv[5] in ['yes', 'no']:
    monitor['left'] = int(sys.argv[1])
    monitor['top'] = int(sys.argv[2])
    monitor['width'] = int(sys.argv[3])
    monitor['height'] = int(sys.argv[4])
    if sys.argv[5] == 'yes':
        auto_surrend = True
    if len(sys.argv) >= 8:
        bot_url = sys.argv[6]
        bot_token = sys.argv[7]
else:
    print('Usage:')
    print(sys.argv[0], '<left> <top> <width> <height> <auto_surrend (yes/no)> [<bot_url> <bot_token>]')
    print('Example:')
    print(sys.argv[0], '10 1062 680 190 yes')
    exit()

print('monitor config:', monitor)
print('auto_surrend:', auto_surrend)
print('bot_url:', bot_url)
print('bot_token:', bot_token)


def press_key(key):
    kb.press(key)
    time.sleep(0.03)
    kb.release(key)
    time.sleep(0.03)


def send_request():
    res = requests.post(bot_url, json={'token': bot_token}, timeout=10)


def alarm(message):
    if bot_url is not None and bot_token is not None:
        threading.Thread(target=send_request).start()

    for i in range(alarm_repetitions):
        print(message)
        playsound.playsound('annoying_alarm_clock_sound.wav')

        if auto_surrend:
            press_key(Key.enter)
            press_key('/')
            press_key('f')
            press_key('f')
            press_key(Key.enter)


def levenshtein_distance(s1, s2):
    n = len(s2)
    m = len(s1)
    v0 = []
    v1 = [0] * (n+1)

    for i in range(n+1):
        v0.append(i)

    for i in range(m):
        v1[0] = i+1

        for j in range(n):
            deletion_cost = v0[j+1] + 1
            insertion_cost = v1[j] + 1
            substitution_cost = v0[j]
            if not s1[i] == s2[j]:
                substitution_cost += 1
            v1[j+1] = min(deletion_cost, insertion_cost, substitution_cost)

        tmp = v0
        v0 = v1
        v1 = tmp

    return v0[n]


def find_closest_match(string, text):
    closest_match = -1
    closest_distance = -1
    for i in range(len(string) + len(text)):
        distance = levenshtein_distance(string[i-len(text) if i-len(text) >= 0 else 0: i], text)
        if distance < closest_distance or closest_distance < 0:
            closest_match = i
            closest_distance = distance

    return closest_distance

if __name__ == '__main__':
    frame_count = 0
    frame_max_count = 20
    t0 = time.time()
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
            alarm('ENEMY SURREND')
            exit()
        elif ally_surrend_distance < ally_surrend_max_distance:
            print('ALLY SURREND')

        frame_count += 1
        if frame_count == frame_max_count:
            t1 = time.time()
            fps = frame_max_count/(t1 - t0)
            print("FPS:", fps)
            frame_count = 0
            frame_max_count = int(fps*2 + 1)
            t0 = t1
