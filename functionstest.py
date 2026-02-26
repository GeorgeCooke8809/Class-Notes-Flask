import os
import functions

while True:
    timetables = os.listdir("timetables") # gives a list of all stored timetables

    print("0 - Create Timetable")

    for i in range(len(timetables)):
        print(f"{i+1} - {timetables[i]}")

    choice = int(input()) - 1

    print()

    if choice == -1: # Create new timetable
        accept_timetable = False
        while not accept_timetable:
            name = input("Timetable Name: ")

            if name not in timetables:
                accept_timetable = True

        start_date = input("Start Date (dd/mm/yyyy): ")
        end_date = input("End Date (dd/mm/yyyy): ")

        active_timetable = functions.timetable(name, timetables, start_date, end_date)

        # Moving on to creating subjects

        print("\nCreate Subjects - Press 0 to exit:")

        running = True

        while running:
            name = input("Subject Name: ")
            if name == "0":
                running = False
                break
            print("\nEnter Lessons:")

            days = []

            adding_days = 1

            while adding_days != 0:
                print(f"\nLesson {adding_days}: ")
                day = input("Day of Week: ")
                if day == "0": 
                    adding_days = 0
                    break

                period = input("Period: ")
                if period == "0": 
                    adding_days = 0
                    break

                length = input("Number of Lessons Long: ")
                if length == "0":
                    adding_days = 0
                    break

                days.append([day, period, length])
                adding_days += 1

            active_timetable.create_subject(name, days)
    else:
        active_timetable = functions.timetable(name = timetables[choice], timetables = timetables)
        print("0 - Add Holiday")
        print("1 - Add Subject")

        choice = input("Choice: ")

        if choice == "0":
            start_date = input("Start Date (dd/mm/yyyy): ")
            end_date = input("End Date (dd/mm/yyyy): ")

            active_timetable.add_holiday(start_date, end_date)

        elif choice == "1":
            pass

        lessons = active_timetable.get_lessons()

        for lesson in lessons: print(lesson)

    print()