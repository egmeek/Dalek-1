import pygame
from pygame import locals
import sys
import Image
import time

#this is important for capturing/displaying images
import opencv
from opencv import highgui

#GUI
from pgu import gui as pgui, text

#Velleman board
from pyk8055 import *

#Buttons on wheel:
#0: X
#1: O
#2: SQUARE
#3: TRIANGLE
#4: Topleft, unmarked

camera = highgui.cvCreateCameraCapture(0)

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




def sendSignal(signalCode):
    #Flashes signal to Veleman
    k.WriteAllDigital(signalCode)
    k.WriteAllDigital(0)

def headTrackState(arg):
    btn, text = arg
    global headTracking
    headTracking = btn.value

def get_image():
    global headTracking
    im = highgui.cvQueryFrame(camera)
    # Add the line below if you need it (Ubuntu 8.04+)
    #im = opencv.cvGetMat(im)
    #convert Ipl image to PIL image
    if (headTracking): 
	detect(im)
	#Also fire servos we need.
    return opencv.adaptors.Ipl2PIL(im)

def detect(image):
    # Find out how large the file is, as the underlying C-based code
    # needs to allocate memory in the following steps
    image_size = opencv.cvGetSize(image)
    scale=8
    # create grayscale version - this is also the point where the allegation about
    # facial recognition being racist might be most true. A caucasian face would have more
    # definition on a webcam image than an African face when greyscaled.
    # I would suggest that adding in a routine to overlay edge-detection enhancements may
    # help, but you would also need to do this to the training images as well.
    grayscale = opencv.cvCreateImage(image_size, 8, 1)
    opencv.cvCvtColor(image, grayscale, opencv.CV_BGR2GRAY)
    thumbnail = opencv.cvCreateImage(opencv.cvSize(grayscale.width/scale,grayscale.height/scale),8,1)
    opencv.cvResize(grayscale,thumbnail)
    # create storage (It is C-based so you need to do this sort of thing)
    storage = opencv.cvCreateMemStorage(0)
    opencv.cvClearMemStorage(storage)

    # equalize histogram
    opencv.cvEqualizeHist(grayscale, grayscale)

    # detect objects - Haar cascade step
    # In this case, the code uses a frontal_face cascade - trained to spot faces that look directly
    # at the camera. In reality, I found that no bearded or hairy person must have been in the training
    # set of images, as the detection routine turned out to be beardist as well as a little racist!
    cascade = opencv.cvLoadHaarClassifierCascade('haarcascade_frontalface_default.xml', opencv.cvSize(1,1))

    faces = opencv.cvHaarDetectObjects(thumbnail, cascade, storage, 1.2, 2, opencv.CV_HAAR_DO_CANNY_PRUNING, opencv.cvSize(10,10))

    if faces.total > 0:
        for face in faces:
            # Hmm should I do a min-size check?
            opencv.cvRectangle(image, opencv.cvPoint( int(face.x) *scale, int(face.y*scale)),opencv.cvPoint(int(face.x + face.width)*scale, int(face.y + face.height)*scale), opencv.CV_RGB(127, 255, 0), 2) # RGB #7FFF00 width=2


headTracking=False
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
	pg_img = pygame.image.frombuffer(im.tostring(), im.size, im.mode)
	screen.fill((0,0,0))
	screen.blit(pg_img, (0,0))
	gui.paint()
	pygame.display.flip()
	pygame.time.delay(int(1000 * 1.0/fps))

