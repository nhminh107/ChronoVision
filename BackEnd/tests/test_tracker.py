from BackEnd.tracker.yolo_tracker import Tracker
from BackEnd.Database.postgre_sql import Postgre_Manager

sql = Postgre_Manager()
sql.init_db()
tracker =Tracker(sql)
tracker.track(0)