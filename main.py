import customtkinter as ctk
from merge_pdf import PDFMergerApp
from split_pdf import PDFSplitterReorganizer

# Cấu hình giao diện
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Toolbox")
        self.geometry("1000x700")
        self.minsize(900, 600)

        # Thanh điều hướng
        nav_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=20)

        title = ctk.CTkLabel(
            nav_frame,
            text="🛠️ PDF Toolbox",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(side="left", padx=10)

        self.merge_btn = ctk.CTkButton(
            nav_frame,
            text="Merge PDFs",
            command=self.show_merge,
            width=150,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        self.merge_btn.pack(side="left", padx=10)

        self.split_btn = ctk.CTkButton(
            nav_frame,
            text="Split & Reorder",
            command=self.show_split,
            width=150,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        self.split_btn.pack(side="left", padx=10)

        # Khung chứa nội dung động
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Hiển thị mặc định
        self.current_frame = None
        self.show_merge()

    def clear_content(self):
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_merge(self):
        self.clear_content()
        self.current_frame = PDFMergerApp(self.content_frame)
        self.current_frame.pack(fill="both", expand=True)

    def show_split(self):
        self.clear_content()
        self.current_frame = PDFSplitterReorganizer(self.content_frame)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()