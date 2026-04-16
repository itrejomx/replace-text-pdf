import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from pdf_processor import process_pdf


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Text Replacer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        self.folder_path = tk.StringVar()
        self.pdf_files = []
        self.check_vars = []
        self.processing = False

        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Folder selection
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(folder_frame, text="Folder:").pack(side=tk.LEFT)
        ttk.Entry(folder_frame, textvariable=self.folder_path, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5)
        )
        ttk.Button(folder_frame, text="Browse...", command=self._browse_folder).pack(
            side=tk.RIGHT
        )

        # Search/Replace inputs
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Search for:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.search_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.search_var).grid(
            row=0, column=1, sticky=tk.EW, pady=2, padx=(5, 0)
        )

        ttk.Label(input_frame, text="Replace with:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.replace_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.replace_var).grid(
            row=1, column=1, sticky=tk.EW, pady=2, padx=(5, 0)
        )
        input_frame.columnconfigure(1, weight=1)

        # File list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        list_header = ttk.Frame(list_frame)
        list_header.pack(fill=tk.X)

        self.select_all_var = tk.BooleanVar()
        ttk.Checkbutton(
            list_header,
            text="Select All",
            variable=self.select_all_var,
            command=self._toggle_select_all,
        ).pack(side=tk.LEFT)

        self.file_count_var = tk.StringVar(value="No folder selected")
        ttk.Label(list_header, textvariable=self.file_count_var).pack(side=tk.RIGHT)

        list_canvas = tk.Canvas(list_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=list_canvas.yview
        )
        self.file_list_frame = ttk.Frame(list_canvas)

        self.file_list_frame.bind(
            "<Configure>",
            lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")),
        )
        list_canvas.create_window((0, 0), window=self.file_list_frame, anchor="nw")
        list_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.process_btn = ttk.Button(
            btn_frame, text="Process Selected", command=lambda: self._process(False)
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.process_all_btn = ttk.Button(
            btn_frame, text="Process All", command=lambda: self._process(True)
        )
        self.process_all_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Progress
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X)

        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(side=tk.LEFT)

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self._scan_folder()

    def _scan_folder(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            return

        self.pdf_files = sorted(
            f for f in os.listdir(folder) if f.lower().endswith(".pdf")
        )
        self.check_vars = []

        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        if not self.pdf_files:
            ttk.Label(self.file_list_frame, text="No PDF files found.").pack(pady=10)
            self.file_count_var.set("0 files")
            return

        for pdf_file in self.pdf_files:
            var = tk.BooleanVar(value=True)
            self.check_vars.append(var)
            ttk.Checkbutton(self.file_list_frame, text=pdf_file, variable=var).pack(
                anchor=tk.W, fill=tk.X
            )

        self.file_count_var.set(f"{len(self.pdf_files)} file(s)")

    def _toggle_select_all(self):
        state = self.select_all_var.get()
        for var in self.check_vars:
            var.set(state)

    def _process(self, process_all):
        if not self.folder_path.get():
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return

        if not self.search_var.get():
            messagebox.showwarning("No Search Text", "Please enter text to search for.")
            return

        if not self.pdf_files:
            messagebox.showwarning(
                "No Files", "No PDF files found in the selected folder."
            )
            return

        if process_all:
            selected = self.pdf_files[:]
        else:
            selected = [f for f, v in zip(self.pdf_files, self.check_vars) if v.get()]

        if not selected:
            messagebox.showwarning("No Selection", "No files selected for processing.")
            return

        self.processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.process_all_btn.config(state=tk.DISABLED)

        thread = threading.Thread(
            target=self._process_files, args=(selected,), daemon=True
        )
        thread.start()

    def _process_files(self, selected):
        folder = self.folder_path.get()
        search_text = self.search_var.get()
        replace_text = self.replace_var.get()
        total = len(selected)
        total_replacements = 0
        errors = []

        for i, pdf_file in enumerate(selected):
            self.root.after(
                0, self._update_progress, i / total * 100, f"Processing {pdf_file}..."
            )

            try:
                input_path = os.path.join(folder, pdf_file)
                output_path, count = process_pdf(input_path, search_text, replace_text)
                total_replacements += count
            except Exception as e:
                errors.append(f"{pdf_file}: {str(e)}")

        self.root.after(
            0,
            self._finish_processing,
            total,
            total_replacements,
            errors,
        )

    def _update_progress(self, percent, status):
        self.progress["value"] = percent
        self.status_var.set(status)

    def _finish_processing(self, total, total_replacements, errors):
        self.processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.process_all_btn.config(state=tk.NORMAL)
        self.progress["value"] = 100

        msg = f"Processed {total} file(s). {total_replacements} replacement(s) made."
        if errors:
            msg += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors)
            self.status_var.set(f"Done with errors")
        else:
            self.status_var.set("Done!")

        messagebox.showinfo("Complete", msg)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
