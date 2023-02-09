import cv2
from darkflow.net.build import  TFNet
import matplotlib.pyplot as plt
import os

options={
   'model':'./cfg/yolo.cfg',        #specifying the path of model
   'load':'./bin/yolov2.weights',   #weights taken from yolo website
   'threshold':0.3                  #minimum confidence factor to create a box
}

tfnet=TFNet(options)
inputPath = os.getcwd() + "/test_images/"
outputPath = os.getcwd() + "/output_images/"

def detectVehicles(filename):
   global tfnet, inputPath, outputPath
   img=cv2.imread(inputPath+filename,cv2.IMREAD_COLOR)

   result=tfnet.return_predict(img)

   for vehicle in result:
      label=vehicle['label']
      if(label=="car" or label=="bus" or label=="pcar" or label=="truck" or label=="sTruck"):
         top_left=(vehicle['topleft']['x'],vehicle['topleft']['y'])
         bottom_right=(vehicle['bottomright']['x'],vehicle['bottomright']['y'])
         img=cv2.rectangle(img,top_left,bottom_right,(0,255,0),3)
         img=cv2.putText(img,label,top_left,cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
   outputFilename = outputPath + "output_" +filename
   cv2.imwrite(outputFilename,img)
   print('Output image stored at:', outputFilename)


for filename in os.listdir(inputPath):
   if(filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg")):
      detectVehicles(filename)
print("The test images are stored in output_image folder!")