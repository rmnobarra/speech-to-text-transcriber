import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Optional, Tuple
import queue

# Import functionality from our existing transcriber
from transcriber import (
    transcribe_audio, 
    get_audio_files_from_directory, 
    save_transcription,
    whisper
)

class TranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Text Transcriber")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Set app icon if available
        try:
            self.root.iconbitmap("icon.ico")  # You can create and add an icon file
        except:
            pass
        
        # Variables
        self.input_files = []
        self.output_dir = tk.StringVar()
        self.model_size = tk.StringVar(value="base")
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        self.file_progress_var = tk.DoubleVar(value=0)
        self.current_file_var = tk.StringVar(value="")
        self.is_processing = False
        self.whisper_model = None
        self.log_queue = queue.Queue()
        
        # Create UI
        self.create_widgets()
        
        # Start log consumer
        self.root.after(100, self.process_log_queue)
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input options
        input_options_frame = ttk.Frame(input_frame)
        input_options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(
            input_options_frame, 
            text="Select Files", 
            value="files", 
            variable=tk.StringVar(value="files"),
            command=self.select_files
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            input_options_frame, 
            text="Select Directory", 
            value="directory", 
            variable=tk.StringVar(value="directory"),
            command=self.select_directory
        ).pack(side=tk.LEFT)
        
        # Files list
        self.files_listbox = tk.Listbox(input_frame, height=5)
        self.files_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Files list scrollbar
        files_scrollbar = ttk.Scrollbar(self.files_listbox, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Output directory
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X)
        
        ttk.Label(output_dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(output_dir_frame, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_dir_frame, text="Browse", command=self.select_output_dir).pack(side=tk.LEFT)
        
        # Model selection
        model_frame = ttk.LabelFrame(main_frame, text="Model Settings", padding="10")
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(model_frame, text="Model Size:").pack(side=tk.LEFT, padx=(0, 5))
        model_combo = ttk.Combobox(
            model_frame, 
            textvariable=self.model_size,
            values=["tiny", "base", "small", "medium", "large"],
            state="readonly",
            width=10
        )
        model_combo.pack(side=tk.LEFT)
        ttk.Label(
            model_frame, 
            text="(larger models are more accurate but slower)"
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Current file
        ttk.Label(progress_frame, text="Current File:").pack(anchor=tk.W)
        ttk.Label(progress_frame, textvariable=self.current_file_var).pack(anchor=tk.W, pady=(0, 5))
        
        # File progress
        ttk.Label(progress_frame, text="File Progress:").pack(anchor=tk.W)
        self.file_progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.file_progress_var,
            length=100,
            mode='determinate'
        )
        self.file_progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Overall progress
        ttk.Label(progress_frame, text="Overall Progress:").pack(anchor=tk.W)
        self.overall_progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            length=100,
            mode='determinate'
        )
        self.overall_progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Status
        ttk.Label(progress_frame, text="Status:").pack(anchor=tk.W)
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Log text
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Log scrollbar
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(
            buttons_frame, 
            text="Start Transcription", 
            command=self.start_transcription
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            buttons_frame, 
            text="Stop", 
            command=self.stop_transcription,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            buttons_frame, 
            text="Clear", 
            command=self.clear_all
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            buttons_frame, 
            text="Exit", 
            command=self.root.destroy
        ).pack(side=tk.RIGHT)
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=(
                ("Audio Files", "*.mp3 *.wav *.ogg"),
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("OGG Files", "*.ogg"),
                ("All Files", "*.*")
            )
        )
        
        if files:
            self.input_files = list(files)
            self.update_files_listbox()
    
    def select_directory(self):
        directory = filedialog.askdirectory(title="Select Directory with Audio Files")
        
        if directory:
            self.input_files = get_audio_files_from_directory(directory)
            if not self.input_files:
                messagebox.showinfo("No Files Found", "No audio files found in the selected directory.")
            else:
                self.update_files_listbox()
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        
        if directory:
            self.output_dir.set(directory)
    
    def update_files_listbox(self):
        self.files_listbox.delete(0, tk.END)
        
        for file in self.input_files:
            self.files_listbox.insert(tk.END, os.path.basename(file))
        
        self.log(f"Selected {len(self.input_files)} files for transcription")
    
    def log(self, message):
        self.log_queue.put(message)
    
    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_queue.task_done()
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_log_queue)
    
    def clear_all(self):
        self.input_files = []
        self.files_listbox.delete(0, tk.END)
        self.output_dir.set("")
        self.log_text.delete(1.0, tk.END)
        self.current_file_var.set("")
        self.progress_var.set(0)
        self.file_progress_var.set(0)
        self.status_var.set("Ready")
    
    def start_transcription(self):
        if not self.input_files:
            messagebox.showerror("Error", "No input files selected")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("Error", "No output directory selected")
            return
        
        if not os.path.exists(self.output_dir.get()):
            try:
                os.makedirs(self.output_dir.get())
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {e}")
                return
        
        # Disable start button and enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_processing = True
        
        # Start transcription in a separate thread
        threading.Thread(target=self.transcription_thread, daemon=True).start()
    
    def stop_transcription(self):
        self.is_processing = False
        self.status_var.set("Stopping...")
        self.log("Stopping transcription...")
    
    def transcription_thread(self):
        try:
            # Reset progress
            self.progress_var.set(0)
            self.file_progress_var.set(0)
            self.status_var.set("Loading model...")
            
            # Load model
            self.log(f"Loading Whisper {self.model_size.get()} model...")
            self.whisper_model = whisper.load_model(self.model_size.get())
            
            # Process files
            total_files = len(self.input_files)
            self.log(f"Starting transcription of {total_files} files...")
            
            for i, input_file in enumerate(self.input_files):
                if not self.is_processing:
                    break
                
                file_name = os.path.basename(input_file)
                self.current_file_var.set(file_name)
                self.status_var.set(f"Transcribing file {i+1} of {total_files}")
                self.progress_var.set((i / total_files) * 100)
                
                try:
                    # Custom progress callback for file progress
                    def update_file_progress(progress):
                        self.file_progress_var.set(progress)
                        self.root.update_idletasks()
                    
                    # Log start of transcription
                    self.log(f"Transcribing: {file_name}")
                    
                    # Transcribe audio
                    # We'll modify our transcribe function to accept a progress callback
                    transcription = self.transcribe_with_progress(input_file, update_file_progress)
                    
                    # Save transcription
                    output_file = os.path.join(
                        self.output_dir.get(), 
                        os.path.splitext(file_name)[0] + ".txt"
                    )
                    save_transcription(transcription, output_file)
                    
                    self.log(f"✅ Completed: {file_name} -> {output_file}")
                    
                except Exception as e:
                    self.log(f"❌ Error processing {file_name}: {str(e)}")
            
            # Update final progress
            if self.is_processing:
                self.progress_var.set(100)
                self.file_progress_var.set(100)
                self.status_var.set("Transcription completed")
                self.log("All transcriptions completed successfully!")
            else:
                self.status_var.set("Transcription stopped")
        
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.status_var.set("Error occurred")
        
        finally:
            # Re-enable start button and disable stop button
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_processing = False
    
    def transcribe_with_progress(self, input_file, progress_callback):
        """Modified version of transcribe_audio that updates GUI progress"""
        # This is a simplified version that calls our existing function
        # but updates the progress bar
        
        # Simulate progress updates since the original function doesn't support callbacks
        def progress_updater():
            for i in range(101):
                if not self.is_processing:
                    break
                progress_callback(i)
                time.sleep(0.05)  # Adjust based on expected transcription time
        
        # Start progress updater in a separate thread
        progress_thread = threading.Thread(target=progress_updater, daemon=True)
        progress_thread.start()
        
        # Perform actual transcription
        result = transcribe_audio(input_file, self.model_size.get(), self.whisper_model)
        
        # Ensure progress reaches 100%
        progress_callback(100)
        
        return result

def main():
    root = tk.Tk()
    app = TranscriberApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

