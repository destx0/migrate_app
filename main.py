import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
from process_option1 import process_option1
from process_option2 import process_option2
from process_option3 import process_option3
from process_option4 import process_option4

class JSONProcessorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("JSON/JSONL/Image Processor")
        self.master.geometry("500x400")

        self.filenames = []
        self.process_option = tk.StringVar()
        self.process_option.set("option1")  # Default option

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Select Files:").pack(pady=10)
        self.file_listbox = tk.Listbox(self.master, width=60, height=5)
        self.file_listbox.pack()
        tk.Button(self.master, text="Browse", command=self.browse_files).pack(pady=5)

        tk.Label(self.master, text="Select Processing Option:").pack(pady=10)
        options = [
            ("Option 1 (JSON)", "option1"),
            ("Option 2 (JSON)", "option2"),
            ("Option 3 (JSONL)", "option3"),
            ("Option 4 (Image Processing & Firebase)", "option4")
        ]
        for text, value in options:
            tk.Radiobutton(self.master, text=text, variable=self.process_option, value=value).pack()

        tk.Button(self.master, text="Process", command=self.process_files).pack(pady=20)

        self.progress = ttk.Progressbar(self.master, length=300, mode='determinate')
        self.progress.pack(pady=10)

    def browse_files(self):
        filenames = filedialog.askopenfilenames(filetypes=[("All files", "*.*"), ("JSON files", "*.json"), ("JSONL files", "*.jsonl"), ("Image files", "*.png;*.jpg;*.jpeg")])
        self.filenames.extend(filenames)
        for filename in filenames:
            self.file_listbox.insert(tk.END, filename)

    def process_files(self):
        if not self.filenames:
            messagebox.showerror("Error", "Please select at least one file.")
            return

        try:
            total_files = len(self.filenames)
            self.progress['maximum'] = total_files

            for index, filename in enumerate(self.filenames):
                self.update_status(f"Processing file: {os.path.basename(filename)}")
                
                if self.process_option.get() == "option4":
                    result = process_option4(filename)
                    if result:
                        self.update_status(f"File processed and updated: {filename}")
                    else:
                        self.update_status(f"Error processing file {filename}")
                else:
                    with open(filename, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    
                    if self.process_option.get() == "option1":
                        result = process_option1(data)
                    elif self.process_option.get() == "option2":
                        result = process_option2(data)
                    elif self.process_option.get() == "option3":
                        result = process_option3(data)
                    
                    output_filename = self.generate_new_filename(filename)
                    with open(output_filename, 'w', encoding='utf-8') as file:
                        json.dump(result, file, ensure_ascii=False, indent=2)

                self.progress['value'] = index + 1
                self.master.update_idletasks()

            messagebox.showinfo("Success", f"Processing complete. {total_files} files processed.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def generate_new_filename(self, original_filename):
        directory = os.path.dirname(original_filename)
        filename = os.path.basename(original_filename)
        name, ext = os.path.splitext(filename)
        new_name = f"{name}_processed_{self.process_option.get()}{ext}"
        return os.path.join(directory, new_name)

    def update_status(self, message):
        print(message)  # Replace with a more sophisticated status update mechanism if needed

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONProcessorApp(root)
    root.mainloop()