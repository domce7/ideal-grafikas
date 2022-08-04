from icalendar import Calendar, Event
from datetime import datetime, tzinfo
from calendar import monthrange
from pathlib import Path
import unicodedata
import os
from numpy import fix
import pdfplumber

PAREIGOS_KURIU_KINTANTIS_DARBO_LAIKAS = [
    'apple specialistas', 'apple profesionalas', 'apple specialiste', 'apple profesionale']


def doWorkerNeedSchedule(jobTitle):
    if simplify(jobTitle.lower()) in PAREIGOS_KURIU_KINTANTIS_DARBO_LAIKAS:
        return True
    else:
        False


def path_to_main_directory():
    cwd = os.getcwd()
    return(cwd + "/schedules")


def write_ics_to_file(calendar, path, year, month, name):
    with open(f"{path}/{name}_{year}{month}.ics", 'wb') as my_file:
        my_file.write(calendar.to_ical())
    my_file.close()


def path_to_ics(path, year, month, name):
    return(f"{path}/{name}_{year}{month}.ics")


def has_number(string):
    string = str(string)
    if any(char.isdigit() for char in string):
        return True
    else:
       return False


def cleanArrayForWorkersThatDay(array):
    array = ([s.replace('-', '') for s in array])
    array = ([s.strip() for s in array])
    array = ([s.strip(',') for s in array])
    return array


def getNumberOfDaysInMonth(year: int, month: int) -> int:
    temp = monthrange(year, month)
    return temp[1]


def simplify(text):
    """Simplifies all special UTF-8 characters. (Finds and replaces them"""
    try:
       text = unicode(text, 'utf-8')
    except NameError:
       pass
    text = unicodedata.normalize('NFD', text).encode(
        'ascii', 'ignore').decode("utf-8")
    return str(text)


def createMailAddress(string: str) -> str:
    your_path = Path(string)
    name = simplify(your_path.stem)

    return(name.lower().replace(" ", ".") + '@ideal.lt')


def getDataFromPDF(path: str) -> list:
    """ Given a path to a pdf file, a table is found and returned as a 2D list,
    using a library called pdfplumber """
    pdf = pdfplumber.open(path)
    page = pdf.pages[0]

    return page.extract_table()


def removeWhiteSpaceAndNone(array: list) -> list:
    """ Removes rows where first value is None or an empty space."""
    cleanedArray = []
    for sublist in array:
        # ---------- If first value of the row is None or '', we ignore it.
        if sublist[0] is not None and sublist[0] != '':
            # ---------- Only add values to temp array if they are not None.
            tempArray =  [x for x in sublist if x]

            cleanedArray.append(tempArray)
    return cleanedArray


def shortRowRemoval(array: list) -> list:
    """ Returns a list without short rows.
        Short row is smaller in lenght than 30."""
    cleanedArray = []
    for sublist in array:
        if len(sublist) > 30:
            cleanedArray.append(sublist)

    return cleanedArray


def removeFirstRow(array: list) -> list:
    """the first row is a table header, so it is removed. """
    del array[0]
    return array


def arrayCleaningWrapper(array: list) -> list:
    return removeFirstRow(shortRowRemoval(removeWhiteSpaceAndNone(array)))


class Worker():
    all = []
    completionMessage = ''
    # ------------ [ [name, email, completionMessage, path], ... ]
    displayInformationArray = []

    whoWorksThatDay = [''] * 32

    targetYear = None
    targetMonth = None

    def __init__(self, name, workHourArray):

        self.name = name
        self.workHourArray = workHourArray
        self.whoWorksThatDayByName = [self.name if has_number(
             item) else '-' for item in self.workHourArray]

        # ---------------- Executing after values are initialized. -------
        Worker.all.append(self)

        Worker.whoWorksThatDay = [str(
             i) + ", " + j for i, j in zip(Worker.whoWorksThatDay, self.whoWorksThatDayByName)]
        Worker.whoWorksThatDay = cleanArrayForWorkersThatDay(
             Worker.whoWorksThatDay)

    @classmethod
    def name_list(self):
        return [item.name for item in Worker.all]

    @ classmethod
    def clean_list(self):
        Worker.all.clear()
        Worker.displayInformationArray.clear()

    @ classmethod
    def magicWrapper(cls, path, year, month):
        Worker.initiate_from_pdf(path, year, month)
        return Worker.do_ics()

    @ classmethod
    def initiate_from_pdf(cls, path, year, month):
        """
        Initiates values feeded from a view and submitted by a user.
        The values submitted are:
            1. PDF file
            2. Year, Month (Date values year and month are used to know for
            which month the schedule is being made.)

        A variable -> dataFromPdf is a 2D array.
        """

        dataFromPDF = getDataFromPDF(path)
        cleanedDataFromPDF = arrayCleaningWrapper(dataFromPDF)

        Worker.targetYear = year
        Worker.targetMonth = month

        # ---------- We delete the pdf file submitted by the user.
        os.remove(path)

        for sublist in cleanedDataFromPDF:
            if not doWorkerNeedSchedule(sublist[1]):
                continue
            Worker(
                name=sublist[0],
                workHourArray=sublist[-getNumberOfDaysInMonth(year, month):]
                )

    @ classmethod
    def do_ics(self):
        paths = []
        # Iterate with every worker in the list
        for worker in Worker.all:
            full_schedule = Calendar()
            Worker.completionMessage = "Sėkminga!"
            tempArray = [worker.name, createMailAddress(worker.name)]
            # when adding to icalendar, yyyy/mm/dd | dd is date_day_counter
            for date_day_counter, working_day in enumerate(worker.workHourArray):
                try:
                    # all days when you have to go to work will include a digit. if there are no digits you have a day off
                    if not has_number(working_day):
                        continue
                    # If you are working, the working hours are written in this format: 10-18, 10-22 and so on
                    work_shift = working_day.split('-')

                    event = Event()
                    event.add('summary', 'Darbas iDeal')
                    event.add('description',
                              f"Dirba: {Worker.whoWorksThatDay[date_day_counter]}")

                    event.add('dtstart', datetime(int(Worker.targetYear), int(
                             Worker.targetMonth), date_day_counter+1, int(work_shift[0]), 0, 0, tzinfo=None)
                    )

                    event.add(
                        'dtend', datetime(int(Worker.targetYear), int(
                             Worker.targetMonth), date_day_counter+1, int(work_shift[1]), 0, 0, tzinfo=None)
                    )
                    full_schedule.add_component(event)

                except ValueError:
                    Worker.completionMessage = f"Rasta nesitikėta reikšmė {date_day_counter + 1}d."

            tempArray.append(Worker.completionMessage)

            write_ics_to_file(full_schedule, path_to_main_directory(
            ), self.targetYear, self.targetMonth, worker.name)

            tempArray.append(path_to_ics(path_to_main_directory(),
                         Worker.targetYear, Worker.targetMonth, worker.name))

            Worker.displayInformationArray.append(tempArray)
