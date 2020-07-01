import os
from typing import List

import mechanicalsoup

from gym_class import GymClass


class ReservationManager(object):
    CYCLING = "class-type-1"
    SWIMMING = "class-type-2"  # not sure
    AEROBIC = "class-type-3"

    def __init__(self, configs):
        self.EMAIL = os.getenv("EMAIL")
        self.PASSWORD = os.getenv("PASSWORD")

        self.LOGIN_PAGE = os.getenv("LOGIN_PAGE")
        self.SCHEDULE_PAGE = os.getenv("SCHEDULE_PAGE")
        self.BOOKING_LINK = os.getenv("BOOKING_LINK")

        self.browser = mechanicalsoup.StatefulBrowser()
        self.configs = configs

    def login(self):
        print("Starting login")
        self.browser.open(self.LOGIN_PAGE)
        self.browser.select_form("form[class='form-signin']")
        self.browser["email"] = self.EMAIL
        self.browser["member_password"] = self.PASSWORD
        self.browser.submit_selected()
        print("Successful login?")

    def select_club(self):
        self.browser.open(self.SCHEDULE_PAGE)
        currently_selected = self.browser.get_current_page().find("option", {"selected": "selected"})
        print(f"Club currently selected {currently_selected.text}")
        if currently_selected["value"] == self.configs["club_id"]:
            return

        form: mechanicalsoup.Form = self.browser.select_form("form[id='clubs-form']")
        form.set_select({"clubid": self.configs["club_id"]})
        self.browser.submit_selected()

        currently_selected = self.browser.get_current_page().find("option", {"selected": "selected"})
        print(f"New club selected {currently_selected.text}")
        assert currently_selected["value"] == self.configs["club_id"]

    def get_classes(self, class_type: str = None) -> List[GymClass]:
        self.browser.open(self.SCHEDULE_PAGE)
        page = self.browser.get_current_page()
        assert page.find(id="schedule-container")
        classes = page.find_all("div", class_=class_type or "schedule-class")

        return list(map(lambda x: GymClass.create_gym_class(club_id=self.configs["club_id"], class_tag=x), classes))

    @staticmethod
    def filter_active_classes(classes: List[GymClass]) -> List[GymClass]:
        active_classes = filter(lambda cls: cls.tag.find(class_="btn-book-class"), classes)

        return list(active_classes)

    @staticmethod
    def filter_upcoming_classes(classes: List[GymClass]) -> List[GymClass]:
        upcoming_classes = filter(lambda cls: len(cls.tag.find_all("br")) == 2, classes)

        return list(upcoming_classes)

    @staticmethod
    def filter_by_hour(classes: List[GymClass], hour) -> List[GymClass]:
        return list(filter(lambda cls: cls.start_hour.hour >= hour, classes))

    @staticmethod
    def filter_by_name(classes: List[GymClass], name: str) -> List[GymClass]:
        return list(filter(lambda x: x.class_name == name, classes))

    def filter(self, classes: List[GymClass]) -> List[GymClass]:
        if "class_name" in self.configs:
            classes = self.filter_by_name(classes, self.configs["class_name"])
        if "hour" in self.configs:
            classes = self.filter_by_hour(classes, self.configs["hour"])

        return classes

    def book_active_class(self, active_class: GymClass) -> bool:
        book_class_link = self.BOOKING_LINK.format(active_class.class_id, active_class.club_id)
        self.browser.open(book_class_link)
        alert = self.browser.get_current_page().find(class_="alert alert-x-danger")

        if alert and alert.text == "Clasa indisponibila":
            print("failed to reserve")
            return False
        else:
            print("tbd maybe reserved")
            return True

    def upcoming_classes(self) -> List[GymClass]:
        self.login()
        self.select_club()
        classes = self.get_classes()
        upcoming_classes = self.filter_upcoming_classes(classes)
        upcoming_classes = self.filter(upcoming_classes)

        return upcoming_classes

    def book_class(self):
        self.login()
        self.select_club()
        classes = self.get_classes()
        active_classes = self.filter_active_classes(classes)
        active_classes = self.filter(active_classes)

        self.book_active_class(active_classes[0])
