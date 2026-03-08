# merge.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import PyPDF2
import os
import threading

class PDFMergerApp(ctk.CTkFrame):  # Kế thừa từ CTkFrame
    def __init__(self, master):
        super().__init__(master)
        self.pdf_files = []  # List of file paths
        self.setup_ui()

    def setup_ui(self):
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            header,
            text="📄 PDF Merger",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        title.pack(side="left", padx=10)

        subtitle = ctk.CTkLabel(
            header,
            text="Combine multiple PDFs into one document",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(side="left", padx=10)

        # Control buttons
        controls = ctk.CTkFrame(self.main_container, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 20))

        self.add_btn = ctk.CTkButton(
            controls,
            text="➕ Add PDFs",
            command=self.add_files,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.add_btn.pack(side="left", padx=5)

        self.merge_btn = ctk.CTkButton(
            controls,
            text="🔀 Merge PDFs",
            command=self.start_merge,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.merge_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(
            controls,
            text="🗑️ Clear All",
            command=self.clear_all,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2,
            border_color="#e74c3c",
            text_color="#e74c3c",
            hover_color="#2b2b2b"
        )
        self.clear_btn.pack(side="left", padx=5)

        # Files list area
        list_label = ctk.CTkLabel(
            self.main_container,
            text="Files to merge (drag to reorder):",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        list_label.pack(fill="x", pady=(0, 10))

        # Scrollable frame for file list
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_container,
            height=300
        )
        self.scroll_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Status bar
        self.status_frame = ctk.CTkFrame(self.main_container, height=40)
        self.status_frame.pack(fill="x", pady=(10, 0))

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200)
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.set(0)

        # Initialize with empty list
        self.refresh_file_list()

    # Các phương thức giữ nguyên (add_files, refresh_file_list, create_file_row, move_up, move_down, remove_file, clear_all, start_merge, merge_pdfs, reset_buttons, update_status, format_size)
    # (Copy toàn bộ các phương thức từ bản gốc, không thay đổi)
    def add_files(self):
        """Open file dialog to select PDF files"""
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if files:
            for file in files:
                if file.lower().endswith('.pdf') and file not in self.pdf_files:
                    self.pdf_files.append(file)
            self.refresh_file_list()
            self.update_status(f"Added {len(files)} file(s). Total: {len(self.pdf_files)}")

    def refresh_file_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        if not self.pdf_files:
            empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No files selected. Click 'Add PDFs' to begin.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            empty_label.pack(pady=50)
            return
        for idx, file_path in enumerate(self.pdf_files):
            self.create_file_row(idx, file_path)

    def create_file_row(self, idx, file_path):
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", pady=2, padx=5)

        num_label = ctk.CTkLabel(frame, text=str(idx+1), width=30)
        num_label.pack(side="left", padx=5)

        filename = os.path.basename(file_path)
        if len(filename) > 50:
            filename = filename[:47] + "..."
        name_label = ctk.CTkLabel(frame, text=filename, anchor="w", width=400)
        name_label.pack(side="left", padx=5, fill="x", expand=True)

        size = os.path.getsize(file_path)
        size_str = self.format_size(size)
        size_label = ctk.CTkLabel(frame, text=size_str, width=80)
        size_label.pack(side="left", padx=5)

        if idx > 0:
            up_btn = ctk.CTkButton(frame, text="↑", width=30, command=lambda i=idx: self.move_up(i))
            up_btn.pack(side="left", padx=2)

        if idx < len(self.pdf_files) - 1:
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
            command=lambda i=idx: self.remove_file(i)
        )
        remove_btn.pack(side="left", padx=2)

    def move_up(self, idx):
        if idx > 0:
            self.pdf_files[idx], self.pdf_files[idx-1] = self.pdf_files[idx-1], self.pdf_files[idx]
            self.refresh_file_list()

    def move_down(self, idx):
        if idx < len(self.pdf_files) - 1:
            self.pdf_files[idx], self.pdf_files[idx+1] = self.pdf_files[idx+1], self.pdf_files[idx]
            self.refresh_file_list()

    def remove_file(self, idx):
        del self.pdf_files[idx]
        self.refresh_file_list()
        self.update_status(f"Removed file. Total: {len(self.pdf_files)}")

    def clear_all(self):
        if self.pdf_files and messagebox.askyesno("Confirm", "Clear all files from the list?"):
            self.pdf_files.clear()
            self.refresh_file_list()
            self.update_status("Cleared all files")

    def start_merge(self):
        if len(self.pdf_files) < 2:
            messagebox.showwarning("Warning", "Please add at least two PDF files to merge.")
            return
        self.add_btn.configure(state="disabled")
        self.merge_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        thread = threading.Thread(target=self.merge_pdfs)
        thread.daemon = True
        thread.start()

    def merge_pdfs(self):
        try:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Merged PDF As"
            )
            if not output_file:
                self.reset_buttons()
                return
            self.update_status("Merging PDFs...")
            self.progress_bar.set(0)
            merger = PyPDF2.PdfMerger()
            total_files = len(self.pdf_files)
            for i, pdf_path in enumerate(self.pdf_files):
                progress = i / total_files
                self.progress_bar.set(progress)
                self.update_status(f"Processing: {os.path.basename(pdf_path)}")
                merger.append(pdf_path)
            merger.write(output_file)
            merger.close()
            self.progress_bar.set(1)
            self.update_status(f"✅ Success! PDF saved to: {output_file}")
            if messagebox.askyesno("Success", "PDF merged successfully! Open containing folder?"):
                os.startfile(os.path.dirname(output_file))
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")
        finally:
            self.reset_buttons()

    def reset_buttons(self):
        self.add_btn.configure(state="normal")
        self.merge_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")

    def update_status(self, message):
        self.status_label.after(0, lambda: self.status_label.configure(text=message))

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"