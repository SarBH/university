from collections import defaultdict
from prettytable import PrettyTable
import os
import unittest


def file_reader(file_name, fields_per_line, separator=',', header=False):
    """this generator returns all the values of a line on each call to next()"""
    try:
        fp = open(file_name, 'r') # Do the risky action of attempting to open a file
    except FileNotFoundError:
        print("can't open", file_name) # If file not found, raise exception
    else: # If the file is found
        with fp:
            line_number = 1 # Start line counter to identify line that raises ValueError
            next_line = [] # Initialize next_line variable to store the line in question
            
            for line in fp:
                line = line.rstrip('\n\r').split(separator) # Strips the \n and/or \r from the end of the line and Separates the line into values using the separator
                if len(line) != fields_per_line:
                    raise ValueError(file_name, "has", len(line), "fields in", line_number, "but expected", fields_per_line)
                for value in line: 
                    next_line.append(value)
                
                line = next_line # Transfer the values into line, so we can empty and reuse next_line
                next_line = [] # Before yielding, we must empty next_line for future use
                line_number += 1 # Increase the line counter by 1
                if header == True: # If there is a header, skip that line. 
                    header = False # Set header=False so later lines don't get skipped
                    continue
                yield tuple(line)


class University:
    def __init__(self, dir_path):
        self.dir_path = dir_path

        self.students = dict()  # self.students[cwid] = instance of class Student
        self.instructors = dict()  # self.instructors[cwid] = instance of class Instructor

        #Calls to functions defined below
        self.import_students(dir_path)
        self.import_instructors(dir_path)
        self.import_grades(dir_path)

        self.instructor_prettytable()
        self.student_prettytable()
        
        self.instructor_row_print()
        self.student_row_print()

    # Functions defined in class University
    def import_students(self, dir_path):
        """ Pulls student data from .txt file and organizes it into the students dictionary """
        students_file = os.path.join(dir_path, "students.txt")
        for cwid, name, major in file_reader(students_file, 3, '\t'):
            self.students[cwid] = Student(cwid, name, major)

    def import_instructors(self, dir_path):
        """ Pulls instructor data from .txt file and organizes it into the instructors dictionary """
        instructors_file = os.path.join(dir_path, "instructors.txt")
        for cwid, name, department in file_reader(instructors_file, 3, '\t'):
            self.instructors[cwid] = Instructor(cwid, name, department)

    def import_grades(self, dir_path):
        """ read the grades file, update the student to note the course and grade, update instructor to 
            note an additional student 
        """
        grades_file = os.path.join(dir_path, "grades.txt")
        for student_cwid, course, grade, instructor_cwid in file_reader(grades_file, 4, '\t'):
            self.students[student_cwid].add_course(course, grade) # adds dictionary entry pair. See def in class Student
            self.instructors[instructor_cwid].add_course(course) # adds a student to #students in course. See def in Instructor class.

    def student_prettytable(self):
        """ create a student pretty table with info the student and courses """
        student_prettytable = PrettyTable() # initialize pt
        student_prettytable.field_names = Student.pt_header(self) #set headers as defined in function inside Student class
        for student in self.students.values():
            student_prettytable.add_row(student.pt_row()) # add rows using the output of pt_row defined in Student class
        return(student_prettytable)

    def instructor_prettytable(self):
        """ create an instructor pretty table with info the instructor and courses """
        instructor_prettytable = PrettyTable()
        instructor_prettytable.field_names = Instructor.pt_header(self)
        for ins in self.instructors.values():
            for row in ins.pt_row():
                instructor_prettytable.add_row(row)
        return(instructor_prettytable)

    #The four functions below makes each row a list of strings, and returns a list of lists (rows).
    def student_row_gen(self):
        """This generator yields each row of the pretty table as a list of strings""" 
        for row in self.student_prettytable(): # remove border and header from the pt
            row.border = False
            row.header = False
            row = row.get_string() # convert pt into a string
            row = row.strip(" ").split("  ") # separate into list values         
            yield row

    def student_row_print(self):
        """This function appends each list yielded from the student_row_gen generator into a larger list"""
        rows = list()
        for row in self.student_row_gen():
            rows.append(row) # append rows into rows list
        return(rows)

    def instructor_row_gen(self):
        """This generator yields each row of the instructor pretty table as a list of strings"""
        for row in self.instructor_prettytable(): # remove border and header from the pt
            row.border = False
            row.header = False
            row = row.get_string() # convert pt into a string
            row = row.strip(" ").split("  ") # separate into list values  
            yield row

    def instructor_row_print(self):
        """This function appends each list yielded from the instructor_row_gen generator into a larger list"""
        rows = list()
        for row in self.instructor_row_gen():
            rows.append(row) # append rows into rows list
        return(rows)
            

class Student:
    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.major = major
        self.name = name
        self.courses = dict()  # self.courses[course] = grade

    def add_course(self, course, grade):
        """ note that the student took a course and earned a grade """
        self.courses[course] = grade
             
    def pt_header(self):
        """ return a list of the fields in the prettytable """
        return ['CWID', 'Name', 'Completed Courses']

    def pt_row(self):
        """ return the values for the students pretty table for self """
        return [self.cwid, self.name, sorted(self.courses.keys())]
        
            
class Instructor:
    def __init__(self, cwid, name, department):
        self.cwid = cwid
        self.department = department
        self.name = name
        self.courses = defaultdict(int)  # self.courses[course] = number of students

    def add_course(self, course):
        """ tell the instructor that she taught a student in a course """
        self.courses[course] += 1

    def pt_header(self):
        return ['CWID', 'Name', 'Department', 'Course', '#Students']

    def pt_row(self):
        """ a generator to return the rows with course and number of students """
        for course, students in self.courses.items():
            yield [self.cwid, self.name, self.department, course, students]


def main():
    stevens = University('G:\My Drive\F18\SSW-810\Week 9')
    print("Student Summary")
    student_summary = print(stevens.student_prettytable())
    print("Instructor Summary")
    instructor_summary = print(stevens.instructor_prettytable())


class UniversityTest(unittest.TestCase):
    def test_student_data(self):
        """Tests the student data by comparing a formatted version 
        of the PrettyTable's output to correct values
        """
        stevens = University('G:\My Drive\F18\SSW-810\Week 9')
        self.assertEqual(stevens.student_row_print(), [['10103', 'Baldwin, C', "['CS 501', 'SSW 564', 'SSW 567', 'SSW 687']"], 
        ['10115', 'Wyatt, X', "['CS 545', 'SSW 564', 'SSW 567', 'SSW 687']"], ['10172', 'Forbes, I', "['SSW 555', 'SSW 567']"], 
        ['10175', 'Erickson, D', "['SSW 564', 'SSW 567', 'SSW 687']"], ['10183', 'Chapman, O', "['SSW 689']"], 
        ['11399', 'Cordova, I', "['SSW 540']"], ['11461', 'Wright, U', "['SYS 611', 'SYS 750', 'SYS 800']"], 
        ['11658', 'Kelly, P', "['SSW 540']"], ['11714', 'Morton, A', "['SYS 611', 'SYS 645']"], ['11788', 'Fuller, E', "['SSW 540']"]])

    def test_instructor_data(self):
        """Tests the instructor data by comparing a formatted version 
        of the PrettyTable's output to correct values
        """
        stevens = University('G:\My Drive\F18\SSW-810\Week 9')
        self.assertEqual(stevens.instructor_row_print(), [['98765', 'Einstein, A', 'SFEN', 'SSW 567', '4'], 
        ['98765', 'Einstein, A', 'SFEN', 'SSW 540', '3'], ['98764', 'Feynman, R', 'SFEN', 'SSW 564', '3'], 
        ['98764', 'Feynman, R', 'SFEN', 'SSW 687', '3'], ['98764', 'Feynman, R', 'SFEN', 'CS 501', '1'], 
        ['98764', 'Feynman, R', 'SFEN', 'CS 545', '1'], ['98763', 'Newton, I', 'SFEN', 'SSW 555', '1'], 
        ['98763', 'Newton, I', 'SFEN', 'SSW 689', '1'], ['98760', 'Darwin, C', 'SYEN', 'SYS 800', '1'], 
        ['98760', 'Darwin, C', 'SYEN', 'SYS 750', '1'], ['98760', 'Darwin, C', 'SYEN', 'SYS 611', '2'], 
        ['98760', 'Darwin, C', 'SYEN', 'SYS 645', '1']])

    def test_student_instance(self):
        """Tests several student instances by comparing the values in the instances to the correct values"""
        stevens = University('G:\My Drive\F18\SSW-810\Week 9')
        self.assertEqual(stevens.students['10175'].name, "Erickson, D")
        self.assertEqual(stevens.students['11461'].name, "Wright, U")
        self.assertEqual(stevens.students['11461'].courses, {'SYS 800': 'A', 'SYS 750': 'A-', 'SYS 611': 'A'})

    def test_instructor_instance(self):
        """Tests several instructor instances by comparing the values in the instances to the correct values"""
        stevens = University('G:\My Drive\F18\SSW-810\Week 9')
        self.assertEqual(stevens.instructors['98764'].name, "Feynman, R")
        self.assertEqual(stevens.instructors['98765'].name, "Einstein, A")
        self.assertEqual(stevens.instructors['98760'].courses, {'SYS 800': 1, 'SYS 750': 1, 'SYS 611': 2, 'SYS 645': 1})


if __name__ == '__main__':
    unittest.main(exit = False, verbosity = 2)
    main()
    
