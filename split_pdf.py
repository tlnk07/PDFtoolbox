# split.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pypdf
import os
import threading

class PDFSplitterReorganizer(ctk.CTkFrame):  # Kế thừa từ CTkFrame
    def __init__(self, master):
        super().__init__(master)
        self.pdf_path = None
        self.total_pages = 0
        self.parts = []  # List of (start_page, end_page) tuples (1-indexed)
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            header,
            text="✂️ PDF Splitter & Reorganizer",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(side="left", padx=10)

        # Load PDF section
        load_frame = ctk.CTkFrame(main)
        load_frame.pack(fill="x", pady=(0, 20))

        self.load_btn = ctk.CTkButton(
            load_frame,
            text="📂 Load PDF",
            command=self.load_pdf,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.load_btn.pack(side="left", padx=10)

        self.pdf_info_label = ctk.CTkLabel(
            load_frame,
            text="No PDF loaded",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.pdf_info_label.pack(side="left", padx=10)

        # Split definition frame
        split_frame = ctk.CTkFrame(main)
        split_frame.pack(fill="x", pady=(0, 20))

        range_label = ctk.CTkLabel(
            split_frame,
            text="Define page ranges to split (1-indexed):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        range_label.pack(anchor="w", padx=10, pady=(10, 5))

        entry_frame = ctk.CTkFrame(split_frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=10, pady=5)

        self.start_entry = ctk.CTkEntry(entry_frame, placeholder_text="Start page", width=100)
        self.start_entry.pack(side="left", padx=5)

        self.end_entry = ctk.CTkEntry(entry_frame, placeholder_text="End page", width=100)
        self.end_entry.pack(side="left", padx=5)

        self.add_part_btn = ctk.CTkButton(
            entry_frame,
            text="➕ Add Part",
            command=self.add_part,
            width=120,
            state="disabled"
        )
        self.add_part_btn.pack(side="left", padx=5)

        self.clear_parts_btn = ctk.CTkButton(
            entry_frame,
            text="🗑️ Clear All Parts",
            command=self.clear_parts,
            width=120,
            fg_color="transparent",
            border_width=2,
            border_color="#e74c3c",
            text_color="#e74c3c"
        )
        self.clear_parts_btn.pack(side="left", padx=5)

        # Parts list
        parts_label = ctk.CTkLabel(
            main,
            text="Parts (reorder using up/down buttons):",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        parts_label.pack(fill="x", pady=(10, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(main, height=200)
        self.scroll_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Process button and status
        process_frame = ctk.CTkFrame(main, fg_color="transparent")
        process_frame.pack(fill="x", pady=(10, 0))

        self.process_btn = ctk.CTkButton(
            process_frame,
            text="⚙️ Merge Reordered PDF",
            command=self.start_processing,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            state="disabled",
            text_color="white",
            text_color_disabled="white"
        )
        self.process_btn.pack(side="left", padx=10)

        self.progress_bar = ctk.CTkProgressBar(process_frame, width=300)
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            process_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)

        self.refresh_parts_list()

    # Các phương thức giữ nguyên (load_pdf, add_part, refresh_parts_list, create_part_row, move_up, move_down, remove_part, clear_parts, start_processing, merge_reordered_pdf, reset_buttons, update_status)
    def load_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                self.total_pages = len(reader.pages)
            self.pdf_path = file_path
            filename = os.path.basename(file_path)
            self.pdf_info_label.configure(
                text=f"Loaded: {filename} ({self.total_pages} pages)",
                text_color="white"
            )
            self.add_part_btn.configure(state="normal")
            self.process_btn.configure(state="normal")
            self.clear_parts()
            self.update_status(f"Loaded PDF with {self.total_pages} pages")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF:\n{str(e)}")

    def add_part(self):
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Please load a PDF first.")
            return
        try:
            start = int(self.start_entry.get())
            end = int(self.end_entry.get())
        except ValueError:
            messagebox.showwarning("Warning", "Please enter valid integers for start and end pages.")
            return
        if start < 1 or end < 1:
            messagebox.showwarning("Warning", "Page numbers must be positive.")
            return
        if start > end:
            messagebox.showwarning("Warning", "Start page must be <= end page.")
            return
        if end > self.total_pages:
            messagebox.showwarning("Warning", f"End page exceeds total pages ({self.total_pages}).")
            return
        self.parts.append((start, end))
        self.start_entry.delete(0, 'end')
        self.end_entry.delete(0, 'end')
        self.refresh_parts_list()
        self.update_status(f"Added part: pages {start}-{end}")

    def refresh_parts_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        if not self.parts:
            empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No parts defined. Add some page ranges.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        for idx, (start, end) in enumerate(self.parts):
            self.create_part_row(idx, start, end)

    def create_part_row(self, idx, start, end):
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", pady=2, padx=5)

        num_label = ctk.CTkLabel(frame, text=str(idx+1), width=40)
        num_label.pack(side="left", padx=5)

        range_text = f"Pages {start} - {end}"
        range_label = ctk.CTkLabel(frame, text=range_text, width=200, anchor="w")
        range_label.pack(side="left", padx=5, fill="x", expand=True)

        if idx > 0:
            up_btn = ctk.CTkButton(frame, text="↑", width=30, command=lambda i=idx: self.move_up(i))
            up_btn.pack(side="left", padx=2)

        if idx < len(self.parts) - 1:
            down_btn = ctk.CTkButton(frame, text="↓", width=30, command=lambda i=idx: self.move_down(i))
            down_btn.pack(side="left", padx=2)

        remove_btn = ctk.CTkButton(
            frame,
            text="✖",
            width=30,
            fg_color="transparent",
            border_width=1,
            border_color="#e74c3c",
            text_color="#e74c3c",
            hover_color="#2b2b2b",
            command=lambda i=idx: self.remove_part(i)
        )
        remove_btn.pack(side="left", padx=2)

    def move_up(self, idx):
        if idx > 0:
            self.parts[idx], self.parts[idx-1] = self.parts[idx-1], self.parts[idx]
            self.refresh_parts_list()

    def move_down(self, idx):
        if idx < len(self.parts) - 1:
            self.parts[idx], self.parts[idx+1] = self.parts[idx+1], self.parts[idx]
            self.refresh_parts_list()

    def remove_part(self, idx):
        del self.parts[idx]
        self.refresh_parts_list()
        self.update_status("Removed part")

    def clear_parts(self):
        self.parts.clear()
        self.refresh_parts_list()
        self.update_status("Cleared all parts")

    def start_processing(self):
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Please load a PDF first.")
            return
        if not self.parts:
            messagebox.showwarning("Warning", "Please add at least one part.")
            return
        self.load_btn.configure(state="disabled")
        self.add_part_btn.configure(state="disabled")
        self.clear_parts_btn.configure(state="disabled")
        self.process_btn.configure(state="disabled")
        thread = threading.Thread(target=self.merge_reordered_pdf)
        thread.daemon = True
        thread.start()

    def merge_reordered_pdf(self):
        try:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Reordered PDF As"
            )
            if not output_file:
                self.update_status("Cancelled")
                self.reset_buttons()
                return
            self.update_status("Merging parts into single PDF...")
            self.progress_bar.set(0)
            writer = pypdf.PdfWriter()
            total_parts = len(self.parts)
            for i, (start, end) in enumerate(self.parts):
                progress = i / total_parts
                self.progress_bar.set(progress)
                self.update_status(f"Adding part {i+1}: pages {start}-{end}")
                with open(self.pdf_path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    for page_num in range(start-1, end):
                        writer.add_page(reader.pages[page_num])
            with open(output_file, 'wb') as f:
                writer.write(f)
            self.progress_bar.set(1)
            self.update_status(f"✅ Saved reordered PDF to: {output_file}")
            if messagebox.askyesno("Success", "PDF created successfully! Open containing folder?"):
                os.startfile(os.path.dirname(output_file))
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Processing failed:\n{str(e)}")
        finally:
            self.reset_buttons()

    def reset_buttons(self):
        self.load_btn.configure(state="normal")
        self.add_part_btn.configure(state="normal")
        self.clear_parts_btn.configure(state="normal")
        self.process_btn.configure(state="normal")

    def update_status(self, message):
        self.status_label.after(0, lambda: self.status_label.configure(text=message))