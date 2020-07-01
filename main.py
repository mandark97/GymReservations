import logging
import os
from datetime import datetime

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from pytz import timezone

from gym_class import GymClass
from reservation_manager import ReservationManager

load_dotenv(verbose=True)
scheduler = BlockingScheduler({'apscheduler.timezone': timezone("Europe/Bucharest")})

CLUB_ID = os.getenv("CLUB_ID")
CLASS_NAME = os.getenv("CLASS_NAME")

logging.basicConfig(filename="test.log")
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


def schedule_events():
    upcoming_classes = ReservationManager({"club_id": CLUB_ID, "class_name": CLASS_NAME, "hour": 18}).upcoming_classes()
    for cls in upcoming_classes:
        scheduler.add_job(book_class, DateTrigger(cls.reservation_start), [cls])
    scheduler.print_jobs()


def book_class(cls: GymClass):
    reservation_manager = ReservationManager({"club_id": "447", "class_name": cls.class_name})
    reservation_manager.book_class()


def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')
        scheduler.print_jobs()


scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

scheduler.add_job(schedule_events, IntervalTrigger(weeks=1, start_date=datetime.now()))
scheduler.add_job(schedule_events, DateTrigger(datetime.now()))
print("Starting Scheduler")
scheduler.print_jobs()
scheduler.start()
