import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import matplotlib
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
                            QComboBox, QLineEdit, QFormLayout, QSpinBox, QScrollArea, QSplitter,
                            QHeaderView, QMessageBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QLinearGradient, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Set the style for matplotlib
plt.style.use('dark_background')

# Custom dark blue theme colors
DARK_COLOR = "#121212"
DARK_BLUE = "#1a237e"
LIGHT_BLUE = "#4f83cc"
ACCENT_COLOR = "#64b5f6"
TEXT_COLOR = "#e0e0e0"
HIGHLIGHT_COLOR = "#03a9f4"

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None
        self.color = self.generate_color()
        self.execution_sequence = []  # Stores (start, duration) tuples for Gantt visualization
    
    def generate_color(self):
        # Generate a pastel color based on process ID
        hue = (self.pid * 0.15) % 1.0
        return plt.cm.viridis(hue)
    
    def reset(self):
        self.remaining_time = self.burst_time
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None
        self.execution_sequence = []


class SchedulingAlgorithm:
    def __init__(self, processes=None):
        self.processes = processes or []
        self.time = 0
        self.current_process = None
        self.ready_queue = []
        self.completed_processes = []
        self.execution_history = []  # For Gantt chart: (time, pid, duration)
    
    def add_process(self, process):
        self.processes.append(process)
    
    def reset(self):
        self.time = 0
        self.current_process = None
        self.ready_queue = []
        self.completed_processes = []
        self.execution_history = []
        for process in self.processes:
            process.reset()
    
    def is_completed(self):
        return len(self.completed_processes) == len(self.processes)
    
    def get_average_waiting_time(self):
        if not self.completed_processes:
            return 0
        return sum(p.waiting_time for p in self.completed_processes) / len(self.completed_processes)
    
    def get_average_turnaround_time(self):
        if not self.completed_processes:
            return 0
        return sum(p.turnaround_time for p in self.completed_processes) / len(self.completed_processes)

    def get_average_response_time(self):
        if not self.completed_processes:
            return 0
        return sum(p.response_time for p in self.completed_processes if p.response_time is not None) / len(self.completed_processes)
    
    def update_waiting_times(self):
        for process in self.processes:
            if (process not in self.completed_processes and 
                process != self.current_process and 
                process.arrival_time <= self.time and
                process.remaining_time > 0):
                process.waiting_time += 1
    
    def step(self):
        # To be implemented by subclasses
        pass


class FCFSScheduling(SchedulingAlgorithm):
    def step(self):
        if self.is_completed():
            return False
        
        # Check for new arriving processes
        new_arrivals = [p for p in self.processes 
                      if p.arrival_time == self.time 
                      and p not in self.ready_queue 
                      and p not in self.completed_processes]
        
        for process in new_arrivals:
            self.ready_queue.append(process)
        
        # If no process is running, get the next from the queue
        if self.current_process is None and self.ready_queue:
            self.current_process = self.ready_queue.pop(0)
            self.current_process.start_time = self.time
            self.current_process.response_time = self.time - self.current_process.arrival_time
            self.execution_history.append((self.time, self.current_process.pid, 0))  # Start new execution block
        
        # Update the current running process
        if self.current_process:
            self.current_process.remaining_time -= 1
            self.execution_history[-1] = (self.execution_history[-1][0], self.execution_history[-1][1], 
                                         self.execution_history[-1][2] + 1)  # Update duration
            
            # If process is completed
            if self.current_process.remaining_time == 0:
                self.current_process.finish_time = self.time + 1
                self.current_process.turnaround_time = self.current_process.finish_time - self.current_process.arrival_time
                self.current_process.execution_sequence.append((self.current_process.start_time, 
                                                              self.current_process.finish_time - self.current_process.start_time))
                self.completed_processes.append(self.current_process)
                self.current_process = None
        
        self.update_waiting_times()
        self.time += 1
        return True


class SJFScheduling(SchedulingAlgorithm):
    def __init__(self, processes=None, preemptive=False):
        super().__init__(processes)
        self.preemptive = preemptive
    
    def step(self):
        if self.is_completed():
            return False
        
        # Check for new arriving processes
        new_arrivals = [p for p in self.processes 
                      if p.arrival_time == self.time 
                      and p not in self.ready_queue 
                      and p not in self.completed_processes
                      and p != self.current_process]
        
        for process in new_arrivals:
            self.ready_queue.append(process)
        
        # If preemptive, we need to check if a new process has shorter burst time
        if self.preemptive and self.current_process:
            shortest_job = min(self.ready_queue + ([self.current_process] if self.current_process else []), 
                              key=lambda p: p.remaining_time, default=None)
            
            if shortest_job != self.current_process and shortest_job in self.ready_queue:
                # Preempt the current process
                self.ready_queue.remove(shortest_job)
                
                if self.current_process:
                    self.ready_queue.append(self.current_process)
                    self.current_process.execution_sequence.append((self.current_process.start_time, 
                                                                 self.time - self.current_process.start_time))
                
                self.current_process = shortest_job
                self.current_process.start_time = self.time
                if self.current_process.response_time is None:
                    self.current_process.response_time = self.time - self.current_process.arrival_time
                self.execution_history.append((self.time, self.current_process.pid, 0))
        
        # If no process is running, get the shortest job from the queue
        if self.current_process is None and self.ready_queue:
            self.ready_queue.sort(key=lambda p: p.remaining_time)
            self.current_process = self.ready_queue.pop(0)
            self.current_process.start_time = self.time
            if self.current_process.response_time is None:
                self.current_process.response_time = self.time - self.current_process.arrival_time
            self.execution_history.append((self.time, self.current_process.pid, 0))
        
        # Update the current running process
        if self.current_process:
            self.current_process.remaining_time -= 1
            self.execution_history[-1] = (self.execution_history[-1][0], self.execution_history[-1][1], 
                                         self.execution_history[-1][2] + 1)
            
            # If process is completed
            if self.current_process.remaining_time == 0:
                self.current_process.finish_time = self.time + 1
                self.current_process.turnaround_time = self.current_process.finish_time - self.current_process.arrival_time
                self.current_process.execution_sequence.append((self.current_process.start_time, 
                                                              self.current_process.finish_time - self.current_process.start_time))
                self.completed_processes.append(self.current_process)
                self.current_process = None
        
        self.update_waiting_times()
        self.time += 1
        return True


class RoundRobinScheduling(SchedulingAlgorithm):
    def __init__(self, processes=None, time_quantum=1):
        super().__init__(processes)
        self.time_quantum = time_quantum
        self.current_time_slice = 0
    
    def reset(self):
        super().reset()
        self.current_time_slice = 0
    
    def step(self):
        if self.is_completed():
            return False
        
        # Check for new arriving processes
        new_arrivals = [p for p in self.processes 
                      if p.arrival_time == self.time 
                      and p not in self.ready_queue 
                      and p not in self.completed_processes
                      and p != self.current_process]
        
        for process in new_arrivals:
            self.ready_queue.append(process)
        
        # If time slice is expired or no process is running, get the next process
        if (self.current_process is None or self.current_time_slice >= self.time_quantum) and self.ready_queue:
            if self.current_process and self.current_process.remaining_time > 0:
                # Time slice expired, but process not finished
                self.current_process.execution_sequence.append(
                    (self.current_process.start_time, self.time - self.current_process.start_time))
                self.ready_queue.append(self.current_process)
            
            self.current_process = self.ready_queue.pop(0)
            self.current_process.start_time = self.time
            if self.current_process.response_time is None:
                self.current_process.response_time = self.time - self.current_process.arrival_time
            self.current_time_slice = 0
            self.execution_history.append((self.time, self.current_process.pid, 0))
        
        # Update the current running process
        if self.current_process:
            self.current_process.remaining_time -= 1
            self.current_time_slice += 1
            self.execution_history[-1] = (self.execution_history[-1][0], self.execution_history[-1][1], 
                                         self.execution_history[-1][2] + 1)
            
            # If process is completed
            if self.current_process.remaining_time == 0:
                self.current_process.finish_time = self.time + 1
                self.current_process.turnaround_time = self.current_process.finish_time - self.current_process.arrival_time
                self.current_process.execution_sequence.append((self.current_process.start_time, 
                                                              self.current_process.finish_time - self.current_process.start_time))
                self.completed_processes.append(self.current_process)
                self.current_process = None
                self.current_time_slice = 0
        
        self.update_waiting_times()
        self.time += 1
        return True


class PriorityScheduling(SchedulingAlgorithm):
    def __init__(self, processes=None, preemptive=False):
        super().__init__(processes)
        self.preemptive = preemptive
    
    def step(self):
        if self.is_completed():
            return False
        
        # Check for new arriving processes
        new_arrivals = [p for p in self.processes 
                      if p.arrival_time == self.time 
                      and p not in self.ready_queue 
                      and p not in self.completed_processes
                      and p != self.current_process]
        
        for process in new_arrivals:
            self.ready_queue.append(process)
        
        # If preemptive, we need to check if a new process has higher priority
        if self.preemptive and self.current_process:
            highest_priority = min(self.ready_queue + ([self.current_process] if self.current_process else []), 
                                 key=lambda p: p.priority, default=None)
            
            if highest_priority != self.current_process and highest_priority in self.ready_queue:
                # Preempt the current process
                self.ready_queue.remove(highest_priority)
                
                if self.current_process:
                    self.ready_queue.append(self.current_process)
                    self.current_process.execution_sequence.append((self.current_process.start_time, 
                                                                 self.time - self.current_process.start_time))
                
                self.current_process = highest_priority
                self.current_process.start_time = self.time
                if self.current_process.response_time is None:
                    self.current_process.response_time = self.time - self.current_process.arrival_time
                self.execution_history.append((self.time, self.current_process.pid, 0))
        
        # If no process is running, get the highest priority job from the queue
        if self.current_process is None and self.ready_queue:
            self.ready_queue.sort(key=lambda p: p.priority)
            self.current_process = self.ready_queue.pop(0)
            self.current_process.start_time = self.time
            if self.current_process.response_time is None:
                self.current_process.response_time = self.time - self.current_process.arrival_time
            self.execution_history.append((self.time, self.current_process.pid, 0))
        
        # Update the current running process
        if self.current_process:
            self.current_process.remaining_time -= 1
            self.execution_history[-1] = (self.execution_history[-1][0], self.execution_history[-1][1], 
                                         self.execution_history[-1][2] + 1)
            
            # If process is completed
            if self.current_process.remaining_time == 0:
                self.current_process.finish_time = self.time + 1
                self.current_process.turnaround_time = self.current_process.finish_time - self.current_process.arrival_time
                self.current_process.execution_sequence.append((self.current_process.start_time, 
                                                              self.current_process.finish_time - self.current_process.start_time))
                self.completed_processes.append(self.current_process)
                self.current_process = None
        
        self.update_waiting_times()
        self.time += 1
        return True


class GanttChartWidget(FigureCanvas):
    def __init__(self, parent=None, width=8, height=2, dpi=100):
        self.fig = plt.Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        
        self.setParent(parent)
        self.processes = []
        self.algorithm = None
        
        # Set the colors
        self.fig.patch.set_facecolor(DARK_COLOR)
        self.axes.set_facecolor(DARK_COLOR)
        self.axes.tick_params(colors=TEXT_COLOR)
        self.axes.xaxis.label.set_color(TEXT_COLOR)
        self.axes.yaxis.label.set_color(TEXT_COLOR)
        
        # Remove y-axis ticks
        self.axes.tick_params(left=False)
    
    def update_chart(self, algorithm):
        self.algorithm = algorithm
        self.processes = algorithm.processes
        self.draw_gantt_chart()
    
    def draw_gantt_chart(self):
        self.axes.clear()
        
        if not self.algorithm or not self.algorithm.execution_history:
            self.axes.set_title("No processes to display", color=TEXT_COLOR)
            self.draw()
            return
        
        # Set up the chart area
        max_time = max([h[0] + h[2] for h in self.algorithm.execution_history]) if self.algorithm.execution_history else 0
        self.axes.set_xlim(0, max(max_time, 1))
        self.axes.set_ylim(0, 1)
        
        # Draw each execution block
        current_y = 0.1
        block_height = 0.6
        
        # Process ID to color mapping
        color_map = {p.pid: p.color for p in self.processes}
        
        # Draw execution blocks
        for start, pid, duration in self.algorithm.execution_history:
            if duration <= 0:
                continue
                
            color = color_map.get(pid, 'gray')
            rect = patches.Rectangle((start, current_y), duration, block_height, 
                                    linewidth=1, edgecolor='black', facecolor=color, alpha=0.7)
            self.axes.add_patch(rect)
            
            # Add process ID in the center of each block
            if duration > 0.5:  # Only add text if the block is wide enough
                self.axes.text(start + duration/2, current_y + block_height/2, f'P{pid}',
                             ha='center', va='center', color='white', fontweight='bold')
        
        # Add grid and labels
        self.axes.grid(True, alpha=0.3, axis='x')
        self.axes.set_yticks([])
        self.axes.set_xlabel('Time', fontweight='bold', color=TEXT_COLOR)
        self.axes.set_title('Process Execution Gantt Chart', fontweight='bold', color=TEXT_COLOR)
        
        # Set tick labels
        self.axes.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        self.draw()


class ProcessMetricsWidget(FigureCanvas):
    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig = plt.Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        super().__init__(self.fig)
        
        # Create subplots for different metrics
        self.ax1 = self.fig.add_subplot(121)  # For waiting time and turnaround time
        self.ax2 = self.fig.add_subplot(122)  # For burst time
        
        self.setParent(parent)
        self.processes = []
        
        # Set the colors
        self.fig.patch.set_facecolor(DARK_COLOR)
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor(DARK_COLOR)
            ax.tick_params(colors=TEXT_COLOR)
            ax.xaxis.label.set_color(TEXT_COLOR)
            ax.yaxis.label.set_color(TEXT_COLOR)
            ax.title.set_color(TEXT_COLOR)
        
    def update_metrics(self, processes):
        self.processes = processes
        self.draw_metrics()
    
    def draw_metrics(self):
        self.ax1.clear()
        self.ax2.clear()
        
        if not self.processes:
            self.ax1.set_title("No process data available", color=TEXT_COLOR)
            self.draw()
            return
        
        # Extract data
        pids = [f'P{p.pid}' for p in self.processes]
        waiting_times = [p.waiting_time for p in self.processes]
        turnaround_times = [p.turnaround_time for p in self.processes]
        burst_times = [p.burst_time for p in self.processes]
        
        # Bar width and positions
        width = 0.35
        x = np.arange(len(pids))
        
        # Plot waiting and turnaround times
        self.ax1.bar(x - width/2, waiting_times, width, label='Waiting Time', color=ACCENT_COLOR, alpha=0.7)
        self.ax1.bar(x + width/2, turnaround_times, width, label='Turnaround Time', color=LIGHT_BLUE, alpha=0.7)
        
        self.ax1.set_xlabel('Process ID')
        self.ax1.set_ylabel('Time')
        self.ax1.set_title('Waiting and Turnaround Times')
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(pids)
        self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)
        
        # Plot burst times
        bars = self.ax2.bar(x, burst_times, color=[p.color for p in self.processes], alpha=0.7)
        
        self.ax2.set_xlabel('Process ID')
        self.ax2.set_ylabel('Time')
        self.ax2.set_title('Burst Times')
        self.ax2.set_xticks(x)
        self.ax2.set_xticklabels(pids)
        self.ax2.grid(True, alpha=0.3)
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            self.ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.1f}', ha='center', va='bottom', color=TEXT_COLOR)
        
        self.fig.tight_layout()
        self.draw()


class ProcessTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {DARK_COLOR};
                color: {TEXT_COLOR};
                gridline-color: {DARK_BLUE};
                border: none;
            }}
            QHeaderView::section {{
                background-color: {DARK_BLUE};
                color: {TEXT_COLOR};
                padding: 5px;
                border: 1px solid {DARK_BLUE};
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: {LIGHT_BLUE};
            }}
        """)
        
        # Set up the table
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "PID", "Arrival Time", "Burst Time", "Start Time", 
            "Finish Time", "Waiting Time", "Turnaround Time"
        ])
        
        # Set column widths
        header = self.horizontalHeader()
        for i in range(self.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
    
    def update_table(self, processes):
        self.setRowCount(0)  # Clear the table
        
        # Add processes to the table
        for process in processes:
            row_position = self.rowCount()
            self.insertRow(row_position)
            
            # Set the data
            self.setItem(row_position, 0, QTableWidgetItem(f"P{process.pid}"))
            self.setItem(row_position, 1, QTableWidgetItem(str(process.arrival_time)))
            self.setItem(row_position, 2, QTableWidgetItem(str(process.burst_time)))
            
            # Handle potentially None values
            start_time = str(process.start_time) if process.start_time is not None else "-"
            finish_time = str(process.finish_time) if process.finish_time is not None else "-"
            
            self.setItem(row_position, 3, QTableWidgetItem(start_time))
            self.setItem(row_position, 4, QTableWidgetItem(finish_time))
            self.setItem(row_position, 5, QTableWidgetItem(str(process.waiting_time)))
            self.setItem(row_position, 6, QTableWidgetItem(str(process.turnaround_time)))
            
            # Set color for the PID cell based on the process color
            pid_item = self.item(row_position, 0)
            color_tuple = [int(c * 255) for c in process.color[:3]]
            pid_item.setBackground(QColor(*color_tuple))
            
            # Make text readable based on background brightness
            brightness = sum(color_tuple) / 3
            text_color = Qt.white if brightness < 128 else Qt.black
            pid_item.setForeground(text_color)
            
            # Center align all items
            for col in range(self.columnCount()):
                item = self.item(row_position, col)
                item.setTextAlignment(Qt.AlignCenter)


class ProcessDashboardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Process Scheduling Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set the dark theme
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {DARK_COLOR};
                color: {TEXT_COLOR};
            }}
            QPushButton {{
                background-color: {DARK_BLUE};
                color: {TEXT_COLOR};
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {HIGHLIGHT_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
            }}
            QComboBox {{
                background-color: {DARK_BLUE};
                color: {TEXT_COLOR};
                border: none;
                padding: 5px;
                border-radius: 4px;
            }}
            QComboBox:hover {{
                background-color: {LIGHT_BLUE};
            }}
            QComboBox QAbstractItemView {{
                background-color: {DARK_COLOR};
                color: {TEXT_COLOR};
                selection-background-color: {LIGHT_BLUE};
            }}
            QLineEdit, QSpinBox {{
                background-color: {DARK_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {DARK_BLUE};
                padding: 5px;
                border-radius: 4px;
            }}
            QTabWidget::pane {{
                border: 1px solid {DARK_BLUE};
                background-color: {DARK_COLOR};
            }}
            QTabBar::tab {{
                background-color: {DARK_BLUE};
                color: {TEXT_COLOR};
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {LIGHT_BLUE};
            }}
            QTabBar::tab:hover {{
                background-color: {HIGHLIGHT_COLOR};
            }}
            QGroupBox {{
                border: 1px solid {DARK_BLUE};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0px 10px;
                color: {TEXT_COLOR};
            }}
        """)
        
        # Initialize the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget for different scheduling algorithms
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Initialize data
        self.processes = []
        self.schedulers = {
            "FCFS": FCFSScheduling(),
            "SJF (Non-preemptive)": SJFScheduling(preemptive=False),
            "SJF (Preemptive)": SJFScheduling(preemptive=True),
            "Round Robin": RoundRobinScheduling(time_quantum=2),
            "Priority (Non-preemptive)": PriorityScheduling(preemptive=False),
            "Priority (Preemptive)": PriorityScheduling(preemptive=True)
        }
        
        # Create tabs for each scheduling algorithm
        for name in self.schedulers.keys():
            tab = QWidget()
            self.tab_widget.addTab(tab, name)
            self.setup_algorithm_tab(tab, name)
        
        # Setup process management tab
        process_tab = QWidget()
        self.tab_widget.addTab(process_tab, "Process Management")
        self.setup_process_management_tab(process_tab)
        
        # Add some sample processes
        self.add_sample_processes()
    
    def setup_algorithm_tab(self, tab, algorithm_name):
        layout = QVBoxLayout(tab)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # Step button
        step_btn = QPushButton("Step")
        step_btn.clicked.connect(lambda: self.step_algorithm(algorithm_name))
        controls_layout.addWidget(step_btn)
        
        # Run button
        run_btn = QPushButton("Run Complete")
        run_btn.clicked.connect(lambda: self.run_algorithm(algorithm_name))
        controls_layout.addWidget(run_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(lambda: self.reset_algorithm(algorithm_name))
        controls_layout.addWidget(reset_btn)
        
        # Spacer
        controls_layout.addStretch()
        
        # Current time display
        time_label = QLabel("Current Time: 0")
        time_label.setObjectName(f"{algorithm_name}_time_label")
        controls_layout.addWidget(time_label)
        
        layout.addLayout(controls_layout)
        
        # Splitter for charts and table
        splitter = QSplitter(Qt.Vertical)
        
        # Upper area with charts
        upper_widget = QWidget()
        upper_layout = QVBoxLayout(upper_widget)
        
        # Gantt Chart
        gantt_chart = GanttChartWidget(width=10, height=2)
        gantt_chart.setObjectName(f"{algorithm_name}_gantt")
        upper_layout.addWidget(gantt_chart)
        
        # Summary metrics
        metrics_layout = QHBoxLayout()
        
        # Avg. Waiting Time
        avg_waiting_label = QLabel("Avg. Waiting Time: 0.0")
        avg_waiting_label.setObjectName(f"{algorithm_name}_avg_waiting")
        metrics_layout.addWidget(avg_waiting_label)
        
        # Avg. Turnaround Time
        avg_tat_label = QLabel("Avg. Turnaround Time: 0.0")
        avg_tat_label.setObjectName(f"{algorithm_name}_avg_tat")
        metrics_layout.addWidget(avg_tat_label)
        
        # Avg. Response Time
        avg_response_label = QLabel("Avg. Response Time: 0.0")
        avg_response_label.setObjectName(f"{algorithm_name}_avg_response")
        metrics_layout.addWidget(avg_response_label)
        
        upper_layout.addLayout(metrics_layout)
        
        # Process metrics charts
        process_metrics = ProcessMetricsWidget(width=10, height=4)
        process_metrics.setObjectName(f"{algorithm_name}_metrics")
        upper_layout.addWidget(process_metrics)
        
        splitter.addWidget(upper_widget)
        
        # Process table
        process_table = ProcessTableWidget()
        process_table.setObjectName(f"{algorithm_name}_table")
        splitter.addWidget(process_table)
        
        layout.addWidget(splitter)
        
        # Set initial stretch factors
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
    
    def setup_process_management_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # Process input form
        form_group = QGroupBox("Add New Process")
        form_layout = QFormLayout(form_group)
        
        # Process ID
        self.pid_input = QSpinBox()
        self.pid_input.setMinimum(1)
        self.pid_input.setMaximum(999)
        form_layout.addRow("Process ID:", self.pid_input)
        
        # Arrival Time
        self.arrival_input = QSpinBox()
        self.arrival_input.setMinimum(0)
        form_layout.addRow("Arrival Time:", self.arrival_input)
        
        # Burst Time
        self.burst_input = QSpinBox()
        self.burst_input.setMinimum(1)
        form_layout.addRow("Burst Time:", self.burst_input)
        
        # Priority (for priority scheduling)
        self.priority_input = QSpinBox()
        self.priority_input.setMinimum(1)
        self.priority_input.setMaximum(10)
        form_layout.addRow("Priority (1-10, lower is higher):", self.priority_input)
        
        # Add Process button
        add_btn = QPushButton("Add Process")
        add_btn.clicked.connect(self.add_process)
        form_layout.addRow("", add_btn)
        
        layout.addWidget(form_group)
        
        # Process list
        list_group = QGroupBox("Current Processes")
        list_layout = QVBoxLayout(list_group)
        
        self.process_table = ProcessTableWidget()
        list_layout.addWidget(self.process_table)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_processes)
        controls_layout.addWidget(clear_btn)
        
        sample_btn = QPushButton("Load Sample Processes")
        sample_btn.clicked.connect(self.add_sample_processes)
        controls_layout.addWidget(sample_btn)
        
        list_layout.addLayout(controls_layout)
        layout.addWidget(list_group)
    
    def add_process(self):
        pid = self.pid_input.value()
        arrival_time = self.arrival_input.value()
        burst_time = self.burst_input.value()
        priority = self.priority_input.value()
        
        # Check if process ID already exists
        if any(p.pid == pid for p in self.processes):
            QMessageBox.warning(self, "Duplicate ID", "A process with this ID already exists!")
            return
        
        process = Process(pid, arrival_time, burst_time, priority)
        self.processes.append(process)
        
        # Reset input values
        self.pid_input.setValue(max([p.pid for p in self.processes], default=0) + 1)
        self.arrival_input.setValue(0)
        self.burst_input.setValue(1)
        self.priority_input.setValue(1)
        
        # Update process table and all algorithm tabs
        self.update_process_displays()
    
    def clear_processes(self):
        self.processes = []
        self.pid_input.setValue(1)
        self.update_process_displays()
    
    def add_sample_processes(self):
        self.processes = [
            Process(1, 0, 5, 3),
            Process(2, 1, 3, 2),
            Process(3, 2, 8, 4),
            Process(4, 3, 2, 1),
            Process(5, 4, 4, 5)
        ]
        self.pid_input.setValue(len(self.processes) + 1)
        self.update_process_displays()
    
    def update_process_displays(self):
        # Update the process table in the management tab
        self.process_table.update_table(self.processes)
        
        # Update all algorithm tabs
        for name, scheduler in self.schedulers.items():
            # Create a deep copy of the processes for each scheduler
            scheduler.processes = [
                Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                for p in self.processes
            ]
            
            # Reset the algorithm
            self.reset_algorithm(name)
    
    def step_algorithm(self, algorithm_name):
        scheduler = self.schedulers[algorithm_name]
        
        # Execute one step of the algorithm
        if scheduler.step():
            # Update the UI
            self.update_algorithm_display(algorithm_name)
        else:
            QMessageBox.information(self, "Complete", "All processes have completed execution!")
    
    def run_algorithm(self, algorithm_name):
        scheduler = self.schedulers[algorithm_name]
        
        # Run until completion
        while scheduler.step():
            pass
        
        # Update the UI
        self.update_algorithm_display(algorithm_name)
        QMessageBox.information(self, "Complete", "All processes have completed execution!")
    
    def reset_algorithm(self, algorithm_name):
        scheduler = self.schedulers[algorithm_name]
        scheduler.reset()
        
        # Update the UI
        self.update_algorithm_display(algorithm_name)
    
    def update_algorithm_display(self, algorithm_name):
        scheduler = self.schedulers[algorithm_name]
        
        # Update time label
        time_label = self.findChild(QLabel, f"{algorithm_name}_time_label")
        if time_label:
            time_label.setText(f"Current Time: {scheduler.time}")
        
        # Update Gantt chart
        gantt_chart = self.findChild(GanttChartWidget, f"{algorithm_name}_gantt")
        if gantt_chart:
            gantt_chart.update_chart(scheduler)
        
        # Update process metrics
        process_metrics = self.findChild(ProcessMetricsWidget, f"{algorithm_name}_metrics")
        if process_metrics:
            process_metrics.update_metrics(scheduler.processes)
        
        # Update process table
        process_table = self.findChild(ProcessTableWidget, f"{algorithm_name}_table")
        if process_table:
            process_table.update_table(scheduler.processes)
        
        # Update average metrics
        avg_waiting_label = self.findChild(QLabel, f"{algorithm_name}_avg_waiting")
        avg_tat_label = self.findChild(QLabel, f"{algorithm_name}_avg_tat")
        avg_response_label = self.findChild(QLabel, f"{algorithm_name}_avg_response")
        
        if avg_waiting_label:
            avg_waiting_label.setText(f"Avg. Waiting Time: {scheduler.get_average_waiting_time():.2f}")
        
        if avg_tat_label:
            avg_tat_label.setText(f"Avg. Turnaround Time: {scheduler.get_average_turnaround_time():.2f}")
        
        if avg_response_label:
            avg_response_label.setText(f"Avg. Response Time: {scheduler.get_average_response_time():.2f}")


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app_font = QFont("Arial", 10)
    app.setFont(app_font)
    
    # Create and show the dashboard
    window = ProcessDashboardApp()
    window.show()
    sys.exit(app.exec_())
