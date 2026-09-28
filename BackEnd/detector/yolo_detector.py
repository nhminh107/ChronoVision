import json
from pathlib import Path

from PIL import Image
from ultralytics import YOLO


class Detector:
    def __init__(self):
        config_path = Path(__file__).resolve().parent.parent / "config.json"
        with config_path.open(encoding="utf-8") as config_file:
            self.classes = json.load(config_file)["classes"]

        self.model = YOLO("yolo26s-objv1-150.pt")

    def detector(self, image: Image.Image):
        return self.model.predict(image, classes=self.classes)
