from ultralytics import YOLO

import cv2
import sys
import threading
from datetime import datetime 
import os
import json

#General detection function
#Returns an anotated image and a dictionary with the objects detected
def is_tomato(in_image, model_path):

    model = YOLO(model_path)

    results = model(in_image, conf = 0.65)
    detect = {}
    for result in results:
        im = result.plot()
        print(result.names)
        for j in result.names:
            detect[result.names[j]] = 0

        for i in result.boxes.cls:
            detect[result.names[int(i.item())]] +=1
    return im, detect

#Thread function
#Runs the detection and saves the image and a .json file with the details
def tomato_thread(in_image, UID, model_path):
    out_image, detect = is_tomato(in_image, model_path)
    print(detect)
    date = datetime.now()
    name = date.strftime("%d-%m-%Y_%H-%M-%S")   #File name is the time

    #Creates user id directory
    if not os.path.exists(UID):
        os.mkdir(UID)
    cv2.imwrite(UID + '/' + name + ".png", out_image)   #Write image file

    with open(UID + '/' + name + '.json', "w") as outfile: 
        json.dump({"model":  model_path, "detections" : detect}, outfile)   #Write .json file

#Runs the detection on an image in a thread
def detect(in_image, UID, model_path):
    t = threading.Thread(target = tomato_thread, args = (in_image, UID, model_path))

    t.start()

if __name__ == "__main__" :
    model_path = sys.argv[2]
    image_path = sys.argv[1]
    in_image = cv2.imread(image_path)
    if in_image is None:
        print('Could not open image')
        exit
    detect(in_image, '1234', model_path)
    # image, objetos = is_tomato(in_image, model_path)
    # print(objetos)
    # cv2.imshow('Output', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

