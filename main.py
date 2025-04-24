import tkinter as tk
from tkinter import ttk
from scheduler_original import run_and_time_scheduler as run_original
from scheduler_optimized import run_and_time_scheduler as run_optimized
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
        self.sidebar_frame = tk.Frame(self.root, bg=styles.COLOR_PRIMARY, width=200)
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
        title = tk.Label(self.content_frame, text="\u2699\ufe0f Run Schedulers", font=styles.APP_TITLE_FONT, bg=styles.COLOR_BG)
        title.pack(pady=20)

        dropdown_frame = tk.Frame(self.content_frame, bg=styles.COLOR_BG)
        dropdown_frame.pack(pady=10)

        tk.Label(dropdown_frame, text="Number of Planes:", font=styles.LABEL_FONT, bg=styles.COLOR_BG).pack(side=tk.LEFT)
        self.plane_count_var = tk.StringVar()
        dropdown = ttk.Combobox(dropdown_frame, textvariable=self.plane_count_var, values=["100", "500", "1000", "2000", "5000"])
        dropdown.pack(side=tk.LEFT, padx=10)
        dropdown.current(0)

        button_frame = tk.Frame(self.content_frame, bg=styles.COLOR_BG)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Run Inefficient Scheduler", font=styles.BUTTON_FONT, command=self.run_original).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Run Optimized Scheduler", font=styles.BUTTON_FONT, command=self.run_optimized).pack(side=tk.LEFT, padx=20)

        self.status_label = tk.Label(self.content_frame, text="", font=styles.LABEL_FONT, bg=styles.COLOR_BG)
        self.status_label.pack(pady=10)

        self.log_output = tk.Text(self.content_frame, height=10, bg="black", fg="lime", font=("Consolas", 10))
        self.log_output.pack(padx=20, pady=10, fill=tk.X)
        self.log("Log initialized...\n")

        # Live Graph
        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.content_frame)
        self.canvas.get_tk_widget().pack(padx=20, pady=10, fill=tk.X)
        self.x_vals = []
        self.y_vals = []
        self.line, = self.ax.plot([], [], color='green')
        self.ax.set_title("Live Scheduling Progress")
        self.ax.set_xlabel("Scheduled Planes")
        self.ax.set_ylabel("Time (ms)")

        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.table = ttk.Treeview(
            table_frame,
            columns=("plane_id", "scheduled_at", "type", "priority"),
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
            self.table.column(col, anchor="center", width=200)

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
        self.canvas.draw()

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
                item["priority"]
            ))

    def show_stats(self, schedule, ms, mode):
        total_planes = len(schedule)
        scheduled_times = [item["scheduled_at"] for item in schedule]
        earliest = min(scheduled_times)
        latest = max(scheduled_times)
        avg_wait = round(sum(scheduled_times) / total_planes, 2)

        summary = f"""
Scheduler: {mode}
Total Planes Scheduled: {total_planes}
Execution Time: {ms} ms
Earliest Scheduled Time: {earliest}
Latest Scheduled Time: {latest}
Average Wait Time: {avg_wait}
        """.strip()

        self.status_label.config(text=summary, justify=tk.LEFT, font=("Segoe UI", 12), bg=styles.COLOR_BG)
        self.log(summary)

    def run_original(self):
        count = int(self.plane_count_var.get())
        self.log(f"Generating {count} planes for original scheduler...")
        generate_planes(count)
        self.status_label.config(text="\u23f3 Scheduling planes...", fg="orange")
        self.root.update()
        schedule, ms = run_original()
        self.update_live_graph(count, ms)
        self.status_label.config(text=f"Original Scheduler Time: {ms} ms", fg=styles.COLOR_DANGER)
        self.update_table(schedule)
        self.show_stats(schedule, ms, "Original")

    def run_optimized(self):
        count = int(self.plane_count_var.get())
        self.log(f"Generating {count} planes for optimized scheduler...")
        generate_planes(count)
        self.status_label.config(text="\u23f3 Scheduling planes...", fg="orange")
        self.root.update()
        schedule, ms = run_optimized()
        self.update_live_graph(count, ms)
        self.status_label.config(text=f"Optimized Scheduler Time: {ms} ms", fg=styles.COLOR_PRIMARY)
        self.update_table(schedule)
        self.show_stats(schedule, ms, "Optimized")

if __name__ == "__main__":
    root = tk.Tk()
    app = AirportSchedulerApp(root)
    root.mainloop()
