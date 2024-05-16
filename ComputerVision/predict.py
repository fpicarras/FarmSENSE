from ultralytics import YOLO

from PIL import Image
import cv2
import sys

def is_tomato(image_path, model_path):

    model = YOLO(model_path)

    results = model(image_path)
    # Read the input image
    image = cv2.imread(image_path)
    # Annotate the detected objects on the image
    for result in results:
        print(result)
#        print(result.boxes)
#        print(result.masks)
        im
#        print(im)
        cv2.imshow('YOLO', im)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return image

if __name__ == "__main__" :
    model_path = './tomato.pt'
    image_path = sys.argv[1]
    is_tomato(image_path, model_path)


