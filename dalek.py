import pygame
from pygame import locals
import sys
import Image

import opencv
#this is important for capturing/displaying images
from opencv import highgui

#Velleman board
from pyk8055 import *

camera = highgui.cvCreateCameraCapture(1)
def get_image():
    im = highgui.cvQueryFrame(camera)
    # Add the line below if you need it (Ubuntu 8.04+)
    #im = opencv.cvGetMat(im)
    #convert Ipl image to PIL image
    return opencv.adaptors.Ipl2PIL(im)

fps = 30.0
pygame.init()
window = pygame.display.set_mode((640,480))
pygame.display.set_caption("WebCam Demo")
screen = pygame.display.get_surface()

pygame.joystick.init()

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


while 1:
	for e in pygame.event.get():
		print e
		if e.type == pygame.locals.JOYAXISMOTION:
			x,y = j.get_axis(0), j.get_axis(1)
			print 'x and y : ' + str(x) + ' , ' + str(y)
		elif e.type == pygame.locals.JOYBALLMOTION:
			print 'ballmotion'
		elif e.type == pygame.locals.JOYHATMOTION:
			print 'hatmotion'
		elif e.type == pygame.locals.JOYBUTTONDOWN:
			if e.button ==2 :
				k.WriteAllDigital(1)
			if e.button == 3:
				k.WriteAllDigital(2)	
		elif e.type == pygame.locals.JOYBUTTONUP:
			print 'buttonup'

	im = get_image()
	pg_img = pygame.image.frombuffer(im.tostring(), im.size, im.mode)
	screen.blit(pg_img, (0,0))
	pygame.display.flip()
	pygame.time.delay(int(1000 * 1.0/fps))

