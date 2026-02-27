import datetime
import os
import logging

class timetable:
    def __init__(self, name, timetables, start = None, end = None):
        if name in timetables:
            self._load(name)
        else:
            self._create_new(name, timetables, start, end)

    def _create_new(self, name:str, timetables: list, start: str, end: str): # Date formats - dd/mm/yyyy
        if name in timetables:
            raise Exception("ERROR: Timetable name already exists")
        
        self.directory = f"timetables/{name}"
        self.start_date = start
        self.end_date = end

        os.mkdir(self.directory)
        holidays = open(f"{self.directory}/holidays.txt", "w")
        holidays.close()

        with open(f"{self.directory}/metadata.txt", "a") as metadata: # Write start and end to metadata text file
            metadata.write(f"Start Date - {self.start_date}\n")
            metadata.write(f"End Date - {self.end_date}\n")


    def _load(self, name:str):    
        self.directory = f"timetables/{name}"

        self.subjects = os.listdir(f"{self.directory}")
        pointer = 0
        total = len(self.subjects)
        while pointer < total: # removes metadata from subjects list
            if self.subjects[pointer][-4:] == ".txt":
                self.subjects.pop(pointer)
                total -= 1
            else:
                pointer += 1

        with open(f"{self.directory}/metadata.txt", "r") as dates:
            start_date = dates.readline()[-11:-1]
            end_date = dates.readline()[-11:-1]
            self.start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
            self.end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")

        with open(f"{self.directory}/holidays.txt", "r") as holidays:
            dates = holidays.readlines()

        temp = []
        for i in dates:
            temp.append(i[:-1])

        self.holidays = temp

    def create_subject(self, subject_name: str, days: list): # Days format - [[Day of week, period, length (1 or 2)], ...]
        os.mkdir(f"{self.directory}/{subject_name}")
        os.mkdir(f"{self.directory}/{subject_name}/notes")

        with open(f"{self.directory}/{subject_name}/days.txt", "a") as days_file:
            for i in days:
                days_file.write(f"{i[0]} - {i[1]} - {i[2]}\n")

    def get_lessons(self):
        """
        1. Get current date,
        2. Get list of all lessons and lesson days of week,
        3. Get list of all lessons that should have taken place from timetable start to datetime.datetime.today() and generate lesson codes,
        4. Put lessons into 2D array - [[Lesson Date, Period, Subject, Lesson ID, Completed - "N"]],
        5. Order by date,
        6. Remove from above list all lessons taking place on holidays,
        7. Compare against lesson notes already made - make Completed = "Y",
        8. Return list of all notes,

        TODO: Split into multiple functions for improved readability
        """
        today = datetime.datetime.today()

        if today >= self.end_date:
            up_to = self.end_date
        else:
            up_to = today

        lessons = []

        for subject in self.subjects:
            lesson_times = []
            directory = f"{self.directory}/{subject}"

            with open(f"{directory}/days.txt", "r") as lesson_dates:
                temp = lesson_dates.readlines()

            for j in temp:
                j = j[:-1]
                j = j.split(" - ")
                lesson_times.append(j)

            for k in range((up_to - self.start_date).days):
                day_in_question = self.start_date + datetime.timedelta(days = k)
                day_of_week = day_in_question.strftime("%A")

                for l in range(len(lesson_times)):
                    if self.__query_day_in_lessons(day_of_week, lesson_times[l]):
                        lessons.append([f"{day_in_question.strftime("%d/%m/%Y")}", lesson_times[l][1], subject, lesson_times[l][2], "N"])
                        break

        # Moving on to ordering the list - lessons should now have a list of all lessons from timetable start to current day for all subjects

        counter = 0
        total = len(lessons)
        while counter < total: # Removes all lessons that take place within holidays
            if lessons[counter][0] in self.holidays:
                lessons.pop(counter)
                total -= 1
            else:
                counter += 1

        # Lessons list should now be a list of all lessons minus holidays
        counter = 0
        total = len(lessons)
        term = 1
        lesson_no = 1

        while counter < total: # Adds lesson identifiers to each lesson
            current_lesson_date = datetime.datetime.strptime(lessons[counter][0], "%d/%m/%Y")
            previous_lesson_date = datetime.datetime.strptime(lessons[counter-1][0], "%d/%m/%Y")

            current_subject = lessons[counter][2]
            previous_subject = lessons[counter-1][2]

            if current_subject != previous_subject and current_lesson_date <= previous_lesson_date:
                term = 1
                lesson_no = 1
            elif current_lesson_date >= previous_lesson_date + datetime.timedelta(days = 9):
                term += 1
                lesson_no = 1
            
            if lessons[counter][3] == "1":
                lessons[counter][3] = f"T{term}L{lesson_no}"
                lesson_no += 1
            elif lessons[counter][3] == "2":
                lessons[counter][3] = f"T{term}L{lesson_no} & T{term}L{lesson_no + 1}"
                lesson_no += 2
            counter += 1

        lessons.sort(reverse = True, key = self.lesson_sorting_algorithm, )

        count = 0
        total = len(lessons)
        while count < total:
            date = lessons[count][0]
            date = f"{date[0:2]}.{date[3:5]}.{date[-4:]}"
            lesson_path = f"{self.directory}/{lessons[count][2]}/notes/{date} - {lessons[count][3]}"
            if os.path.isdir(lesson_path): lessons[count][4] = "Y"
            count += 1

        self.lessons_list = lessons

        return self.lessons_list

    def _query_day_in_lessons(self, day: str, lessons_sub: list):
        if day in lessons_sub:
            return True
        
    def lesson_sorting_algorithm(self, list):
        date = list[0]
        period = list[1]
        return f"{date[-4:]}/{date[-7:-5]}/{date[0:2]} - {period}"


    def add_holiday(self, start: str, end: str):
        current = datetime.datetime.strptime(start, "%d/%m/%Y")
        end_date = datetime.datetime.strptime(end, "%d/%m/%Y")

        with open(f"{self.directory}/holidays.txt", "a") as holidays:
            while current <= end_date:
                holidays.write(f"{current.strftime("%d/%m/%Y")}\n")
                current = current + datetime.timedelta(days = 1)

    def add_lesson_notes(self, subject: str, ID: str, date:str, summary: list = None, impression: str = None, definitions: list = None, information: list = None):
        if subject not in self.subjects:
            raise Exception("ERROR: Subject not in subjects")
        
        date = f"{date[0:2]}.{date[3:5]}.{date[-4:]}"
        
        folder_directory = f"{self.directory}/{subject}/notes/{date} - {ID}"
        os.mkdir(folder_directory)

        if summary != None:
            with open(f"{folder_directory}/summary.txt", "w") as summary_file:
                for bullet in summary:
                    summary_file.write(f"{bullet}\n")

        if impression != None:
            with open(f"{folder_directory}/impression.txt", "w") as impression_file:
                impression_file.write(impression)

        if definitions != None:
            with open(f"{folder_directory}/definitions.txt", "a") as definition_file:
                for definition in definitions:
                    definition_file.write(f"{definition}\n")

        if information != None:
            with open(f"{folder_directory}/information.txt", "a") as information_file:
                for info in information:
                    information_file.write(f"{info}\n")

    def get_notes(self, subject: str, date: str, ID: str):
        date = f"{date[0:2]}.{date[3:5]}.{date[-4:]}"

        data = {
            "definitions" : [],
            "impression" : "",
            "information" : [],
            "summary" : []
        }

        directory = f"{self.directory}/{subject}/notes/{date} - {ID}"

        try:
            with open(f"{directory}/definitions.txt", "r") as definitions_file:
                temp_definitions = definitions_file.readlines()
            definitions = []
            for definition in temp_definitions:
                definitions.append(definition[:-1])

            data["definitions"] = definitions
        except: data["definitions"] = "ERROR"

        try:
            with open(f"{directory}/impression.txt", "r") as impression_file:
                impression = impression_file.readlines()

            data["impression"] = impression
        except: data["impression"] = "ERROR"

        try:
            with open(f"{directory}/information.txt", "r") as information_file:
                temp_information = information_file.readlines()
            information = []
            for info in temp_information:
                information.append(info[:-1])

            data["information"] = information
        except: data["information"] = "ERROR"

        try:
            with open(f"{directory}/summary.txt", "r") as summary_file:
                temp_summary = summary_file.readlines()
            summary = []
            for sums in temp_summary:
                summary.append(sums[:-1])

            data["summary"] = summary
        except: data["summary"] = "ERROR"

        return data
    
    def change_title(self, new_title: str): # TODO: Implement
        pass

    def change_dates(self, start_date: str = None, end_date: str = None): # TODO: Implement
        pass

    def edit_subject_lessons(self, subject: str, new_times: list): # TODO: Implement
        pass

    def delete_subject(self, subject: str): # TODO: Implement
        pass

    def edit_subject_name(self, old_name: str, new_name: str): # TODO: Implement
        pass
    
def get_subjects():
    return os.listdir("timetables")