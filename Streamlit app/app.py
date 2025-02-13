import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from constraint import Problem, BacktrackingSolver
import random

def generate_student_schedules(num_students, num_subjects, subjects_per_student):
    return [random.sample([str(i) for i in range(num_subjects)], subjects_per_student) for _ in range(num_students)]

def solve_exam_scheduling(days, subjects, student_schedules):
    problem = Problem(BacktrackingSolver())

    # Add variables (subjects) and their domains (days)
    for subject in subjects:
        problem.addVariable(subject, days)

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
    for i, subject1 in enumerate(subjects):
        for subject2 in subjects[i+1:]:
            problem.addConstraint(no_conflict(subject1, subject2), (subject1, subject2))

    # Solve the problem
    solution = problem.getSolution()
    return solution

def verify_solution(schedule, student_schedules):
    for student_schedule in student_schedules:
        exam_days = [schedule[subject] for subject in student_schedule]
        if len(exam_days) != len(set(exam_days)):
            return False
    return True

st.title("Exam Scheduling")

# Get user input
num_days = st.number_input("Enter the number of days:", min_value=1, step=1, value=5)
num_students = st.number_input("Enter the number of students:", min_value=1, step=1, value=70)
subjects_per_student = st.number_input("Enter the number of subjects per student:", min_value=1, step=1, value=3)
total_subjects = st.number_input("Enter the total number of available subjects:", min_value=1, step=1, value=40)

days = [f"Day {i+1}" for i in range(num_days)]

# Generate and solve the problem
student_schedules = generate_student_schedules(num_students, total_subjects, subjects_per_student)
solution = solve_exam_scheduling(days, [str(i) for i in range(total_subjects)], student_schedules)

# Display the results in a table
if solution:
    st.header("Exam Schedule:")

    # Create a DataFrame for easy display
    schedule_df = pd.DataFrame(list(solution.items()), columns=["Subject", "Day"])
    st.write(schedule_df)

    # Verify if the solution is valid
    is_valid = verify_solution(solution, student_schedules)
    st.write(f"Is the solution valid? {'Yes' if is_valid else 'No'}")

    # Visualization of Exam Schedule
    st.subheader("Visualized Exam Schedule")
    
    # Plotting the exam schedule in a calendar-like form using a heatmap
    day_subject_matrix = pd.DataFrame(index=days, columns=[f"Subject {i}" for i in range(total_subjects)], data="")

    # Fill in the schedule based on the solution
    for subject, day in solution.items():
        day_subject_matrix.loc[day, f"Subject {subject}"] = "x"
    
    # Plot with seaborn heatmap
    plt.figure(figsize=(10, len(days) / 2))
    sns.heatmap(day_subject_matrix.applymap(lambda x: 1 if x == "x" else 0),
                cmap="YlGnBu", cbar=False, linewidths=0.1, linecolor="black",
                annot=day_subject_matrix, fmt="", annot_kws={"size": 8})
    
    plt.title("Exam Schedule per Day")
    plt.xlabel("Subjects")
    plt.ylabel("Days")
    st.pyplot(plt)

else:
    st.write("No solution found.")
