# Exam Scheduler

A Python implementation of an exam scheduling system using custom constraint satisfaction with various heuristics. The scheduler ensures no student has to take multiple exams on the same day while optimizing the schedule distribution.

## Custom Implementation Overview

The main implementation (`custom.ipynb`) provides a robust exam scheduling solution using:

### Key Features
- **Backtracking Algorithm**: Custom implementation of backtracking search
- **Multiple Heuristics**:
  - Minimum Remaining Values (MRV): Chooses subjects with fewest valid scheduling options
  - Degree Heuristic: Prioritizes subjects with more constraints
  - Least Constraining Value (LCV): Selects days that restrict future assignments least
- **Performance Testing**: Comprehensive comparison of different heuristic combinations
- **Visualization**: Detailed step-by-step visualization of the scheduling process

### Core Components
```python
class ExamScheduler:
    def __init__(self, num_students, num_subjects, num_days,
                 use_mrv=False, use_degree=False, use_lcv=False):
        # Initialize scheduler with desired configuration
```

### Example Usage
```python
# Basic usage of custom implementation
scheduler = ExamScheduler(
    num_students=70,    # Number of students
    num_subjects=25,    # Number of subjects to schedule
    num_days=7,         # Available days for scheduling
    use_mrv=True,      # Enable Minimum Remaining Values
    use_degree=True,   # Enable Degree heuristic
    use_lcv=True       # Enable Least Constraining Value
)

# Solve and display results
if scheduler.solve():
    scheduler.display_solution()
    scheduler.visualize_steps()  # Optional: see detailed solving process
```

## Project Structure

```
├── custom.ipynb              # Main implementation (Custom CSP)
├── Using Libraries/          # Alternative implementations
│   ├── csp_constraint.ipynb  # Using constraint library
│   └── csp_simpleai.ipynb   # Using simpleai library
├── Streamlit app/           # Web interfaces
│   ├── app.py              # Using constraint library
│   └── app2.py            # Using custom implementation
└── requirements.txt
```

## Requirements

- All dependencies in requirements.txt

## Installation

```bash
git clone https://github.com/yourusername/exam-scheduler.git
cd exam-scheduler
```

## Contributing

Contributions to improve the custom implementation are welcome. Areas of interest:
- Additional heuristics
- Arc consistency
- Performance optimizations
- Visualization enhancements

