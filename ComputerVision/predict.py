from ultralytics import YOLO

import cv2
import sys

def is_tomato(in_image, model_path):

    model = YOLO(model_path)

    results = model(in_image)
    for result in results:
        im = result.plot()

    return im

if __name__ == "__main__" :
    model_path = './tomato.pt'
    image_path = sys.argv[1]
    in_image = cv2.imread(image_path)
    if in_image is None:
        print('Could not open image')
        exit
    image = is_tomato(in_image, model_path)
    cv2.imshow('Output', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

