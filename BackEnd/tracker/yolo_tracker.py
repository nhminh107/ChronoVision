import cv2
from ultralytics import YOLO
from BackEnd.Database.postgre_sql import Postgre_Manager
from pathlib import Path
import json
from BackEnd.Contract.data_contracts import (CameraContract, EntityContract, EventContract, TrackContract)
from uuid import uuid4
from collections import deque

import datetime


class Tracker: 
    def __init__(self, sql: Postgre_Manager = None):
        self._sql = sql
        self.model = YOLO("yolo26s-objv1-150.pt")
        config_path = Path.cwd() / "BackEnd" / "tracker" / "config.json"
        with config_path.open(encoding="utf-8") as config_file:
            self.classes = json.load(config_file)["classes"]
        self.q = deque(maxlen=300)
    def _is_exists_queue(self, id): 
        for track_id, track_id_key in self.q: 
            if track_id == id: 
                return track_id_key
        return False
        
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
                persist=True
            )
            result = results[0]
            
            if count % 150 == 0: 
                for track_id, conf, class_id in zip(result.boxes.id, 
                                                    result.boxes.conf, result.boxes.cls): 
                    isExists =  self._is_exists_queue(track_id)
                    if isExists:
                        self._sql.update_track(isExists, datetime.datetime.now())
                        continue
                    obj_id = str(uuid4())
                    entity = EntityContract(
                        entity_id=obj_id, 
                        class_name=self.model.names[int(class_id)],
                        first_seen=datetime.datetime.now(),
                        last_seen=datetime.datetime.now(),
                        attributes={}
                    )
                    self._sql.add_entity(entity)
                    obj_track_id = str(uuid4())
                    obj_track = TrackContract(
                        track_id=obj_track_id, 
                        entity_id=obj_id, 
                        start_time=datetime.datetime.now(),
                        end_time=datetime.datetime.now(),
                        confidence=conf
                    )
                    self._sql.add_track(obj_track)
                    self.q.append((result.boxes.id, obj_track_id))
                
            
            count+=1
            annotated_frame = result.plot()
            cv2.imshow("Indoor Camera", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"): 
                break
        cap.release()
        cv2.destroyAllWindows()