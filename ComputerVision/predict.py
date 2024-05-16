from ultralytics import YOLO

import cv2
import sys

def is_tomato(in_image, model_path):

    model = YOLO(model_path)

    results = model(in_image)
    detect = {}
    for result in results:
        im = result.plot(show = True)
        print(result.names)
        for j in result.names:
            detect[result.names[j]] = 0

        for i in result.boxes.cls:
            detect[result.names[int(i.item())]] +=1
    return im, detect

if __name__ == "__main__" :
    model_path = './tomato.pt'
    image_path = sys.argv[1]
    in_image = cv2.imread(image_path)
    if in_image is None:
        print('Could not open image')
        exit
    image, objetos = is_tomato(in_image, model_path)
    print(objetos)
    cv2.imshow('Output', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

