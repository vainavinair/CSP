import streamlit as st
import random
import time
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import io

class ExamScheduler:
    def __init__(self, num_students: int, num_subjects: int, num_days: int,
                 use_mrv: bool = False, use_degree: bool = False, 
                 use_lcv: bool = False):
        self.num_students = num_students
        self.num_subjects = num_subjects
        self.num_days = num_days
        self.use_mrv = use_mrv
        self.use_degree = use_degree
        self.use_lcv = use_lcv
        self.student_subjects = self._generate_student_subjects()
        self.schedule = {subject: None for subject in range(num_subjects)}
        self.steps = []
        self.subject_constraints = self._create_subject_constraints()
        # Add StringIO buffer for logging
        self.log_buffer = io.StringIO()

    def _generate_student_subjects(self) -> Dict[int, Set[int]]:
        student_subjects = {}
        subjects = list(range(self.num_subjects))
        
        for student in range(self.num_students):
            num_subjects_per_student = min(3, len(subjects))
            student_subjects[student] = set(random.sample(subjects, num_subjects_per_student))
        return student_subjects

    def _create_subject_constraints(self) -> Dict[int, Set[int]]:
        constraints = defaultdict(set)
        for student_subjects in self.student_subjects.values():
            subjects_list = list(student_subjects)
            for i in range(len(subjects_list)):
                for j in range(i + 1, len(subjects_list)):
                    constraints[subjects_list[i]].add(subjects_list[j])
                    constraints[subjects_list[j]].add(subjects_list[i])
        return constraints

    def log_step(self, message: str):
        """Log a step to the buffer"""
        self.log_buffer.write(message + "\n")

    def solve(self, unassigned_subjects: Optional[Set[int]] = None) -> bool:
        if unassigned_subjects is None:
            unassigned_subjects = set(range(self.num_subjects))
        
        if not unassigned_subjects:
            return True

        subject = self.get_next_subject(unassigned_subjects)
        ordered_days = self.order_domain_values(subject)

        # Log subject selection
        heuristic_info = []
        if self.use_mrv:
            heuristic_info.append("MRV")
        if self.use_degree:
            heuristic_info.append("Degree")
        if self.use_lcv:
            heuristic_info.append("LCV")
        
        heuristic_str = f" using {', '.join(heuristic_info)}" if heuristic_info else ""
        self.log_step(f"\n👉 Selected Subject {subject}{heuristic_str}")
        self.log_step(f"   Current schedule: {self._format_schedule()}")
        
        for day in ordered_days:
            self.log_step(f"\n   Trying Day {day}")
            conflicts = self.get_conflicts(subject, day)
            
            if conflicts:
                self.log_step(f"   ❌ Conflicts found: {conflicts}")
                continue
                
            self.log_step(f"   ✅ No conflicts - assigning Subject {subject} to Day {day}")
            self.schedule[subject] = day
            new_unassigned = unassigned_subjects - {subject}
            
            if self.solve(new_unassigned):
                return True
                
            self.log_step(f"   🔄 Backtracking: removing Subject {subject} from Day {day}")
            self.schedule[subject] = None
        
        self.log_step(f"   ⚠️ No valid day found for Subject {subject}")
        return False

    def _format_schedule(self) -> str:
        """Format current schedule for logging"""
        assigned = [f"S{s}:D{d}" for s, d in self.schedule.items() if d is not None]
        return ", ".join(assigned) if assigned else "empty"

    def get_conflicts(self, subject: int, day: int) -> List[Tuple[int, int]]:
        conflicts = []
        students_in_subject = {
            student for student in self.student_subjects 
            if subject in self.student_subjects[student]
        }
        
        for student in students_in_subject:
            other_subjects = self.student_subjects[student] - {subject}
            for other_subject in other_subjects:
                if (self.schedule[other_subject] is not None and 
                    self.schedule[other_subject] == day):
                    conflicts.append((student, other_subject))
        return conflicts

    def is_valid_assignment(self, subject: int, day: int) -> bool:
        return len(self.get_conflicts(subject, day)) == 0

    def get_next_subject(self, unassigned_subjects: Set[int]) -> int:
        if not self.use_mrv and not self.use_degree:
            return min(unassigned_subjects)

        subject_scores = {}
        for subject in unassigned_subjects:
            score = 0
            
            if self.use_mrv:
                valid_days = sum(1 for day in range(self.num_days) 
                               if self.is_valid_assignment(subject, day))
                score -= valid_days
            
            if self.use_degree:
                unassigned_constraints = len([s for s in self.subject_constraints[subject]
                                           if s in unassigned_subjects])
                score += unassigned_constraints
            
            subject_scores[subject] = score

        return max(subject_scores.items(), key=lambda x: x[1])[0]

    def order_domain_values(self, subject: int) -> List[int]:
        if not self.use_lcv:
            return list(range(self.num_days))

        day_scores = {}
        for day in range(self.num_days):
            if not self.is_valid_assignment(subject, day):
                day_scores[day] = float('inf')
                continue

            eliminated_options = 0
            for neighbor in self.subject_constraints[subject]:
                if self.schedule[neighbor] is None:
                    self.schedule[subject] = day
                    valid_days = sum(1 for d in range(self.num_days) 
                                   if self.is_valid_assignment(neighbor, d))
                    eliminated_options += self.num_days - valid_days
                    self.schedule[subject] = None
            
            day_scores[day] = eliminated_options

        return sorted(range(self.num_days), key=lambda d: day_scores[d])

def main():
    st.set_page_config(layout="wide")
    st.title("Exam Schedule Generator")
    st.write("Configure the exam scheduling parameters and see the results!")

    # Sidebar controls with number inputs
    st.sidebar.header("Configuration")
    
    col1, col2, col3 = st.sidebar.columns(3)
    
    with col1:
        num_students = st.number_input("Number of Students", 
                                     min_value=1, 
                                     value=70,
                                     step=1)
    
    with col2:
        num_subjects = st.number_input("Number of Subjects", 
                                     min_value=1, 
                                     value=45,
                                     step=1)
    
    with col3:
        num_days = st.number_input("Number of Days", 
                                 min_value=1, 
                                 value=6,
                                 step=1)
    
    st.sidebar.header("Heuristics")
    use_mrv = st.sidebar.checkbox("Use Minimum Remaining Values (MRV)", False)
    use_degree = st.sidebar.checkbox("Use Degree Heuristic", False)
    use_lcv = st.sidebar.checkbox("Use Least Constraining Value (LCV)", False)

    # Basic validation
    warning_messages = []
    if num_subjects < 3:
        warning_messages.append("⚠️ Having fewer than 3 subjects might not be practical.")
    if num_days < 2:
        warning_messages.append("⚠️ Having only 1 day might make it impossible to create a valid schedule.")
    if num_students < 1 or num_subjects < 1 or num_days < 1:
        warning_messages.append("❌ All values must be positive numbers.")
    
    # Display warnings if any
    for msg in warning_messages:
        st.sidebar.warning(msg)

    if st.button("Generate Schedule"):
        if num_students < 1 or num_subjects < 1 or num_days < 1:
            st.error("Please ensure all values are positive numbers.")
            return

        with st.spinner("Generating schedule..."):
            try:
                random.seed(42)  # For consistent results
                scheduler = ExamScheduler(
                    num_students=num_students,
                    num_subjects=num_subjects,
                    num_days=num_days,
                    use_mrv=use_mrv,
                    use_degree=use_degree,
                    use_lcv=use_lcv
                )
                
                start_time = time.time()
                solution_found = scheduler.solve()
                end_time = time.time()
                
                if solution_found:
                    st.success(f"Solution found in {end_time - start_time:.3f} seconds!")
                    
                    # Display schedule and student distribution in two columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.header("Final Schedule")
                        day_schedule = {day: [] for day in range(num_days)}
                        for subject, day in scheduler.schedule.items():
                            if day is not None:
                                day_schedule[day].append(subject)
                        
                        schedule_data = []
                        for day in range(num_days):
                            subjects = day_schedule[day]
                            schedule_data.append({
                                "Day": f"Day {day + 1}",
                                "Subjects": ", ".join(map(str, subjects)),
                                "Number of Exams": len(subjects)
                            })
                        
                        st.table(schedule_data)
                    
                    # Display student distribution
                    with col2:
                        st.header("Student Subject Distribution")
                        student_data = []
                        for student in range(num_students):
                            subjects = scheduler.student_subjects[student]
                            student_data.append({
                                "Student": f"Student {student}",
                                "Subjects": ", ".join(map(str, subjects)),
                                "Exam Days": ", ".join(f"Day {scheduler.schedule[subject] + 1}" 
                                                     for subject in subjects)
                            })
                        
                        with st.container():
                            st.dataframe(
                                student_data,
                                height=400,
                                hide_index=True
                            )
                    
                    # Verify conflicts
                    conflicts = []
                    for student in scheduler.student_subjects:
                        student_days = {scheduler.schedule[subject] 
                                      for subject in scheduler.student_subjects[student]}
                        if len(student_days) != len(scheduler.student_subjects[student]):
                            conflicts.append(student)
                    
                    if conflicts:
                        st.error(f"Warning: Conflicts found for students: {conflicts}")
                    else:
                        st.success("No conflicts found! Schedule is valid.")
                    
                    # Display backtracking steps in a scrollable text box
                    st.header("Backtracking Steps")
                    st.text_area(
                        "Detailed solving process:",
                        scheduler.log_buffer.getvalue(),
                        height=300
                    )
                else:
                    st.error("No solution exists with the given constraints!")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Try adjusting the numbers to more reasonable values.")

if __name__ == "__main__":
    main()