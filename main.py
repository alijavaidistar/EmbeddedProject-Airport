import tkinter as tk
from tkinter import ttk, filedialog
from scheduler_original import run_and_time_scheduler as run_original
from scheduler_optimized import run_and_time_scheduler as run_optimized
from edf_scheduler import run_edf_scheduler
from round_robin_scheduler import run_rr_scheduler
from priority_preemptive_scheduler import run_pp_scheduler
from generate_planes import generate_planes
from theme import styles
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import time
import os
import inspect

class AirportSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airport Runway Scheduler")
        self.root.state('zoomed')
        
        # Initialize data structures with smoothing buffers
        self.scheduler_data = {
            "FCFS": {"x": [], "y": [], "color": "#FF5722", "buffer": []},
            "Optimized": {"x": [], "y": [], "color": "#4CAF50", "buffer": []},
            "EDF": {"x": [], "y": [], "color": "#2196F3", "buffer": []},
            "Round Robin": {"x": [], "y": [], "color": "#9C27B0", "buffer": []},
            "Priority Preemptive": {"x": [], "y": [], "color": "#FFC107", "buffer": []}
        }
        
        os.makedirs("results", exist_ok=True)
        
        self.create_layout()
        self.show_home()

    def create_layout(self):
        # Sidebar
        self.sidebar_frame = tk.Frame(self.root, bg=styles.COLOR_SECONDARY, width=220)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Content area
        self.content_frame = tk.Frame(self.root, bg=styles.COLOR_BG)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Menu buttons
        menu_items = [
            ("🏠 Home", self.show_home),
            ("⚙️ Run Schedulers", self.show_scheduler_buttons),
            ("📊 Performance Graph", self.show_performance_graph),
            ("🚪 Exit", self.root.quit)
        ]

        tk.Label(self.sidebar_frame, 
                text="Menu", 
                bg=styles.COLOR_SECONDARY,
                fg=styles.COLOR_TEXT,
                font=("Arial", 14, "bold")).pack(pady=20)
        
        for label, command in menu_items:
            btn = tk.Button(
                self.sidebar_frame,
                text=label,
                font=("Arial", 12),
                bg=styles.COLOR_SECONDARY,
                fg=styles.COLOR_TEXT,
                relief="flat",
                command=command
            )
            btn.pack(fill=tk.X, padx=10, pady=5)

    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        """Show the home screen"""
        self.clear_content()
        
        tk.Label(self.content_frame, 
                text="✈️ Airport Runway Scheduler",
                font=("Arial", 24, "bold"),
                bg=styles.COLOR_BG,
                fg=styles.COLOR_TEXT).pack(pady=50)
                
        tk.Label(self.content_frame,
                text="Compare different scheduling algorithms for airport runway management",
                font=("Arial", 12),
                bg=styles.COLOR_BG,
                fg=styles.COLOR_TEXT).pack(pady=10)
                
        tk.Label(self.content_frame,
                text="Use the menu to run schedulers and view performance results",
                font=("Arial", 10),
                bg=styles.COLOR_BG,
                fg=styles.COLOR_TEXT).pack()

    def show_scheduler_buttons(self):
        self.clear_content()
        
        # Main container with scrollbar
        container = tk.Frame(self.content_frame, bg=styles.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container, bg=styles.COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=styles.COLOR_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control Panel
        control_frame = tk.Frame(scrollable_frame, bg=styles.COLOR_BG)
        control_frame.pack(pady=20, fill=tk.X)
        
        # Plane count
        tk.Label(control_frame, 
                text="Planes:", 
                bg=styles.COLOR_BG,
                fg=styles.COLOR_TEXT).grid(row=0, column=0, padx=5)
        self.plane_count = ttk.Combobox(control_frame, values=["100", "500", "1000", "2000", "5000"])
        self.plane_count.current(0)
        self.plane_count.grid(row=0, column=1, padx=5)
        
        # Runway count
        tk.Label(control_frame, 
                text="Runways:", 
                bg=styles.COLOR_BG,
                fg=styles.COLOR_TEXT).grid(row=0, column=2, padx=5)
        self.runway_count = ttk.Combobox(control_frame, values=["1", "2", "3", "4", "5"])
        self.runway_count.current(0)
        self.runway_count.grid(row=0, column=3, padx=5)
        
        # Algorithm selection
        tk.Label(control_frame, 
                text="Algorithm:", 
                bg=styles.COLOR_BG,
                fg=styles.COLOR_TEXT).grid(row=0, column=4, padx=5)
        self.algorithm = ttk.Combobox(control_frame, 
                                    values=["FCFS", "Optimized", "EDF", "Round Robin", "Priority Preemptive"])
        self.algorithm.current(0)
        self.algorithm.grid(row=0, column=5, padx=5)
        
        # Run button
        ttk.Button(control_frame, 
                  text="Run Scheduler", 
                  command=self.run_scheduler).grid(row=0, column=6, padx=10)

        # Live Graph
        self.init_live_graph(scrollable_frame)
        
        # Results Table
        self.init_results_table(scrollable_frame)
        
        # Status Log
        self.log_output = tk.Text(
            scrollable_frame, 
            height=8, 
            bg=styles.COLOR_SECONDARY,
            fg=styles.COLOR_SUCCESS,
            font=("Consolas", 10)
        )
        self.log_output.pack(fill=tk.X, padx=20, pady=10)
        self.log("System ready. Select parameters and run a scheduler.")

    def init_live_graph(self, parent):
        """Initialize the live progress graph"""
        plt.style.use('dark_background')
        
        self.fig, self.ax = plt.subplots(figsize=(10, 4), facecolor=styles.COLOR_BG)
        self.ax.set_title("Live Scheduling Progress", 
                         fontsize=12, 
                         color=styles.COLOR_TEXT)
        self.ax.set_xlabel("Planes Scheduled", 
                          fontsize=10, 
                          color=styles.COLOR_TEXT)
        self.ax.set_ylabel("Time (ms)", 
                          fontsize=10, 
                          color=styles.COLOR_TEXT)
        self.ax.grid(True, linestyle='--', alpha=0.6, color=styles.COLOR_SECONDARY)
        
        self.ax.set_facecolor(styles.COLOR_BG)
        
        # Create lines for each scheduler
        self.graph_lines = {}
        for algo, props in self.scheduler_data.items():
            line, = self.ax.plot([], [], label=algo, color=props["color"], linewidth=2)
            self.graph_lines[algo] = line
        
        self.ax.legend(facecolor=styles.COLOR_SECONDARY, 
                      labelcolor=styles.COLOR_TEXT)
        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def init_results_table(self, parent):
        """Initialize the results comparison table"""
        frame = tk.Frame(parent, bg=styles.COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(frame, 
                text="📋 Scheduler Results Comparison", 
                font=("Arial", 12, "bold"),
                bg=styles.COLOR_BG,
                fg=styles.COLOR_TEXT).pack(anchor="w")
        
        self.results_table = ttk.Treeview(frame, 
                                        columns=("Algorithm", "Time (ms)", "Avg Delay", "Utilization"), 
                                        show="headings",
                                        height=5)
        
        # Configure columns
        for col in ["Algorithm", "Time (ms)", "Avg Delay", "Utilization"]:
            self.results_table.heading(col, text=col)
            self.results_table.column(col, width=120, anchor="center")
        
        self.results_table.pack(fill=tk.BOTH, expand=True)
        
        # Clear button
        ttk.Button(frame, 
                  text="Clear All Results", 
                  command=self.clear_results).pack(side=tk.RIGHT, pady=5)

    def log(self, message):
        """Add a message to the log"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_output.insert(tk.END, f"{timestamp} {message}\n")
        self.log_output.see(tk.END)

    def update_live_graph(self, algo, count, time):
        """Update the graph with new data points"""
        if algo not in self.scheduler_data:
            return

        # Add to buffer for smoothing
        self.scheduler_data[algo]["buffer"].append((count, time))
        
        # Only update every 5 points or when we have more than 20 points buffered
        if len(self.scheduler_data[algo]["buffer"]) % 5 == 0 or len(self.scheduler_data[algo]["buffer"]) > 20:
            # Get the most recent point from buffer
            count, time = self.scheduler_data[algo]["buffer"][-1]
            
            self.scheduler_data[algo]["x"].append(count)
            self.scheduler_data[algo]["y"].append(time)
            self.graph_lines[algo].set_data(self.scheduler_data[algo]["x"], self.scheduler_data[algo]["y"])
            
            # Clear buffer if it's getting too large
            if len(self.scheduler_data[algo]["buffer"]) > 20:
                self.scheduler_data[algo]["buffer"] = self.scheduler_data[algo]["buffer"][-10:]
            
            self.ax.relim()
            self.ax.autoscale_view()
            self.graph_canvas.draw()
            self.graph_canvas.flush_events()

    def run_scheduler(self):
        """Run the selected scheduler"""
        algo = self.algorithm.get()
        count = int(self.plane_count.get())
        runways = int(self.runway_count.get())

        # Clear previous data and buffers
        self.scheduler_data[algo]["x"] = []
        self.scheduler_data[algo]["y"] = []
        self.scheduler_data[algo]["buffer"] = []
        self.graph_lines[algo].set_data([], [])
        self.graph_canvas.draw()

        self.log(f"Running {algo} scheduler with {count} planes and {runways} runways...")
        generate_planes(count)

        def progress_callback(completed, elapsed):
            if algo == "Round Robin" and completed > count:
                completed = count
            self.update_live_graph(algo, completed, elapsed)
            self.root.update()

        try:
            if algo == "FCFS":
                schedule, time_taken = run_original(num_runways=runways, progress_callback=progress_callback)
            elif algo == "Optimized":
                schedule, time_taken = run_optimized(num_runways=runways, progress_callback=progress_callback)
            elif algo == "EDF":
                schedule, time_taken = run_edf_scheduler(progress_callback=progress_callback)
            elif algo == "Round Robin":
                schedule, time_taken = run_rr_scheduler(progress_callback=progress_callback)
            elif algo == "Priority Preemptive":
                schedule, time_taken = run_pp_scheduler(progress_callback=progress_callback)

            # Final update with all points
            self.scheduler_data[algo]["x"].extend([x for x, y in self.scheduler_data[algo]["buffer"]])
            self.scheduler_data[algo]["y"].extend([y for x, y in self.scheduler_data[algo]["buffer"]])
            self.graph_lines[algo].set_data(self.scheduler_data[algo]["x"], self.scheduler_data[algo]["y"])
            self.ax.relim()
            self.ax.autoscale_view()
            self.graph_canvas.draw()
            
            self.add_result(algo, time_taken, schedule)
            self.save_to_csv(algo, time_taken)
            self.log(f"{algo} completed in {time_taken:.2f} ms")

        except Exception as e:
            self.log(f"Error running {algo}: {str(e)}")

    def save_to_csv(self, algorithm, time_ms):
        """Save scheduler results to CSV file"""
        filepath = "results/execution_times.csv"
        file_exists = os.path.isfile(filepath)

        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["timestamp", "algorithm", "time_ms"])
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), algorithm, time_ms])

    def add_result(self, algorithm, time_ms, schedule):
        """Add a result to the comparison table"""
        avg_delay = self.calculate_avg_delay(schedule)
        utilization = self.calculate_utilization(schedule)
        self.results_table.insert("", tk.END, 
                                values=(algorithm, f"{time_ms:.2f}", 
                                      f"{avg_delay:.2f}", f"{utilization:.1f}%"))

    def calculate_avg_delay(self, schedule):
        """Calculate average delay from schedule"""
        if not schedule:
            return 0
        delays = [plane["scheduled_at"] - plane.get("arrival_time", 0) for plane in schedule]
        return sum(delays) / len(delays)

    def calculate_utilization(self, schedule):
        """Calculate runway utilization percentage"""
        if not schedule:
            return 0
        last_time = max(plane["scheduled_at"] for plane in schedule)
        return (last_time / (last_time + 1)) * 100

    def clear_results(self):
        """Clear all results from the table and graphs"""
        for item in self.results_table.get_children():
            self.results_table.delete(item)
        for algo in self.scheduler_data:
            self.scheduler_data[algo]["x"] = []
            self.scheduler_data[algo]["y"] = []
            self.scheduler_data[algo]["buffer"] = []
            self.graph_lines[algo].set_data([], [])
        self.graph_canvas.draw()
        self.log("Cleared all results")

    def get_best_scheduler_times(self):
        """Get the best recorded times for current simulation parameters"""
        self.log("Starting performance data generation...")  # Debug line
        try:
            num_planes = int(self.plane_count.get())
            num_runways = int(self.runway_count.get())
            self.log(f"Parameters: {num_planes} planes, {num_runways} runways")  # Debug line
        except Exception as e:
            self.log(f"Parameter error: {str(e)}")
            return {}

        best_times = {}
        schedulers = [
            ("FCFS", run_original),
            ("Optimized", run_optimized),
            ("EDF", run_edf_scheduler),
            ("Round Robin", run_rr_scheduler),
            ("Priority Preemptive", run_pp_scheduler)
        ]

        for algo_name, scheduler_func in schedulers:
            try:
                self.log(f"Running {algo_name}...")  # Debug line
                generate_planes(num_planes)
                _, exec_time = scheduler_func(num_runways=num_runways) if "runways" in inspect.signature(scheduler_func).parameters else scheduler_func()
                best_times[algo_name] = exec_time
                self.log(f"{algo_name} completed in {exec_time:.2f} ms")  # Debug line
            except Exception as e:
                self.log(f"Error in {algo_name}: {str(e)}")  # Debug line
                best_times[algo_name] = 0

        return best_times

    def show_performance_graph(self):
        """Show real performance comparison using actual scheduler execution times"""
        self.clear_content()
        
        # Create loading indicator
        loading_label = tk.Label(self.content_frame, 
                            text="Generating performance data...",
                            font=("Arial", 12),
                            bg=styles.COLOR_BG,
                            fg=styles.COLOR_TEXT)
        loading_label.pack(pady=50)
        self.root.update()  # Force UI update

        # Get actual recorded execution times
        best_times = self.get_best_scheduler_times()
        loading_label.destroy()

        if not best_times:
            tk.Label(self.content_frame, 
                    text="Error: No data to display.",
                    font=("Arial", 12),
                    fg="red",
                    bg=styles.COLOR_BG).pack(pady=20)
            return

        # Create the graph
        fig, ax = plt.subplots(figsize=(10, 6), facecolor=styles.COLOR_BG)
        
        algorithms = ["FCFS", "Optimized", "EDF", "Round Robin", "Priority Preemptive"]
        times = [best_times.get(algo, 0) for algo in algorithms]

        bars = ax.bar(algorithms, times, 
                    color=[self.scheduler_data[algo]["color"] for algo in algorithms],
                    edgecolor='white')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f"{height:.1f} ms",
                    ha='center', va='bottom',
                    color='white', fontsize=10)

        # Style the graph
        ax.set_title(f"Algorithm Performance Comparison (Best Times)",
                    color='white', pad=20)
        ax.set_xlabel("Scheduling Algorithm", color='white')
        ax.set_ylabel("Execution Time (ms)", color='white')
        ax.grid(axis='y', linestyle='--', alpha=0.3, color='white')
        ax.set_facecolor(styles.COLOR_SECONDARY)

        for spine in ax.spines.values():
            spine.set_color('white')
        ax.tick_params(colors='white')

        # Embed in UI
        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Export button
        ttk.Button(self.content_frame,
                text="Export Graph",
                command=lambda: self.export_graph(fig)).pack(pady=10)

    def export_graph(self, fig):
        """Export the current graph to a file"""
        filetypes = [
            ("PNG Image", "*.png"),
            ("PDF Document", "*.pdf"),
            ("SVG Vector", "*.svg")
        ]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=filetypes,
            title="Save Performance Graph"
        )

        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            self.log(f"Graph exported to {filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AirportSchedulerApp(root)
    root.mainloop()