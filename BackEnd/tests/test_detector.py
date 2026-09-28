from PIL import Image

from BackEnd.detector.yolo_detector import Detector


if __name__ == "__main__":
    image_path = "/home/nhminh/Pictures/Image/minh.jpg"

    with Image.open(image_path) as image:
        results = Detector().detector(image)

    for result in results:
        print(result.summary())
