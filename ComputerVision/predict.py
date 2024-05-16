from ultralytics import YOLO

import cv2
import sys

def is_tomato(image_path, model_path):

    model = YOLO(model_path)

    results = model(image_path)
    for result in results:
        im = result.plot()

    return im

if __name__ == "__main__" :
    model_path = './tomato.pt'
    image_path = sys.argv[1]
    image = is_tomato(image_path, model_path)
    cv2.imshow('Output', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

