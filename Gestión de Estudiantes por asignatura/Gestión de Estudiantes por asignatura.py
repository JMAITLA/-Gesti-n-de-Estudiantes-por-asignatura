from abc import ABC, abstractmethod

# --- 1. OperationResult Class ---
class OperationResult:
    def __init__(self, success: bool, message: str, data=None):
        self.success = success
        self.message = message
        self.data = data

# --- 2. Student Hierarchy (Inheritance and Polymorphism) ---
class Student(ABC): # Abstract Base Class
    def __init__(self, student_id: str, name: str):
        self.student_id = student_id
        self.name = name

    @abstractmethod
    def display_info(self):
        pass # To be implemented by subclasses

class OnsiteStudent(Student):
    def __init__(self, student_id: str, name: str):
        super().__init__(student_id, name)

    def display_info(self):
        return f"Student ID: {self.student_id}, Name: {self.name} (Type: Onsite)"

class RemoteStudent(Student):
    def __init__(self, student_id: str, name: str, connection_platform: str):
        super().__init__(student_id, name)
        self.connection_platform = connection_platform

    def display_info(self):
        return (f"Student ID: {self.student_id}, Name: {self.name} "
                f"(Type: Remote, Platform: {self.connection_platform})")

# --- 3. Grade Class ---
class Grade:
    def __init__(self, assessment_name: str, score: float):
        if not (0 <= score <= 100):
            raise ValueError("Score must be between 0 and 100.")
        self.assessment_name = assessment_name
        self.score = score

# --- 4. Group Class ---
class Group:
    def __init__(self, group_name: str):
        self.group_name = group_name
        self.students: list[Student] = []
        self.grades_by_student: dict[str, list[Grade]] = {} # student_id -> list of Grade objects

    def add_student(self, student: Student) -> OperationResult:
        if any(s.student_id == student.student_id for s in self.students):
            return OperationResult(False, f"Student with ID {student.student_id} already exists in group {self.group_name}.")
        self.students.append(student)
        self.grades_by_student[student.student_id] = []
        return OperationResult(True, f"Student {student.name} added to group {self.group_name}.")

    def find_student(self, student_id: str) -> Student | None:
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def register_grade(self, student_id: str, assessment_name: str, score: float) -> OperationResult:
        student = self.find_student(student_id)
        if not student:
            return OperationResult(False, f"Student with ID {student_id} not found in group {self.group_name}.")
        try:
            grade = Grade(assessment_name, score)
            self.grades_by_student[student_id].append(grade)
            return OperationResult(True, f"Grade {score} for {assessment_name} registered for {student.name}.")
        except ValueError as e:
            return OperationResult(False, f"Error registering grade: {e}")

    def get_student_average_grade(self, student_id: str) -> OperationResult:
        if student_id not in self.grades_by_student or not self.grades_by_student[student_id]:
            return OperationResult(False, f"No grades found for student ID {student_id} in group {self.group_name}.", 0.0)
        
        grades = self.grades_by_student[student_id]
        total_score = sum(g.score for g in grades)
        average = total_score / len(grades)
        return OperationResult(True, f"Average grade for student {student_id} calculated.", average)

    def show_grades_list(self) -> OperationResult:
        if not self.students:
            return OperationResult(False, f"No students in group {self.group_name}.")
        
        report = []
        report.append(f"--- Grades for Group: {self.group_name} ---")
        for student in self.students:
            report.append(student.display_info())
            grades = self.grades_by_student.get(student.student_id, [])
            if grades:
                report.append("  Grades:")
                for grade in grades:
                    report.append(f"    - {grade.assessment_name}: {grade.score}")
                avg_result = self.get_student_average_grade(student.student_id)
                if avg_result.success:
                    report.append(f"    Average: {avg_result.data:.2f}")
            else:
                report.append("  No grades registered yet.")
            report.append("-" * 30)
        return OperationResult(True, "Grade list generated.", "\n".join(report))

    def calculate_approved_percentage(self) -> OperationResult:
        if not self.students:
            return OperationResult(False, f"No students in group {self.group_name}.", 0.0)
        
        approved_students_count = 0
        for student in self.students:
            avg_result = self.get_student_average_grade(student.student_id)
            if avg_result.success and avg_result.data >= 70:
                approved_students_count += 1
        
        percentage = (approved_students_count / len(self.students)) * 100
        return OperationResult(True, f"Approved percentage for group {self.group_name} calculated.", percentage)

# --- 5. Course Class ---
class Course:
    def __init__(self, course_name: str, course_code: str):
        self.course_name = course_name
        self.course_code = course_code
        self.groups: list[Group] = []

    def add_group(self, group: Group) -> OperationResult:
        if any(g.group_name == group.group_name for g in self.groups):
            return OperationResult(False, f"Group {group.group_name} already exists in course {self.course_name}.")
        self.groups.append(group)
        return OperationResult(True, f"Group {group.group_name} added to course {self.course_name}.")

    def find_group(self, group_name: str) -> Group | None:
        for group in self.groups:
            if group.group_name == group_name:
                return group
        return None

    def add_student_to_group(self, group_name: str, student: Student) -> OperationResult:
        group = self.find_group(group_name)
        if not group:
            return OperationResult(False, f"Group {group_name} not found in course {self.course_name}.")
        return group.add_student(student)

    def register_grade_in_group(self, group_name: str, student_id: str, assessment_name: str, score: float) -> OperationResult:
        group = self.find_group(group_name)
        if not group:
            return OperationResult(False, f"Group {group_name} not found in course {self.course_name}.")
        return group.register_grade(student_id, assessment_name, score)

    def show_group_grades(self, group_name: str) -> OperationResult:
        group = self.find_group(group_name)
        if not group:
            return OperationResult(False, f"Group {group_name} not found in course {self.course_name}.")
        return group.show_grades_list()

    def calculate_group_approved_percentage(self, group_name: str) -> OperationResult:
        group = self.find_group(group_name)
        if not group:
            return OperationResult(False, f"Group {group_name} not found in course {self.course_name}.")
        return group.calculate_approved_percentage()

# --- 6. Professor Class (Main Application Logic) ---
class Professor:
    def __init__(self, professor_id: str, name: str):
        self.professor_id = professor_id
        self.name = name
        self.courses: list[Course] = []

    def add_course(self, course: Course) -> OperationResult:
        if any(c.course_code == course.course_code for c in self.courses):
            return OperationResult(False, f"Course {course.course_name} ({course.course_code}) already exists for this professor.")
        self.courses.append(course)
        return OperationResult(True, f"Course {course.course_name} added to professor {self.name}'s courses.")

    def find_course(self, course_name: str) -> Course | None:
        for course in self.courses:
            if course.course_name.lower() == course_name.lower():
                return course
        return None

    def display_courses(self):
        if not self.courses:
            print("No courses registered yet.")
            return
        print("\n--- Your Courses ---")
        for i, course in enumerate(self.courses):
            print(f"{i + 1}. {course.course_name} ({course.course_code})")
        print("--------------------")

    def display_groups_in_course(self, course: Course):
        if not course.groups:
            print(f"No groups registered for {course.course_name} yet.")
            return
        print(f"\n--- Groups in {course.course_name} ---")
        for i, group in enumerate(course.groups):
            print(f"{i + 1}. {group.group_name}")
        print("------------------------")

    def get_course_selection(self) -> Course | None:
        self.display_courses()
        if not self.courses:
            return None
        while True:
            try:
                choice = input("Enter the number of the course, or 0 to cancel: ")
                if choice == '0':
                    return None
                index = int(choice) - 1
                if 0 <= index < len(self.courses):
                    return self.courses[index]
                else:
                    print("Invalid course number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def get_group_selection(self, course: Course) -> Group | None:
        self.display_groups_in_course(course)
        if not course.groups:
            return None
        while True:
            try:
                choice = input("Enter the number of the group, or 0 to cancel: ")
                if choice == '0':
                    return None
                index = int(choice) - 1
                if 0 <= index < len(course.groups):
                    return course.groups[index]
                else:
                    print("Invalid group number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def manage_students_and_grades_menu(self):
        while True:
            print("\n===== Professor Menu =====")
            print("1. Add a new Course")
            print("2. Add a new Group to a Course")
            print("3. Add Student to a Group")
            print("4. Register Grade for a Student")
            print("5. Show Grades List for a Group")
            print("6. Calculate Approved Percentage for a Group")
            print("7. Exit")
            print("==========================")

            choice = input("Enter your choice: ")

            if choice == '1':
                course_name = input("Enter course name: ")
                course_code = input("Enter course code: ")
                new_course = Course(course_name, course_code)
                result = self.add_course(new_course)
                print(result.message)

            elif choice == '2':
                course = self.get_course_selection()
                if not course: continue
                group_name = input("Enter new group name: ")
                new_group = Group(group_name)
                result = course.add_group(new_group)
                print(result.message)

            elif choice == '3':
                course = self.get_course_selection()
                if not course: continue
                group = self.get_group_selection(course)
                if not group: continue

                student_id = input("Enter student ID: ")
                student_name = input("Enter student name: ")
                student_type = input("Is the student (P)resencial or (D)istancia? (P/D): ").upper()

                if student_type == 'P':
                    student = OnsiteStudent(student_id, student_name)
                elif student_type == 'D':
                    platform = input("Enter connection platform (e.g., Zoom, Teams): ")
                    student = RemoteStudent(student_id, student_name, platform)
                else:
                    print("Invalid student type. Please enter P or D.")
                    continue
                
                result = course.add_student_to_group(group.group_name, student)
                print(result.message)

            elif choice == '4':
                course = self.get_course_selection()
                if not course: continue
                group = self.get_group_selection(course)
                if not group: continue

                student_id = input("Enter student ID: ")
                student_found = group.find_student(student_id)
                if not student_found:
                    print(f"Student with ID {student_id} not found in group {group.group_name}.")
                    continue

                assessment_name = input("Enter assessment name (e.g., Midterm, Homework 1): ")
                try:
                    score = float(input("Enter score (0-100): "))
                    result = course.register_grade_in_group(group.group_name, student_id, assessment_name, score)
                    print(result.message)
                except ValueError:
                    print("Invalid score. Please enter a number between 0 and 100.")

            elif choice == '5':
                course = self.get_course_selection()
                if not course: continue
                group = self.get_group_selection(course)
                if not group: continue
                
                result = course.show_group_grades(group.group_name)
                if result.success:
                    print(result.data)
                else:
                    print(result.message)

            elif choice == '6':
                course = self.get_course_selection()
                if not course: continue
                group = self.get_group_selection(course)
                if not group: continue
                
                result = course.calculate_group_approved_percentage(group.group_name)
                if result.success:
                    print(f"Percentage of approved students in {group.group_name}: {result.data:.2f}%")
                else:
                    print(result.message)

            elif choice == '7':
                print("Exiting application. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

# --- Example Usage ---
if __name__ == "__main__":
    professor = Professor("P001", "Dr. Albus Dumbledore")
    professor.manage_students_and_grades_menu()