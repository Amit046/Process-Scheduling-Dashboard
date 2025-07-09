
# 🖥️ Process Scheduling Dashboard

A comprehensive **PyQt5-based desktop application** for visualizing and analyzing various CPU scheduling algorithms. This educational tool provides an interactive environment to understand how different scheduling algorithms work in operating systems.

---

## 🎯 Features

### ✅ Scheduling Algorithms Implemented
- **First Come First Serve (FCFS)** - Non-preemptive
- **Shortest Job First (SJF)** - Both preemptive and non-preemptive variants
- **Round Robin (RR)** - Time quantum-based scheduling
- **Priority Scheduling** - Both preemptive and non-preemptive variants

### 🎨 Visual Components
- **Interactive Gantt Charts** - Real-time process execution visualization
- **Process Metrics Charts** - Waiting time, turnaround time, and burst time analysis
- **Process Table** - Detailed process information display
- **Real-time Statistics** - Avg waiting, turnaround & response time

### 🔄 Interactive Features
- **Step-by-step execution** - Watch algorithms execute one time unit at a time
- **Complete execution** - Run algorithms to completion instantly
- **Process management** - Add, remove, and modify processes
- **Algorithm comparison** - View different algorithms side-by-side
- **Dark theme UI** - Modern, eye-friendly interface

---

## 🚀 Getting Started

### 🔧 Prerequisites
- Python 3.7 or higher
- PyQt5
- matplotlib
- numpy
- pandas

### 🛠️ Installation

```bash
pip install PyQt5 matplotlib numpy pandas
```

### ▶️ Run the Application
```bash
python process_scheduler.py
```

---

## 📖 How to Use

### 🧩 Adding Processes
1. Go to **"Process Management"** tab
2. Enter:
   - **Process ID**
   - **Arrival Time**
   - **Burst Time**
   - **Priority** (1 = highest)
3. Click **"Add Process"**
4. OR use **"Load Sample Processes"** for testing

### ⚙️ Running Algorithms
1. Select a scheduling algorithm tab
2. Use buttons:
   - **Step**: Execute one time unit
   - **Run Complete**: Run full execution
   - **Reset**: Restart simulation

---

## 📊 Understanding the Visuals

### Gantt Chart
- Visual timeline of process execution
- Unique colors for each process
- X-axis = Time units

### Process Metrics Charts
- Left: Waiting Time vs Turnaround Time
- Right: Burst Time distribution
- Colors match Gantt Chart

### Process Table
- Metrics for each process: start, finish, wait, turnaround
- Colored IDs for easy tracking

---

## 🔧 Technical Details

### 📂 Project Structure
```
process_scheduler.py
├── Process Class
├── SchedulingAlgorithm Classes
│   ├── FCFSScheduling
│   ├── SJFScheduling
│   ├── RoundRobinScheduling
│   └── PriorityScheduling
├── UI Components
│   ├── GanttChartWidget
│   ├── ProcessMetricsWidget
│   ├── ProcessTableWidget
│   └── ProcessDashboardApp
```

### ⚙️ Algorithms Overview

#### FCFS
- Based on arrival time
- Simple, non-preemptive

#### SJF
- Chooses shortest burst job
- Supports preemptive (SRTF) & non-preemptive

#### Round Robin
- Equal time quantum for each
- Best for time-sharing

#### Priority Scheduling
- Based on priority value
- Can be preemptive/non-preemptive

---

## 📊 Metrics Explained
- **Waiting Time**: Time in ready queue
- **Turnaround Time**: Completion - arrival time
- **Response Time**: First run - arrival time
- **Burst Time**: Required CPU time

---

## 🎨 Design Features
- Dark blue UI theme
- Resizable layout
- Unique colors per process
- Real-time updates on execution

---

## 📚 Educational Value
Perfect for:
- 📘 Operating Systems learning
- 📊 Algorithm performance comparison
- 🎓 Semester projects
- 🧠 Step-by-step algorithm understanding

---

## 🏫 Course Context
Created as part of **4th Semester Computer Science** project to demonstrate:
- PyQt5 GUI programming
- matplotlib data visualization
- Scheduling algorithms in OOP
- Hands-on operating system concepts

---

## 🛠️ Customization Guide

### ➕ Add New Algorithms
1. Inherit `SchedulingAlgorithm`
2. Implement `step()` method
3. Register in `schedulers` dictionary

### 🎨 Customize Visualization
- Modify `GanttChartWidget` and `ProcessMetricsWidget`
- Change global color constants as needed

---

## 🐛 Known Issues
- Round Robin has fixed time quantum = 2
- Priority limited to 1–10
- Process ID max = 999

---

## 🌟 Future Enhancements
- [ ] Multilevel Queue Scheduling
- [ ] Feedback Queue Support
- [ ] Configurable Time Quantum
- [ ] Priority Aging
- [ ] Export charts & tables
- [ ] Animation speed control
- [ ] Parallel comparison view

---

## 👥 Contributing

Contributions welcome for:
- 🧠 New algorithms
- 🎨 UI polish
- 🐞 Bug fixes
- 📘 Documentation

Fork and submit PRs!

---

## 📝 License

Educational use only. Free to use and modify for academic and learning purposes.

---

## 👨‍💻 Developed By

**Name**: Amit Yadav  
**GitHub**: [github.com/Amit046](https://github.com/Amit046)  
**Email**: amityt500678@gmail.com  
**Course**: Operating Systems (4th Semester)  
**Institution**: Lovely Professional University  
**Year**: 2025

---

*This project brings CPU scheduling concepts to life through interactive visualizations and user-friendly design.*
