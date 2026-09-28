import cv2
from ultralytics import YOLO
from BackEnd.Database.postgre_sql import Postgre_Manager
from pathlib import Path
import json
from BackEnd.Contract.data_contracts import (CameraContract, EntityContract, EventContract, TrackContract)
from uuid import uuid4
from queue import Queue
import datetime


class Tracker: 
    def __init__(self, sql: Postgre_Manager = None):
        self._sql = sql
        self.model = YOLO("yolo26s-objv1-150.pt")
        config_path = Path.cwd() / "BackEnd" / "tracker" / "config.json"
        with config_path.open(encoding="utf-8") as config_file:
            self.classes = json.load(config_file)["classes"]

        self.q = Queue(maxsize=300)

    def track(self, camera_id: int): 
        cap = cv2.VideoCapture(camera_id)
        count = 0
        while cap.isOpened(): 
            ret, frame = cap.read()
            if not ret: 
                break

            results = self.model.track(
                source=frame, 
                conf=0.5,
                iou=0.7,
                persist=True,
                classes=self.classes
            )
            result = results[0]
            if count % 90 == 0: 
                for cls_id, conf in zip(result.boxes.cls, result.boxes.conf): 
                    entity_id = str(uuid4())
                    entity = EntityContract(
                        entity_id=entity_id, 
                        class_name=self.model.names[int(cls_id)],
                        first_seen=datetime.datetime.now(),
                        last_seen=datetime.datetime.now(),
                        attributes={}
                    )

                    self._sql.add_entity(entity)
                    track_entity = TrackContract(
                        track_id=str(uuid4()), 
                        entity_id=entity_id,
                        start_time=datetime.datetime.now(), 
                        end_time=datetime.datetime.now(),
                        confidence=conf
                    )
                    self._sql.add_track(track_entity)
            count+=1
            annotated_frame = result.plot()
            cv2.imshow("Indoor Camera", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"): 
                break
        cap.release()
        cv2.destroyAllWindows()