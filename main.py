import os
import threading

import customtkinter as ctk
from tkinter import filedialog, messagebox

from pdf_processor import process_pdf

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Text Replacer")
        self.geometry("680x560")
        self.minsize(560, 460)

        self.folder_path = ctk.StringVar()
        self.search_var = ctk.StringVar()
        self.replace_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Ready")
        self.file_count_var = ctk.StringVar(value="No folder selected")
        self.select_all_var = ctk.BooleanVar(value=True)

        self.pdf_files: list[str] = []
        self.check_vars: list[ctk.BooleanVar] = []

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ── Folder row ──────────────────────────────────────────────────────
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 8))
        folder_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(folder_frame, text="Folder:", width=90, anchor="w").grid(
            row=0, column=0, padx=(0, 8)
        )
        ctk.CTkEntry(
            folder_frame, textvariable=self.folder_path, state="disabled"
        ).grid(row=0, column=1, sticky="ew", padx=(0, 8))
        ctk.CTkButton(
            folder_frame, text="Browse…", width=90, command=self._browse_folder
        ).grid(row=0, column=2)

        # ── Search / Replace ────────────────────────────────────────────────
        inputs_frame = ctk.CTkFrame(self, fg_color="transparent")
        inputs_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))
        inputs_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(inputs_frame, text="Search for:", width=90, anchor="w").grid(
            row=0, column=0, padx=(0, 8), pady=(0, 6)
        )
        ctk.CTkEntry(inputs_frame, textvariable=self.search_var).grid(
            row=0, column=1, sticky="ew", pady=(0, 6)
        )

        ctk.CTkLabel(inputs_frame, text="Replace with:", width=90, anchor="w").grid(
            row=1, column=0, padx=(0, 8)
        )
        ctk.CTkEntry(inputs_frame, textvariable=self.replace_var).grid(
            row=1, column=1, sticky="ew"
        )

        # ── File list ───────────────────────────────────────────────────────
        list_outer = ctk.CTkFrame(self)
        list_outer.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 8))
        list_outer.grid_columnconfigure(0, weight=1)
        list_outer.grid_rowconfigure(1, weight=1)

        list_header = ctk.CTkFrame(list_outer, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))
        list_header.grid_columnconfigure(0, weight=1)

        ctk.CTkCheckBox(
            list_header,
            text="Select All",
            variable=self.select_all_var,
            command=self._toggle_select_all,
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(list_header, textvariable=self.file_count_var).grid(
            row=0, column=1, sticky="e"
        )

        self.scroll_frame = ctk.CTkScrollableFrame(list_outer, label_text="")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # ── Action buttons ──────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 8))

        self.process_btn = ctk.CTkButton(
            btn_frame,
            text="Process Selected",
            command=lambda: self._process(False),
        )
        self.process_btn.pack(side="left", padx=(0, 8))

        self.process_all_btn = ctk.CTkButton(
            btn_frame,
            text="Process All",
            command=lambda: self._process(True),
        )
        self.process_all_btn.pack(side="left")

        # ── Progress ─────────────────────────────────────────────────────────
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        progress_frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(progress_frame)
        self.progress.set(0)
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ctk.CTkLabel(progress_frame, textvariable=self.status_var, anchor="w").grid(
            row=1, column=0, sticky="w"
        )

    # ── Logic ────────────────────────────────────────────────────────────────

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=os.getcwd())
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

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.pdf_files:
            ctk.CTkLabel(self.scroll_frame, text="No PDF files found.").grid(
                row=0, column=0, pady=10
            )
            self.file_count_var.set("0 files")
            return

        for i, pdf_file in enumerate(self.pdf_files):
            var = ctk.BooleanVar(value=True)
            self.check_vars.append(var)
            ctk.CTkCheckBox(
                self.scroll_frame, text=pdf_file, variable=var
            ).grid(row=i, column=0, sticky="w", pady=2)

        self.file_count_var.set(f"{len(self.pdf_files)} file(s)")

    def _toggle_select_all(self):
        state = self.select_all_var.get()
        for var in self.check_vars:
            var.set(state)

    def _process(self, process_all: bool):
        if not self.folder_path.get():
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return
        if not self.search_var.get():
            messagebox.showwarning("No Search Text", "Please enter text to search for.")
            return
        if not self.pdf_files:
            messagebox.showwarning("No Files", "No PDF files found in the selected folder.")
            return

        selected = (
            self.pdf_files[:]
            if process_all
            else [f for f, v in zip(self.pdf_files, self.check_vars) if v.get()]
        )

        if not selected:
            messagebox.showwarning("No Selection", "No files selected for processing.")
            return

        self.process_btn.configure(state="disabled")
        self.process_all_btn.configure(state="disabled")
        self.progress.set(0)

        threading.Thread(
            target=self._process_files, args=(selected,), daemon=True
        ).start()

    def _process_files(self, selected: list[str]):
        folder = self.folder_path.get()
        search_text = self.search_var.get()
        replace_text = self.replace_var.get()
        total = len(selected)
        total_replacements = 0
        errors: list[str] = []

        for i, pdf_file in enumerate(selected):
            self.after(
                0, self._update_progress, i / total, f"Processing {pdf_file}…"
            )
            try:
                _, count = process_pdf(
                    os.path.join(folder, pdf_file), search_text, replace_text
                )
                total_replacements += count
            except Exception as e:
                errors.append(f"{pdf_file}: {e}")

        self.after(0, self._finish_processing, total, total_replacements, errors)

    def _update_progress(self, value: float, status: str):
        self.progress.set(value)
        self.status_var.set(status)

    def _finish_processing(self, total: int, total_replacements: int, errors: list[str]):
        self.process_btn.configure(state="normal")
        self.process_all_btn.configure(state="normal")
        self.progress.set(1)

        msg = f"Processed {total} file(s). {total_replacements} replacement(s) made."
        if errors:
            msg += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors)
            self.status_var.set("Done with errors")
        else:
            self.status_var.set("Done!")

        messagebox.showinfo("Complete", msg)


if __name__ == "__main__":
    app = App()
    app.mainloop()
