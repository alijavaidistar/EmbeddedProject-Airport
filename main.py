import tkinter as tk
from tkinter import ttk
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

class AirportSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airport Runway Scheduler")
        self.root.state('zoomed')

        self.create_layout()
        self.show_home()

    def create_layout(self):
        self.sidebar_frame = tk.Frame(self.root, bg=styles.COLOR_SECONDARY, width=220)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.content_frame = tk.Frame(self.root, bg=styles.COLOR_BG)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(self.sidebar_frame, text="Menu", bg=styles.COLOR_PRIMARY, fg="white", font=styles.APP_TITLE_FONT).pack(pady=20)

        menu_items = [
            ("\ud83c\udfe0 Home", self.show_home),
            ("\u2699\ufe0f Run Schedulers", self.show_scheduler_buttons),
            ("\ud83d\udcc8 Performance Graph", self.show_performance_graph),
            ("\u274c Exit", self.root.quit)
        ]

        for label, command in menu_items:
            tk.Button(
                self.sidebar_frame,
                text=label,
                font=styles.BUTTON_FONT,
                bg="white",
                fg=styles.COLOR_PRIMARY,
                relief="flat",
                command=command
            ).pack(fill=tk.X, padx=10, pady=5)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_content()
        title = tk.Label(self.content_frame, text="\u2708\ufe0f Welcome to Airport Runway Scheduler", font=styles.APP_TITLE_FONT, bg=styles.COLOR_BG)
        title.pack(pady=40)

        description = tk.Label(
            self.content_frame,
            text="This app simulates runway assignments and compares scheduling performance.\nUse the sidebar to navigate.",
            font=styles.LABEL_FONT,
            bg=styles.COLOR_BG
        )
        description.pack(pady=10)

    def show_scheduler_buttons(self):
        self.clear_content()

        # SCROLLABLE CANVAS WRAPPER
        container = tk.Frame(self.content_frame, bg=styles.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg=styles.COLOR_BG)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=styles.COLOR_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- UI CONTENT INSIDE scrollable_frame ---

        title = tk.Label(scrollable_frame, text="⚙️ Run Schedulers", font=styles.APP_TITLE_FONT, bg=styles.COLOR_BG,
                         fg=styles.COLOR_TEXT)
        title.pack(pady=20)

        dropdown_frame = tk.Frame(scrollable_frame, bg=styles.COLOR_BG)
        dropdown_frame.pack(pady=10)

        # Plane Count
        tk.Label(dropdown_frame, text="Number of Planes:", font=styles.LABEL_FONT, bg=styles.COLOR_BG,
                 fg=styles.COLOR_TEXT).pack(side=tk.LEFT)
        self.plane_count_var = tk.StringVar()
        dropdown = ttk.Combobox(dropdown_frame, textvariable=self.plane_count_var,
                                values=["100", "500", "1000", "2000", "5000"])
        dropdown.pack(side=tk.LEFT, padx=10)
        dropdown.current(0)

        # Runway Count
        tk.Label(dropdown_frame, text="Number of Runways:", font=styles.LABEL_FONT, bg=styles.COLOR_BG,
                 fg=styles.COLOR_TEXT).pack(side=tk.LEFT)
        self.runway_count_var = tk.StringVar()
        runway_dropdown = ttk.Combobox(dropdown_frame, textvariable=self.runway_count_var,
                                       values=["1", "2", "3", "4", "5"])
        runway_dropdown.pack(side=tk.LEFT, padx=10)
        runway_dropdown.current(0)

        # Algorithm Dropdown
        algo_frame = tk.Frame(scrollable_frame, bg=styles.COLOR_BG)
        algo_frame.pack(pady=10)

        tk.Label(algo_frame, text="Select Algorithm:", font=styles.LABEL_FONT, bg=styles.COLOR_BG,
                 fg=styles.COLOR_TEXT).pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="FCFS")
        algo_menu = ttk.Combobox(algo_frame, textvariable=self.algo_var,
                                 values=["FCFS", "Optimized", "EDF", "Round Robin", "Priority Preemptive"])
        algo_menu.pack(side=tk.LEFT, padx=10)

        tk.Button(algo_frame, text="Run Scheduler", font=styles.BUTTON_FONT, command=self.run_selected_scheduler,
                  bg=styles.COLOR_SECONDARY, fg=styles.COLOR_PRIMARY, activebackground=styles.COLOR_ACCENT).pack(
            side=tk.LEFT, padx=20)

        # Status label
        self.status_label = tk.Label(scrollable_frame, text="", font=styles.LABEL_FONT, bg=styles.COLOR_BG,
                                     fg=styles.COLOR_PRIMARY)
        self.status_label.pack(pady=10)

        # Runway Visualizer Canvas
        self.runway_canvas = tk.Canvas(scrollable_frame, bg="black", height=200)
        self.runway_canvas.pack(padx=20, pady=10, fill=tk.X)

        for i in range(3):
            y = 50 * (i + 1)
            self.runway_canvas.create_line(50, y, 750, y, fill="white", width=3)
            self.runway_canvas.create_text(30, y, text=f"RWY {i + 1}", fill="lime", font=styles.LABEL_FONT)

        # Live Graph
        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=scrollable_frame)
        self.graph_canvas.get_tk_widget().pack(padx=20, pady=10, fill=tk.X)
        self.x_vals = []
        self.y_vals = []
        self.line, = self.ax.plot([], [], color='green')
        self.ax.set_title("Live Scheduling Progress", color=styles.COLOR_TEXT)
        self.ax.set_xlabel("Scheduled Planes", color=styles.COLOR_TEXT)
        self.ax.set_ylabel("Time (ms)", color=styles.COLOR_TEXT)
        self.ax.tick_params(colors=styles.COLOR_TEXT)

        # Logs
        self.log_output = tk.Text(scrollable_frame, height=10, bg="black", fg="lime", font=styles.LOG_FONT)
        self.log_output.pack(padx=20, pady=10, fill=tk.X)
        self.log("Log initialized...\n")

        # Table
        table_frame = tk.Frame(scrollable_frame)
        table_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.table = ttk.Treeview(
            table_frame,
            columns=("plane_id", "scheduled_at", "type", "priority", "runway_id"),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.table.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.config(command=self.table.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        for col in self.table["columns"]:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, anchor="center", width=150)

        self.table.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_output.insert(tk.END, f"{timestamp} {message}\n")
        self.log_output.see(tk.END)

    def update_live_graph(self, count, elapsed):
        self.x_vals.append(count)
        self.y_vals.append(elapsed)
        self.line.set_data(self.x_vals, self.y_vals)
        self.ax.relim()
        self.ax.autoscale_view()
        #self.canvas.draw()
        self.graph_canvas.draw()

    def show_performance_graph(self):
        self.clear_content()
        try:
            labels = []
            times = []

            with open("results/execution_times.csv", newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    labels.append(row[1])
                    times.append(float(row[2]))

            plt.figure(figsize=(6, 4))
            plt.bar(labels, times, color=['red', 'blue'])
            plt.title("Scheduler Performance Comparison")
            plt.ylabel("Execution Time (ms)")
            plt.xlabel("Version")
            plt.tight_layout()
            plt.show()

        except FileNotFoundError:
            tk.Label(self.content_frame, text="No performance data found!", font=styles.LABEL_FONT, fg=styles.COLOR_WARNING).pack(pady=10)

    def update_table(self, schedule):
        for row in self.table.get_children():
            self.table.delete(row)
        for item in schedule:
            self.table.insert("", tk.END, values=(
                item["plane_id"],
                item["scheduled_at"],
                item["type"],
                item["priority"],
                item.get("runway_id", "N/A")

            ))

    def show_stats(self, schedule, ms, mode):
        total_planes = len(schedule)
        if total_planes == 0:
            return

        # Extract times and sort
        scheduled_times = [item["scheduled_at"] for item in schedule]
        arrival_times = [item.get("arrival_time", 0) for item in schedule]
        priorities = [item.get("priority", 1) for item in schedule]

        earliest = min(scheduled_times)
        latest = max(scheduled_times)
        avg_wait = round(sum(st - at for st, at in zip(scheduled_times, arrival_times)) / total_planes, 2)

        # Metric 1: Average Delay per Plane
        avg_delay = avg_wait

        # Metric 2: Runway Utilization %
        total_runway_time = latest - earliest + 1
        total_time_elapsed = latest + 1
        runway_util = round((total_runway_time / total_time_elapsed) * 100, 2)

        # Metric 3: Priority-Weighted Completion Score
        weighted_score = round(
            sum(p * (st - at) for p, st, at in zip(priorities, scheduled_times, arrival_times)) / total_planes, 2)

        summary = f"""
    Scheduler: {mode}
    Total Planes Scheduled: {total_planes}
    Execution Time: {ms} ms
    Earliest Scheduled Time: {earliest}
    Latest Scheduled Time: {latest}
    Average Delay per Plane: {avg_delay}
    Runway Utilization: {runway_util}%
    Priority-Weighted Completion Score: {weighted_score}
        """.strip()

        self.status_label.config(text=summary, justify=tk.LEFT, font=("Segoe UI", 12), bg=styles.COLOR_BG)
        self.log(summary)


    def run_selected_scheduler(self):
        count = int(self.plane_count_var.get())
        algo = self.algo_var.get()

        self.log(f"Generating {count} planes for {algo} scheduler...")
        generate_planes(count)
        self.status_label.config(text="⏳ Scheduling planes...", fg="orange")
        self.root.update()

        if algo == "FCFS":
            schedule, ms = run_original()
        elif algo == "Optimized":
            num_runways = int(self.runway_count_var.get())
            schedule, ms = run_optimized(num_runways=num_runways, progress_callback=self.update_live_graph)
        elif algo == "EDF":
            schedule, ms = run_edf_scheduler(progress_callback=self.update_live_graph)
        elif algo == "Round Robin":
            schedule, ms = run_rr_scheduler(progress_callback=self.update_live_graph)
        elif algo == "Priority Preemptive":
            schedule, ms = run_pp_scheduler(progress_callback=self.update_live_graph)
        else:
            self.log("Unsupported scheduler selected.")
            return

        self.update_live_graph(count, ms)
        self.status_label.config(text=f"{algo} Scheduler Time: {ms} ms", fg=styles.COLOR_SUCCESS)
        self.update_table(schedule)
        self.show_stats(schedule, ms, algo)

if __name__ == "__main__":
    root = tk.Tk()
    app = AirportSchedulerApp(root)
    root.mainloop()



