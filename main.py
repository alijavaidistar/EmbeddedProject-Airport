import tkinter as tk
from tkinter import ttk
from scheduler_original import run_and_time_scheduler as run_original
from scheduler_optimized import run_and_time_scheduler as run_optimized
from theme import styles
import matplotlib.pyplot as plt
import csv

class AirportSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airport Runway Scheduler")
        self.root.state('zoomed')  # Fullscreen including taskbar

        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="✈️ Airport Runway Scheduler", font=styles.APP_TITLE_FONT)
        title.pack(pady=20)

        # Buttons Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Run Inefficient Scheduler", font=styles.BUTTON_FONT, command=self.run_original).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Run Optimized Scheduler", font=styles.BUTTON_FONT, command=self.run_optimized).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Show Performance Graph", font=styles.BUTTON_FONT, command=self.show_performance_graph).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Exit", font=styles.BUTTON_FONT, command=self.root.quit).pack(side=tk.LEFT, padx=20)

        # Status Label
        self.status_label = tk.Label(self.root, text="", font=styles.LABEL_FONT, fg=styles.COLOR_SUCCESS)
        self.status_label.pack(pady=10)

        # Table Frame with Scrollbars
        table_frame = tk.Frame(self.root)
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

    def run_original(self):
        schedule, ms = run_original()
        self.status_label.config(text=f"Original Scheduler Time: {ms} ms", fg=styles.COLOR_DANGER)
        self.update_table(schedule)

    def run_optimized(self):
        schedule, ms = run_optimized()
        self.status_label.config(text=f"Optimized Scheduler Time: {ms} ms", fg=styles.COLOR_PRIMARY)
        self.update_table(schedule)

    def show_performance_graph(self):
        labels = []
        times = []

        try:
            with open("results/execution_times.csv", newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # skip header
                for row in reader:
                    labels.append(row[1])
                    times.append(float(row[2]))
        except FileNotFoundError:
            self.status_label.config(text="No performance data found!", fg=styles.COLOR_WARNING)
            return

        plt.figure(figsize=(6, 4))
        plt.bar(labels, times, color=['red', 'blue'])
        plt.title("Scheduler Performance Comparison")
        plt.ylabel("Execution Time (ms)")
        plt.xlabel("Version")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = AirportSchedulerApp(root)
    root.mainloop()
