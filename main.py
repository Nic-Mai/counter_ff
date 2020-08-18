
import cv2
import pytesseract
import numpy
import mss
import keyboard

def noop(val):
    pass

mon = {'top': 150, 'left': 50, 'width': 500, 'height': 500}

cv2.namedWindow('control')
cv2.createTrackbar('min H', 'control', 5, 180, noop)
cv2.createTrackbar('max H', 'control', 35, 180, noop)
cv2.createTrackbar('min S', 'control', 110, 255, noop)
cv2.createTrackbar('max S', 'control', 255, 255, noop)
cv2.createTrackbar('min V', 'control', 100, 255, noop)
cv2.createTrackbar('max V', 'control', 255, 255, noop)

img = cv2.imread('C:\\Users\\Nicolas\\Desktop\\surrend.png')

sct = mss.mss()
while True:
    #img = numpy.array(sct.grab(mon))

    min_h = cv2.getTrackbarPos('min H', 'control')
    max_h = cv2.getTrackbarPos('max H', 'control')
    min_s = cv2.getTrackbarPos('min S', 'control')
    max_s = cv2.getTrackbarPos('max S', 'control')
    min_v = cv2.getTrackbarPos('min V', 'control')
    max_v = cv2.getTrackbarPos('max V', 'control')

    kernel = numpy.ones((3,3), numpy.uint8)

    mask = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), (min_h, 110, 110), (max_h, max_s, max_v))
    mask = cv2.dilate(mask, kernel, iterations=3)

    masked = cv2.bitwise_and(img, img, mask=mask)
    
    filtered = cv2.inRange(cv2.cvtColor(masked, cv2.COLOR_BGR2HSV), (min_h, min_s, min_v), (max_h, max_s, max_v))
    filtered = 255-filtered

    cv2.imshow('raw', img)
    cv2.imshow('mask', mask)
    cv2.imshow('masked', masked)
    cv2.imshow('filtered', filtered)
    cv2.waitKey(1)

    string = pytesseract.image_to_string(filtered, lang='eng')

    print("===================")
    print(string)

    references = [
        'Type /help for a list of commands',
        'Type /allcommands for all possible commands.',
        'Usage: /help [command] to get usage information on that command.'
    ]

    ok = True
    for ref in references:
        if ref not in string:
            print('-------------')
            print('Did not get:')
            print(ref)
            ok = False

    if ok:
        print("OK")

    if keyboard.is_pressed('q'):
        break
