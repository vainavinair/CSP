import random
from constraint import Problem,RecursiveBacktrackingSolver

# Constants
SUBJECTS = [str(i) for i in range(150)]
DAYS = [f'{x}' for x in range(15) ]
NUM_STUDENTS = 200

# Generate random student schedules
def generate_student_schedules(num_students, subjects, subjects_per_student=3):
    return [random.sample(subjects, subjects_per_student) for _ in range(num_students)]

# Generate student schedules
student_schedules = generate_student_schedules(NUM_STUDENTS, SUBJECTS)
print(student_schedules)
# Create the CSP problem
problem = Problem(RecursiveBacktrackingSolver())

# Add variables (subjects) and their domains (days)
for subject in SUBJECTS:
    problem.addVariable(subject, DAYS)

# Add constraint: No student should have two exams on the same day
def no_conflict(subject1, subject2):
    def constraint(day1, day2):
        for schedule in student_schedules:
            if subject1 in schedule and subject2 in schedule:
                if day1 == day2:
                    return False
        return True
    return constraint

# Add constraints for each pair of subjects
for i, subject1 in enumerate(SUBJECTS):
    for subject2 in SUBJECTS[i+1:]:
        problem.addConstraint(no_conflict(subject1, subject2), (subject1, subject2))

# Solve the problem
solution = problem.getSolution()

# Print the result
if solution:
    print("Exam Schedule:")
    for subject, day in solution.items():
        print(f"{subject}: {day}")
else:
    print("No solution found.")

# Verify the solution
def verify_solution(schedule, student_schedules):
    for student_schedule in student_schedules:
        exam_days = [schedule[subject] for subject in student_schedule]
        if len(exam_days) != len(set(exam_days)):
            return False
    return True

if solution:
    is_valid = verify_solution(solution, student_schedules)
    print(f"\nIs the solution valid? {'Yes' if is_valid else 'No'}")