import flet as ft

class FileSelector:

    def __init__(self, page: ft.Page):
        self.page = page
        self.filePicker = ft.FilePicker(on_result=self.on_file_selected)
        self.selectedFilePath = None
        self.fileName = ft.Text("Select File")
        page.overlay.append(self.filePicker)
        self.image = ft.Image(
            src="",
            width=300,
            height=300,
            fit=ft.ImageFit.CONTAIN
        )

    def pick_file(self, e=None):
        self.filePicker.pick_files(
            allow_multiple=False,
            allowed_extensions=["jpg"]
        )

    def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.selectedFilePath = e.files[0].path
            self.fileName.value = e.files[0].name
            print(f"File path: {self.selectedFilePath}")
            self.image.src = self.selectedFilePath
            self.page.update()

    def get_selected_file(self):
        return self.selectedFilePath
