import random
import time
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

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
        # Create subject constraints graph
        self.subject_constraints = self._create_subject_constraints()

    def _generate_student_subjects(self) -> Dict[int, Set[int]]:
        """Generate random subject assignments for each student"""
        student_subjects = {}
        subjects = list(range(self.num_subjects))
        
        for student in range(self.num_students):
            student_subjects[student] = set(random.sample(subjects, 3))
        return student_subjects

    def _create_subject_constraints(self) -> Dict[int, Set[int]]:
        """Create a graph of subject constraints based on student enrollments"""
        constraints = defaultdict(set)
        for student_subjects in self.student_subjects.values():
            subjects_list = list(student_subjects)
            for i in range(len(subjects_list)):
                for j in range(i + 1, len(subjects_list)):
                    constraints[subjects_list[i]].add(subjects_list[j])
                    constraints[subjects_list[j]].add(subjects_list[i])
        return constraints

    def get_conflicts(self, subject: int, day: int) -> List[Tuple[int, int]]:
        """Return list of conflicts if subject is scheduled on day"""
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
        """Check if assigning a subject to a day creates conflicts"""
        return len(self.get_conflicts(subject, day)) == 0

    def get_next_subject(self, unassigned_subjects: Set[int]) -> int:
        """Select next subject using MRV and Degree heuristics"""
        if not self.use_mrv and not self.use_degree:
            return min(unassigned_subjects)  # Default: select lowest numbered subject

        subject_scores = {}
        for subject in unassigned_subjects:
            score = 0
            
            if self.use_mrv:
                # Count valid remaining days for this subject
                valid_days = sum(1 for day in range(self.num_days) 
                               if self.is_valid_assignment(subject, day))
                score -= valid_days  # Negative because we want minimum remaining values
            
            if self.use_degree:
                # Add degree (number of constraints with unassigned subjects)
                unassigned_constraints = len([s for s in self.subject_constraints[subject]
                                           if s in unassigned_subjects])
                score += unassigned_constraints
            
            subject_scores[subject] = score

        return max(subject_scores.items(), key=lambda x: x[1])[0]

    def order_domain_values(self, subject: int) -> List[int]:
        """Order days using LCV heuristic"""
        if not self.use_lcv:
            return list(range(self.num_days))

        day_scores = {}
        for day in range(self.num_days):
            if not self.is_valid_assignment(subject, day):
                day_scores[day] = float('inf')
                continue

            # Count how many options we eliminate for neighboring subjects
            eliminated_options = 0
            for neighbor in self.subject_constraints[subject]:
                if self.schedule[neighbor] is None:  # Only check unassigned neighbors
                    # Temporarily assign this day
                    self.schedule[subject] = day
                    # Count valid remaining days for neighbor
                    valid_days = sum(1 for d in range(self.num_days) 
                                   if self.is_valid_assignment(neighbor, d))
                    eliminated_options += self.num_days - valid_days
                    # Undo temporary assignment
                    self.schedule[subject] = None
            
            day_scores[day] = eliminated_options

        return sorted(range(self.num_days), key=lambda d: day_scores[d])

    def print_current_state(self, subject: int, day: int, conflicts: List[Tuple[int, int]], 
                          tried: bool, heuristic_info: Optional[Dict] = None):
        """Create a visual representation of the current schedule state"""
        state = {
            'schedule': self.schedule.copy(),
            'current_subject': subject,
            'current_day': day,
            'conflicts': conflicts,
            'tried': tried,
            'heuristic_info': heuristic_info or {}
        }
        self.steps.append(state)

    def solve(self, unassigned_subjects: Optional[Set[int]] = None) -> bool:
        """Solve the scheduling problem using backtracking with heuristics"""
        if unassigned_subjects is None:
            unassigned_subjects = set(range(self.num_subjects))
        
        if not unassigned_subjects:
            return True

        subject = self.get_next_subject(unassigned_subjects)
        ordered_days = self.order_domain_values(subject)
        
        heuristic_info = {
            'mrv_active': self.use_mrv,
            'degree_active': self.use_degree,
            'lcv_active': self.use_lcv,
            'subject_chosen': subject,
            'day_order': ordered_days
        }

        for day in ordered_days:
            conflicts = self.get_conflicts(subject, day)
            self.print_current_state(subject, day, conflicts, True, heuristic_info)
            
            if not conflicts:
                self.schedule[subject] = day
                new_unassigned = unassigned_subjects - {subject}
                
                if self.solve(new_unassigned):
                    return True
                    
                self.schedule[subject] = None
                self.print_current_state(subject, day, [], False, heuristic_info)
                
        return False

    def visualize_steps(self):
        """Display the backtracking steps with heuristic information"""
        print("\nDetailed Backtracking Steps:")
        print("=" * 70)
        for i, step in enumerate(self.steps, 1):
            print(f"\nStep {i}:")
            
            # Show heuristic information
            if step['heuristic_info']:
                print("Heuristics active:")
                if step['heuristic_info']['mrv_active']:
                    print("  → MRV: Choosing subject with fewest valid days")
                if step['heuristic_info']['degree_active']:
                    print("  → Degree: Considering subject constraints")
                if step['heuristic_info']['lcv_active']:
                    print("  → LCV: Trying days in order:", 
                          step['heuristic_info']['day_order'])
                print(f"Selected Subject {step['heuristic_info']['subject_chosen']} "
                      f"to schedule next")
            
            print(f"Attempting to schedule Subject {step['current_subject']} "
                  f"on Day {step['current_day']}")
            
            # Show current schedule
            print("Current schedule:", end=" ")
            for subject in range(self.num_subjects):
                if step['schedule'][subject] is not None:
                    print(f"S{subject}:D{step['schedule'][subject]}", end=" ")
            print()
            
            # Show conflicts if any
            if step['conflicts']:
                print("CONFLICTS FOUND:")
                for student, other_subject in step['conflicts']:
                    print(f"  → Student {student} would have conflict between "
                          f"Subject {step['current_subject']} and Subject "
                          f"{other_subject} on Day {step['current_day']}")
                print("  → Trying next day...")
            else:
                if step['tried']:
                    print("No conflicts - Assignment successful!")
                else:
                    print("Backtracking - Removing assignment and trying next possibility")
            
            print("-" * 70)

    def display_solution(self):
        """Display the final schedule in a formatted way"""
        day_schedule = {day: [] for day in range(self.num_days)}
        for subject, day in self.schedule.items():
            if day is not None:
                day_schedule[day].append(subject)
                
        print("\nFinal Schedule:")
        print("=" * 50)
        for day in range(self.num_days):
            print(f"Day {day + 1}: Subject(s) {', '.join(map(str, day_schedule[day]))}")
        
        # Verify and show any conflicts
        conflicts = []
        for student in self.student_subjects:
            student_days = {self.schedule[subject] 
                          for subject in self.student_subjects[student]}
            if len(student_days) != len(self.student_subjects[student]):
                conflicts.append(student)
                
        if conflicts:
            print("\nWarning: Conflicts found for students:", conflicts)
        else:
            print("\nNo conflicts found! Schedule is valid.")

def main():
    # Test different heuristic combinations
    test_cases = [
        {'name': 'No Heuristics', 'mrv': False, 'degree': False, 'lcv': False},
        {'name': 'MRV Only', 'mrv': True, 'degree': False, 'lcv': False},
        {'name': 'Degree Only', 'mrv': False, 'degree': True, 'lcv': False},
        {'name': 'LCV Only', 'mrv': False, 'degree': False, 'lcv': True},
        {'name': 'All Heuristics', 'mrv': True, 'degree': True, 'lcv': True},
    ]

    for case in test_cases:
        print(f"\nTesting {case['name']}:")
        print("=" * 50)
        
        random.seed(42)  # Reset seed for fair comparison
        scheduler = ExamScheduler(
            num_students=70,
            num_subjects=45,
            num_days=6,
            use_mrv=case['mrv'],
            use_degree=case['degree'],
            use_lcv=case['lcv']
        )
        
        start_time = time.time()
        if scheduler.solve():
            end_time = time.time()
            print(f"\nSolution found in {end_time - start_time:.3f} seconds!")
            scheduler.display_solution()
            scheduler.visualize_steps()
        else:
            print("\nNo solution exists!")

if __name__ == "__main__":
    main()