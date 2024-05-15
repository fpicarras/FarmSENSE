from ultralytics import YOLO

import cv2

def is_tomato(image_path, model_path):

    model = YOLO(model_path)

    results = model.predict(image_path, imgsz = 640, conf = 0.5, show = True, save = True)
    cv2.waitKey(0)
    for i, r in enumerate(results):
        cv2.waitKey(0)
    print(results)

if __name__ == "__main__" :
    model_path = '/home/wonebone/Documents/PIC/laboro_tomato/image-segmentation-yolov8/runs/segment/train4/weights/last.pt'
    image_path = '/home/wonebone/Pictures/tomatoes.jpg'
    is_tomato(image_path, model_path)


