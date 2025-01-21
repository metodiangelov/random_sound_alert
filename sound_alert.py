import time
import random
import pygame
import tkinter as tk
from tkinter import ttk
from threading import Thread, Event

# Initialize pygame mixer
pygame.mixer.init()

# List of sound file paths (use the full path to your sound files)
sound_files = [
    r"C:\path_to_your_sound_file\sound_alert.wav"
]

class SoundAlertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Sound Alert")
        
        # Set the font size for the whole app
        self.font = ('Arial', 14)
        
        # Create a frame for the entire content (to be scrollable)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar for the canvas
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create a frame inside the canvas where we will place the widgets
        self.content_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Add a function to update the scrollable area when the content changes
        self.content_frame.bind("<Configure>", self.on_frame_configure)

        # Create buttons for starting, pausing, and stopping the alerts
        self.start_button = tk.Button(self.content_frame, text="Start Alerts", command=self.start_alerts, font=self.font)
        self.start_button.grid(row=0, column=0, pady=10)

        self.pause_button = tk.Button(self.content_frame, text="Pause Alerts", command=self.pause_alerts, font=self.font)
        self.pause_button.grid(row=1, column=0, pady=10)

        # Label to display the last button pressed
        self.status_label = tk.Label(self.content_frame, text="Last Button Pressed: None", font=self.font)
        self.status_label.grid(row=2, column=0, pady=20)

        # Text widget to display output (like print statements)
        self.output_text = tk.Text(self.content_frame, height=10, width=50, font=self.font)
        self.output_text.grid(row=3, column=0, pady=10)
        self.output_text.config(state=tk.DISABLED)  # Make the text box read-only
        
        self.alert_thread = None
        self.running = False
        self.paused = False
        self.pause_event = Event()

        # Task checklist frame
        self.task_frame = tk.Frame(self.content_frame)
        self.task_frame.grid(row=4, column=0, pady=20, padx=10, sticky="w")

        # Group 1: SHIFT ON – Attendance – Check In – Check Out
        self.shift_group_label = tk.Label(self.task_frame, text="SHIFT ON – Attendance – Check In – Check Out", font=self.font)
        self.shift_group_label.grid(row=0, column=0, sticky="w")
        self.shift_checkboxes = []
        self.shift_checkboxes.append(tk.Checkbutton(self.task_frame, text="Check In", variable=tk.BooleanVar(), font=self.font))
        self.shift_checkboxes.append(tk.Checkbutton(self.task_frame, text="Check Out", variable=tk.BooleanVar(), font=self.font))
        self.shift_checkboxes[0].grid(row=1, column=0, sticky="w")
        self.shift_checkboxes[1].grid(row=2, column=0, sticky="w")

        # Group 2: Promotions
        self.promotions_group_label = tk.Label(self.task_frame, text="Promotions", font=self.font)
        self.promotions_group_label.grid(row=3, column=0, sticky="w")
        self.promotions_checkboxes = []
        self.promotions_checkboxes.append(tk.Checkbutton(self.task_frame, text="Post 1 Promotion", variable=tk.BooleanVar(), font=self.font))
        self.promotions_checkboxes.append(tk.Checkbutton(self.task_frame, text="Post 2 Promotions", variable=tk.BooleanVar(), font=self.font))
        self.promotions_checkboxes.append(tk.Checkbutton(self.task_frame, text="Post 3 Promotions", variable=tk.BooleanVar(), font=self.font))
        for i, checkbox in enumerate(self.promotions_checkboxes, 4):
            checkbox.grid(row=i, column=0, sticky="w")

        # Group 3: General Welcome Messages
        self.general_welcome_group_label = tk.Label(self.task_frame, text="General Welcome Messages", font=self.font)
        self.general_welcome_group_label.grid(row=7, column=0, sticky="w")
        self.general_welcome_checkboxes = []
        for i in range(4):
            self.general_welcome_checkboxes.append(tk.Checkbutton(self.task_frame, text=f"Message {i+1}", variable=tk.BooleanVar(), font=self.font))
            self.general_welcome_checkboxes[i].grid(row=8 + i, column=0, sticky="w")

        # Group 4: Open-ended Questions
        self.open_ended_group_label = tk.Label(self.task_frame, text="Open-ended Questions", font=self.font)
        self.open_ended_group_label.grid(row=12, column=0, sticky="w")
        self.open_ended_checkboxes = []
        for i in range(6):
            self.open_ended_checkboxes.append(tk.Checkbutton(self.task_frame, text=f"Question {i+1}", variable=tk.BooleanVar(), font=self.font))
            self.open_ended_checkboxes[i].grid(row=13 + i, column=0, sticky="w")

        # Group 5: Chat Games
        self.chat_games_group_label = tk.Label(self.task_frame, text="CHAT GAMES", font=self.font)
        self.chat_games_group_label.grid(row=19, column=0, sticky="w")
        self.chat_games_checkboxes = []
        for i in range(3):
            self.chat_games_checkboxes.append(tk.Checkbutton(self.task_frame, text=f"Game {i+1}", variable=tk.BooleanVar(), font=self.font))
            self.chat_games_checkboxes[i].grid(row=20 + i, column=0, sticky="w")

    def on_frame_configure(self, event):
        """Update the scrollable region of the canvas when the frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def play_random_sound(self):
        """Plays a random sound from the sound_files list."""
        sound = random.choice(sound_files)
        pygame.mixer.Sound(sound).play()
        time.sleep(2)  # Adjust based on sound length

    def random_alert(self):
        """Plays random sound alerts at random intervals between 60 and 115 seconds."""
        while self.running:
            if self.paused:
                self.pause_event.wait()  # Wait for the pause to be lifted
            interval = random.randint(60, 115)  # Random interval in seconds
            self.update_output(f"Next alert in {interval} seconds.")
            print(f"Next alert in {interval} seconds.")  # Print to terminal
            time.sleep(interval)  # Wait for the random interval
            self.play_random_sound()  # Play a random sound

    def update_status(self, button_name):
        """Updates the status label with the last button pressed."""
        self.status_label.config(text=f"Last Button Pressed: {button_name}")

    def update_output(self, message):
        """Updates the output text widget with a new message."""
        self.output_text.config(state=tk.NORMAL)  # Enable editing
        self.output_text.insert(tk.END, message + "\n")  # Append message
        self.output_text.config(state=tk.DISABLED)  # Disable editing to make it read-only
        self.output_text.yview(tk.END)  # Auto-scroll to the latest message

    def start_alerts(self):
        """Starts the random alert sound in a separate thread."""
        if not self.running:
            self.running = True
            self.alert_thread = Thread(target=self.random_alert)
            self.alert_thread.start()
            self.update_output("Alerts started.")
            print("Alerts started.")  # Print to terminal
            self.update_status("Start Alerts")
        elif self.paused:
            self.paused = False
            self.pause_event.set()  # Resume the alerts when resumed
            self.update_output("Alerts resumed.")
            print("Alerts resumed.")  # Print to terminal
            self.update_status("Resumed Alerts")

    def pause_alerts(self):
        """Pauses the random alert sound."""
        if self.running and not self.paused:
            self.paused = True
            self.pause_event.clear()  # Block the thread from continuing
            self.update_output("Alerts paused.")
            print("Alerts paused.")  # Print to terminal
            self.update_status("Pause Alerts")

    def get_checked_tasks(self):
        """Returns a list of checked tasks."""
        checked_tasks = []
        for group in [self.shift_checkboxes, self.promotions_checkboxes, self.general_welcome_checkboxes,
                      self.open_ended_checkboxes, self.chat_games_checkboxes]:
            for checkbox in group:
                if checkbox.var.get():
                    checked_tasks.append(checkbox.cget("text"))
        return checked_tasks


if __name__ == "__main__":
    root = tk.Tk()
    app = SoundAlertApp(root)
    root.geometry("700x600")  # Set initial size of the window
    root.mainloop()
