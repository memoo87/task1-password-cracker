import tkinter as tk
import threading
import queue
import itertools
import string
CORRECT_PASSWORD = 'Apple'
DICTIONARY_FILE = 'D:/section/dictionary.txt'
class PasswordCrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Cracker")
        self.username_label = tk.Label(root, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()
        self.start_button = tk.Button(root, text="Start Attack", command=self.start_attack)
        self.start_button.pack()
        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack()
        self.log_text = tk.Text(root, height=10, width=40)
        self.log_text.pack()
        self.attack_queue = queue.Queue()
        self.root.after(100, self.check_queue)
    def start_attack(self):
        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.run_attacks).start()
    def run_attacks(self):
        username = self.username_entry.get().strip()
        self.attack_queue.put({'type': 'status', 'text': f"Starting attack for user: {username}"})
        if self.dictionary_attack():
            return
        self.brute_force_attack()
    def dictionary_attack(self):
        try:
            with open(DICTIONARY_FILE, 'r') as f:
                self.attack_queue.put({'type': 'status', 'text': "Starting dictionary attack..."})
                for line in f:
                    password = line.strip()
                    if password == CORRECT_PASSWORD:
                        self.attack_queue.put({'type': 'success', 'text': f"Success! Password found: {password}"})
                        return True
                self.attack_queue.put({'type': 'status', 'text': "Dictionary attack failed."})
        except FileNotFoundError:
            self.attack_queue.put({'type': 'status', 'text': "Dictionary file not found. Skipping dictionary attack."})
        return False
    def brute_force_attack(self):
        characters = string.ascii_letters
        total_attempts = len(characters) ** 5
        current_attempt = 0
        self.attack_queue.put({'type': 'status', 'text': "Starting brute force attack..."})
        for password_tuple in itertools.product(characters, repeat=5):
            password = ''.join(password_tuple)
            current_attempt += 1
            if current_attempt % 1000 == 0:
                progress = (current_attempt / total_attempts) * 100
                self.attack_queue.put({'type': 'status', 'text': f"Brute force progress: {progress:.2f}% ({current_attempt}/{total_attempts})"})
            if password == CORRECT_PASSWORD:
                self.attack_queue.put({'type': 'success', 'text': f"Success! Password found: {password}"})
                return
        self.attack_queue.put({'type': 'status', 'text': "Brute force attack failed."})
    def check_queue(self):
        try:
            while True:
                message = self.attack_queue.get_nowait()
                if message['type'] == 'status':
                    self.status_label.config(text=message['text'])
                    self.log_text.insert(tk.END, message['text'] + '\n')
                    self.log_text.see(tk.END)
                elif message['type'] == 'success':
                    self.status_label.config(text=message['text'], fg="green")
                    self.log_text.insert(tk.END, message['text'] + '\n')
                    self.log_text.see(tk.END)
                    self.start_button.config(state=tk.NORMAL)
                self.attack_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordCrackerGUI(root)
    root.mainloop()