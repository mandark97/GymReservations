import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

MONTH_MAPPING = {
    "Ianuarie": "01",
    "Februarie": "02",
    "Martie": "03",
    "Aprilie": "04",
    "Mai": "05",
    "Iunie": "06",
    "Iulie": "07",
    "August": "08",
    "Septembrie": "09",
    "Octombrie": "10",
    "Noiembrie": "11",
    "Decembrie": "12"
}


@dataclass
class GymClass():
    club_id: str
    class_id: Optional[str]
    start_hour: datetime
    class_name: str
    instructor: str
    class_location: str
    reservation_start: Optional[datetime]

    def __init__(self, club_id, tag, hours, class_name, instructor, class_location, reservation_start=None):
        self.club_id = club_id
        self.tag = tag
        self.start_hour = self.__hours(hours)
        self.class_name = class_name
        self.instructor = instructor
        self.class_location = class_location
        if reservation_start:
            self.reservation_start = self.__process_reservation_date(reservation_start)
        else:
            self.reservation_start = None

        self.class_id = self.__class_id()

    def __hours(self, hours) -> datetime:
        start_hour, end_hour = hours.split(" - ")

        return datetime.strptime(start_hour, "%H:%M")

    def __class_id(self):
        book_button = self.tag.find(class_="btn-book-class")
        if book_button:
            return book_button.attrs['data-target'].split('-')[1]
        else:
            return None

    def __process_reservation_date(self, reservation_date):
        p = re.compile("Rezervarile se deschid la ora ([0-9:]+,[a-zA-z 0-9]+)")
        matches = p.match(reservation_date)
        if matches == None:
            return None
        reservation_date = matches.group(1)

        for k, v in MONTH_MAPPING.items():
            reservation_date = reservation_date.replace(k, v)

        date = datetime.strptime(reservation_date, "%H:%M, %d %m")
        date = date.replace(year=datetime.today().year)

        return date

    @staticmethod
    def create_gym_class(club_id, class_tag):
        return GymClass(club_id, class_tag, *list(filter(None, re.split("\n|\t", class_tag.text))))
