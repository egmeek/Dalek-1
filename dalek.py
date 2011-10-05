import pygame
from pygame import locals
import sys
import Image
import time

#this is important for capturing/displaying images
import numpy as np
import cv2
import cv2.cv as cv
from video import create_capture
from common import clock, draw_str

#GUI
from pgu import gui as pgui, text

#Velleman board
from pyk8055 import *

#Arduino - only one of this and Velleman will be used. Probably...
import pyduino

#Buttons on wheel:
#0: X
#1: O
#2: SQUARE
#3: TRIANGLE
#4: Topleft, unmarked

camera = create_capture(0)

def playSound(fileName):
	if not pygame.mixer.music.get_busy():
		pygame.mixer.music.load(fileName)
		pygame.mixer.music.play(1)

def open_file_browser(guiInput):
    d = pgui.FileDialog()
    d.connect(pgui.CHANGE, handle_file_browser_closed, d,guiInput)
    d.open()


def handle_file_browser_closed(dlg, guiInput):
    if dlg.value: guiInput.value = dlg.value


def sendSignalVelleman(signalCode):
    k.WriteAllDigital(signalCode)
    k.WriteAllDigital(0)

def sendSignalArduino(signalCode):
    print signalCode

def sendSignal(signalCode):
    #Flashes signal to Veleman
    sendSignalVelleman(signalCode)


def headTrackState(arg):
    btn, text = arg
    global headTracking
    headTracking = btn.value

def get_image():
    global headTracking
    global cascade    
    ret, im = camera.read()
    t = clock()
    if (headTracking):
        grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        grey = cv2.equalizeHist(grey)
	rects = detect(grey, cascade)
        draw_rects(im, rects, (0,255,0))
	#TODO: Also fire servos we need.
    dt = clock() - t
    draw_str(im, (20,20), 'Latency: %.4f ms' % (dt*1000))
    im_rgb=cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    cv_img=cv.fromarray(im_rgb)
    return cv_img

def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv.CV_HAAR_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)



fps = 30.0
pygame.init()
window = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
pygame.display.set_caption("DalekCam")
screen = pygame.display.get_surface()

pygame.joystick.init()

#Set up the GUI
fontBig = pygame.font.SysFont("default", 48)
fg=(255,255,255)
gui = pgui.App()
lo=pgui.Container(width=1024,height=600)
title = pgui.Label("Dalek Controller", color=fg, font=fontBig)
lo.add(title,700,10)

cbt = pgui.Table()
cb1 = pgui.Switch()
cb1.connect(pgui.CHANGE, headTrackState, (cb1, "Head Tracking"))
cb1l = pgui.Label("Enable Head Tracking",color=fg)
cbt.add(cb1)
cbt.add(cb1l)
cbt.tr()
lo.add(cbt,750,60)

#Choose MP3s
t = pgui.Table()
t.tr()
td_style = {'padding_right': 10, 'color':fg}
t.td( pgui.Label('Top Left Sound File:',color=fg) , style=td_style)
input_file_1 = pgui.Input()
t.td( input_file_1, style=td_style )
b = pgui.Button("Browse...")
t.td( b, style=td_style )
input_file_1.value="./ext1.mp3"
b.connect(pgui.CLICK, open_file_browser, input_file_1)

t.tr()
t.td( pgui.Label('Top Right Sound File:',color=fg) , style=td_style)
input_file_2 = pgui.Input()
t.td( input_file_2, style=td_style )
b2 = pgui.Button("Browse...")
t.td( b2, style=td_style )
b2.connect(pgui.CLICK, open_file_browser, input_file_2)
input_file_2.value="./dalek-doctor.mp3"
lo.add(t,550,500)

#Load information about face detection.

cascade_fn = "./haarcascade_frontalface_alt.xml"
cascade = cv2.CascadeClassifier(cascade_fn)
headTracking=False



gui.init(lo)

try:
	j=pygame.joystick.Joystick(0)
	j.init()
	print 'Enabled joystick: ' + j.get_name()
except pygame.error:
	print 'no joystick found'

try:
	k=k8055(0)
except IOError:
	print 'could not find K8055 board'

done=False
while not done:
	for e in pygame.event.get():
		if e.type is pygame.locals.QUIT:
			done=True
		elif e.type is pygame.locals.KEYDOWN and e.key == pygame.locals.K_ESCAPE:
			done=True	
		elif e.type == pygame.locals.JOYAXISMOTION:
			x,y = j.get_axis(0), j.get_axis(1)
			print 'x and y : ' + str(x) + ' , ' + str(y)
		elif e.type == pygame.locals.JOYBALLMOTION:
			print 'ballmotion'
		elif e.type == pygame.locals.JOYHATMOTION:
			print 'hatmotion'
		elif e.type == pygame.locals.JOYBUTTONDOWN:
			if e.button ==0 :
				sendSignal(22)
			elif e.button == 1:
				#Enable Head Tracking
				cb1.click()
			elif e.button == 2:
				sendSignal(58)
			elif e.button == 3:
				sendSignal(2)	

			elif e.button == 4:
				playSound(input_file_1.value)
			elif e.button == 5:
				playSound(input_file_2.value)
		elif e.type == pygame.locals.JOYBUTTONUP:
			print 'buttonup'
		else:
			gui.event(e) #pass it to the GUI

	im = get_image()
	pg_img = pygame.image.frombuffer(im.tostring(), cv.GetSize(im), "RGB")
	screen.fill((0,0,0))
	screen.blit(pg_img, (0,0))
	gui.paint()
	pygame.display.flip()
	pygame.time.delay(int(1000 * 1.0/fps))

