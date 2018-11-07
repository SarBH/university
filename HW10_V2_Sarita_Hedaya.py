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
    """ Class University imports data from .txt files, organizes such data into 
    dictionaries with classes, and prints them in prettytable format """
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.students = dict()  # self.students[cwid] = instance of class Student
        self.instructors = dict()  # self.instructors[cwid] = instance of class Instructor
        self._majors = dict() # self.majors[major] = instance of class major

        # Calls functions that import university data from files
        self.import_majors(dir_path)
        self.import_students(dir_path)
        self.import_instructors(dir_path)
        self.import_grades(dir_path)

    # Methods that import data from .txt files, and create instances of classes as values in dicitonaries
    def import_students(self, dir_path):
        """ Pulls student data from .txt file and organizes it into the students dictionary """
        students_file = os.path.join(dir_path, "students.txt")
        try:
            for cwid, name, major_name in file_reader(students_file, 3, '\t'):
                self.students[cwid] = Student(cwid, name, major_name, self._majors[major_name])
        except ValueError as e:
            print(e)

    def import_instructors(self, dir_path):
        """ Pulls instructor data from .txt file and organizes it into the instructors dictionary """
        instructors_file = os.path.join(dir_path, "instructors.txt")
        try:
            for cwid, name, department in file_reader(instructors_file, 3, '\t'):
                self.instructors[cwid] = Instructor(cwid, name, department)
        except ValueError as e:
            print(e)        

    def import_grades(self, dir_path):
        """ read the grades file, update the student to note the course and grade, update instructor to 
            note an additional student 
        """
        grades_file = os.path.join(dir_path, "grades.txt")
        try:
            for student_cwid, course, grade, instructor_cwid in file_reader(grades_file, 4, '\t'):
                self.students[student_cwid].add_course(course, grade) # adds dictionary entry pair. See def in class Student
                self.instructors[instructor_cwid].add_course(course) # adds a student to #students in course. See def in Instructor class.
        except ValueError as e:
            print(e)  
  
    def import_majors(self, dir_path):
        """ reads majors from file in dir_path and adds them to a dictionary self._majors """
        majors_file = os.path.join(dir_path, "majors.txt")
        try:
            for major, flag, course in file_reader(majors_file, 3, separator='\t', header=False):
                if major not in self._majors:
                    self._majors[major] = Major(major)

                self._majors[major].add_course(flag, course)
        except ValueError as e:
            print(e)

    # Print summary information as tables
    def student_prettytable(self):
        """ create a student pretty table with info the student and courses """
        student_prettytable = PrettyTable() # initialize pt
        student_prettytable.field_names = Student.pt_header(self) #set headers as defined in function inside Student class
        for student in self.students.values():
            student_prettytable.add_row(student.pt_row()) # add rows using the output of pt_row defined in Student class
        return student_prettytable

    def instructor_prettytable(self):
        """ create an instructor pretty table with info the instructor and courses """
        instructor_prettytable = PrettyTable()
        instructor_prettytable.field_names = Instructor.pt_header(self)
        for ins in self.instructors.values():
            for row in ins.pt_row():
                instructor_prettytable.add_row(row)
        return instructor_prettytable

    def major_prettytable(self):
        """ create a pretty table containing information of courses associated with majors """
        major_prettytable = PrettyTable() # initialize pt
        major_prettytable.field_names = Major.pt_header(self) #set headers as defined in function inside Student class
        for major in self._majors.values():
            major_prettytable.add_row(major.pt_row()) # add rows using the output of pt_row defined in Student class
        return major_prettytable


class Student:
    """ Keeps track of all information concerning students, 
    including what happens when a student takes a new course """
    def __init__(self, cwid, name, major_name, major):
        self.cwid = cwid
        self.name = name
        self.major_name = major_name
        self.major = major

        self.courses = dict()  # self.courses[course] = grade

    def add_course(self, course, grade):
        """ note that the student took a course and earned a grade """
        self.courses[course] = grade
             
    def pt_header(self):
        """ return a list of the fields in the prettytable """
        return ['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required', 'Remaining Electives']

    def pt_row(self):
        """ return the values for the students pretty table for self """
        completed_courses, remaining_required, remaining_electives = self.major.remaining(self.courses)
        return [self.cwid, self.name, self.major_name, completed_courses, remaining_required, remaining_electives]
        
            
class Instructor:
    """ Keeps track of all information concerning Instructors, 
    including what happens when a student takes a new course """
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


class Major:
    """ Track all the information regarding the major, inlcuding its required and elective courses """
    def __init__(self, department, passing=None):
        self._department = department
        self._required = set()
        self._electives = set()
        if passing is None:
            self.passing_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}
        else:
            self.passing_grades = passing

    def add_course(self, flag, course):
        """ notes another required course or elective """
        if flag.upper() == 'E':
            self._electives.add(course)
        elif flag.upper() == 'R':
            self._required.add(course)
        else:
            raise ValueError(f"Flag {flag} is invalid for course {course}")

    def pt_header(self):
        """ return a list of the fields in the prettytable """
        return ['Major', 'Required Courses', 'Elective Courses']

    def pt_row(self):
        """ returns the list of values that populate the prettytable for a specific major """
        return [self._department, self._required, self._electives]

    def remaining(self, courses):
        """ Calculate completed_courses, remaining_required, remaining_electives from 
        a dictionary of course=grade for a single student """
        completed_courses = {course for course, grade in courses.items() if grade in self.passing_grades}
        remaining_required = self._required - completed_courses
        if self._electives.intersection(completed_courses):
            remaining_electives = None
        else:
            remaining_electives = self._electives
        return completed_courses, remaining_required, remaining_electives


def main():
    stevens = University('G:\My Drive\F18\SSW-810\Week 10')
    print("Student Summary")
    student_summary = print(stevens.student_prettytable())
    print("Instructor Summary")
    instructor_summary = print(stevens.instructor_prettytable())
    print("Major Summary")
    major_summary = print(stevens.major_prettytable())


class UniversityTest(unittest.TestCase):
    def test_student_instance(self):
        """Tests several student instances by comparing the values in the instances to the correct values"""
        stevens = University('G:\My Drive\F18\SSW-810\Week 10')
        self.assertEqual(stevens.students['10175'].name, "Erickson, D")
        self.assertEqual(stevens.students['11461'].name, "Wright, U")
        self.assertEqual(stevens.students['11461'].courses, {'SYS 800': 'A', 'SYS 750': 'A-', 'SYS 611': 'A'})

    def test_instructor_instance(self):
        """Tests several instructor instances by comparing the values in the instances to the correct values"""
        stevens = University('G:\My Drive\F18\SSW-810\Week 10')
        self.assertEqual(stevens.instructors['98764'].name, "Feynman, R")
        self.assertEqual(stevens.instructors['98765'].name, "Einstein, A")
        self.assertEqual(stevens.instructors['98760'].courses, {'SYS 800': 1, 'SYS 750': 1, 'SYS 611': 2, 'SYS 645': 1})

    def test_major_instance(self):
        """ Tests Major instances to compare to the correct values """
        stevens = University('G:\My Drive\F18\SSW-810\Week 10')
        self.assertEqual(stevens._majors['SFEN']._required, {'SSW 540', 'SSW 555', 'SSW 564', 'SSW 567'})
        self.assertEqual(stevens._majors['SFEN']._electives, {'CS 501', 'CS 545', 'CS 513'})


if __name__ == '__main__':
    unittest.main(exit = False, verbosity = 2)
    main()
    
