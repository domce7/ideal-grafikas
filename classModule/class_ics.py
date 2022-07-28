from datetime import datetime, tzinfo
import unicodedata
import pandas as pd
from icalendar import Calendar, Event
import pathlib
import os
import re

PAREIGOS_KURIU_KINTANTIS_DARBO_LAIKAS = ['Apple specialistas', 'Apple Profesionalas'] # prideti mot. g.

class Worker():
    all = []
    who_is_working = [''] * 32

    def __init__(self, name: str, pareigos: str, darbo_dienu_sk: int, darbo_valandu_sk: int, netvarkytas_darbo_grafikas):

        self.name = name
        self.pareigos = pareigos
        self.darbo_dienu_sk = darbo_dienu_sk
        self.darbo_valandu_sk = darbo_valandu_sk
        self.netvarkytas_darbo_grafikas = netvarkytas_darbo_grafikas
        self.darbo_dienos = [self.name if has_number(item) else '-' for item in self.netvarkytas_darbo_grafikas]

        # Executing actions
        Worker.all.append(self)

        Worker.who_is_working = [str(i) + ", " + j for i, j in zip(Worker.who_is_working, self.darbo_dienos)]
        Worker.who_is_working = clean_array(Worker.who_is_working)

    @classmethod
    def clean_list(self):
        Worker.all.clear()

    @classmethod
    def initiate_from_excel(cls, path):
        """ """
        list = remove_garbage(pd.read_excel(path))

        for item in list:
            Worker(
                name=item[0],
                pareigos=item[1],
                darbo_dienu_sk=item[2],
                darbo_valandu_sk=item[3],
                netvarkytas_darbo_grafikas=item[7:],
            )
        print(Worker.all)

    def __repr__(self):
        return(
            f"Worker({self.name}, {self.pareigos},  {self.darbo_dienu_sk}, {self.darbo_valandu_sk}, {self.netvarkytas_darbo_grafikas})"
        )

    @classmethod
    def name_list(self):
        return [item.name for item in Worker.all]

    @classmethod
    def do_ics(self, year, month):
        year = int(year)
        month = int(month)
        paths = []
        # Iterate with every worker in the list
        for worker in Worker.all:
            full_schedule = Calendar()
            # when adding to icalendar, yyyy/mm/dd | dd is date_day_counter
            for date_day_counter, working_day in enumerate(worker.netvarkytas_darbo_grafikas):
                # all days when you have to go to work will include a digit. if there are no digits you have a day off
                if not has_number(working_day):
                    continue
                # If you are working, the working hours are written in this format: 10-18, 10-22 and so on
                work_shift = working_day.split('-')

                event = Event()
                event.add('summary', 'Darbas iDeal')
                event.add('description', f"Dirba: {Worker.who_is_working[date_day_counter]}")


                event.add(
                    'dtstart', datetime(int(year), int(month), date_day_counter+1, int(work_shift[0]), 0, 0, tzinfo=None)
                )

                event.add(
                    'dtend', datetime(int(year), int(month), date_day_counter+1, int(work_shift[1]), 0, 0, tzinfo=None)
                )
                full_schedule.add_component(event)

            write_ics_to_file(full_schedule, create_main_directory(),year, month, worker.name)
            paths.append(path_to_ics(path_to_main_directory(),year, month, worker.name))
        return paths


def remove_garbage(dataframe):
    # Removes everything except worker schedule lines.

    # Code to remove not needed columns and rows.
    # Works fine with four tested months
    dataframe = dataframe.dropna(subset=['Unnamed: 1'])
    dataframe = dataframe.dropna(axis=1, how='all')

    # Converting df rows to list
    temporyList = dataframe.values.tolist()

    completeList = []

    for x in temporyList:
        if (re.match("[a-zA-Z]+\s[a-zA-Z]+", simplify(str(x[0]))) 
        and ('Darbo dienos' not in str(x[0])) 
        and x[1] in PAREIGOS_KURIU_KINTANTIS_DARBO_LAIKAS):
            completeList.append(x)

    return completeList

def has_number(string):
    string = str(string)
    if any(char.isdigit() for char in string):
        return True
    else:
       return False

def simplify(text):
	try:
		text = unicode(text, 'utf-8')
	except NameError:
		pass
	text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
	return str(text)

def create_main_directory():
    # If not created - creates a directory to store all the schedules for all months.
    # AND returns path to it
    cwd = os.getcwd()
    pathlib.Path(
        cwd + "/schedules").mkdir(parents=True, exist_ok=True
    )
    return(cwd + "/schedules")

def path_to_main_directory():
     cwd = os.getcwd()
     return(cwd + "/schedules")

def write_ics_to_file(calendar, path, year, month, name):
    is_directory_created(year, month)

    with open(f"{path}/{str(year)}_{month}/{name}.ics", 'wb') as my_file:
        my_file.write(calendar.to_ical())
    my_file.close()

def path_to_ics(path, year, month, name):
    return(f"{path}/{str(year)}_{month}/{name}.ics")

def is_directory_created(year, month):
    # Checks if a directory exists.
    # If not creates it
        cwd = os.getcwd()
        pathlib.Path(
            cwd + f"/schedules/{str(year)}_{month}").mkdir(parents=True, exist_ok=True
        )

def remove_dash(array):
    return ([s.replace('-', '') for s in array])

def remove_border_whitespace(array):
    return ([s.strip() for s in array])

def remove_last_comma(array):
    return ([s.strip(',') for s in array])

def clean_array(array):
    array = ([s.replace('-', '') for s in array])
    array = ([s.strip() for s in array])
    array = ([s.strip(',') for s in array])
    return array