import pygame
from pygame import locals
import sys
import Image

import opencv
#this is important for capturing/displaying images
from opencv import highgui

#GUI
from pgu import gui

#Velleman board
from pyk8055 import *

camera = highgui.cvCreateCameraCapture(1)
def get_image():
    im = highgui.cvQueryFrame(camera)
    # Add the line below if you need it (Ubuntu 8.04+)
    #im = opencv.cvGetMat(im)
    #convert Ipl image to PIL image
    return opencv.adaptors.Ipl2PIL(im)

class DalekControl(gui.Table):
	def __init__(self,**params):
		gui.Table.__init__(self,**params)
		fg=(255,255,255)
 		self.tr()
        	self.td(gui.Label("Dalek GUI",color=fg),colspan=2)




fps = 30.0
pygame.init()
window = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
pygame.display.set_caption("DalekCam")
screen = pygame.display.get_surface()

pygame.joystick.init()

form = gui.Form()
app = gui.App()
dalekCtrl = DalekControl()
c=gui.Container(align=-1,valign=-1)
c.add(dalekCtrl,700,30)

app.init(c)

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
		print e
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
			if e.button ==2 :
				k.WriteAllDigital(1)
			if e.button == 3:
				k.WriteAllDigital(2)	
		elif e.type == pygame.locals.JOYBUTTONUP:
			print 'buttonup'
		else:
			app.event(e) #pass it to the GUI

	im = get_image()
	pg_img = pygame.image.frombuffer(im.tostring(), im.size, im.mode)
	screen.blit(pg_img, (0,0))
	app.paint()
	pygame.display.flip()
	pygame.time.delay(int(1000 * 1.0/fps))

