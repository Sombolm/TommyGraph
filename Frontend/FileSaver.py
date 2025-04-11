import flet as ft
from Backend.Saver import Saver

class FileSaver:

    def __init__(self, page: ft.Page):
        self.page = page
        self.saver = Saver()
        self.filePicker = ft.FilePicker(on_result=self.on_file_saved)
        self.selectedFilePath = None
        self.page.overlay.append(self.filePicker)

        self.imageRaw = None
        self.meta = {}

    def set_data(self, imageRaw, meta: dict):
        self.imageRaw = imageRaw
        self.meta = meta

    def pick_file(self, e=None):
        self.filePicker.save_file(
            file_name="output.dcm",
            allowed_extensions=["dcm"]
        )

    def on_file_saved(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.selectedFilePath = e.path
            print(f"Zapisz plik jako: {self.selectedFilePath}")
            self.saver.saveAsDicomFile(self.selectedFilePath, self.imageRaw, self.meta)
