import flet as ft
from flet.matplotlib_chart import MatplotlibChart
import Backend.Converter as Converter
import os
import matplotlib.pyplot as plt

class FileLoader:

    def __init__(self, page: ft.Page):
        self.page = page
        self.filePicker = ft.FilePicker(on_result=self.on_file_selected)
        self.selectedFilePath = None
        self.fileName = ft.Text("Select File")
        page.overlay.append(self.filePicker)

        self.imageContainer = ft.Container(
            content=ft.Image(
                src="../ExampleImages/Default.jpg",
                width=200,
                height=200,
                fit=ft.ImageFit.CONTAIN
            )
        )

        self.defaultMeta = dict(PatientName='', PatientID='', ImageComments='', StudyDate='')
        self.meta = self.defaultMeta
        self.imageDcm = None
        self.isDcm = False

        self.on_meta_update = None

    def pick_file(self, e=None):
        self.filePicker.pick_files(
            allow_multiple=False,
            allowed_extensions=["jpg", "dcm"]
        )

    def update_file_name_display(self, name: str):
        self.fileName.value = name
        self.fileName.update()

    def dcm_to_plt(self, pixelArray):
        fig, ax = plt.subplots(figsize=(8, 8), tight_layout=True)
        ax.imshow(pixelArray, cmap='gray')

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        chart = MatplotlibChart(fig)

        chartContainer = ft.Container(content=chart, width=200, height=200)

        return chartContainer

    def print_meta(self, meta):
        print(f"Patient Name: {self.meta['PatientName']}\n"
              f"Patient ID: {self.meta['PatientID']}\n"
              f"Image Comments: {self.meta['ImageComments']}\n"
              f"Study Date: {self.meta['StudyDate']}")

    def check_for_missing_meta(self):
        if 'PatientName' not in self.meta.keys():
            self.meta['PatientName'] = ''
        if 'PatientID' not in self.meta.keys():
            self.meta['PatientID'] = ''
        if 'ImageComments' not in self.meta.keys():
            self.meta['ImageComments'] = ''
        if 'StudyDate' not in self.meta.keys():
            self.meta['StudyDate'] = ''

    def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.selectedFilePath = e.files[0].path
            self.update_file_name_display(e.files[0].name)
            fileExt = os.path.splitext(e.files[0].name)[1].lower()
            print(f"File path: {self.selectedFilePath}")

            if fileExt == ".dcm":
                converter = Converter.Converter()
                self.imageDcm, self.meta = converter.readDicomFile(self.selectedFilePath)
                newImage = self.dcm_to_plt(self.imageDcm)
                self.check_for_missing_meta()
                self.print_meta(self.meta)
                self.isDcm = True

            elif fileExt == ".jpg":
                newImage = ft.Image(src=self.selectedFilePath, width=200, height=200, fit=ft.ImageFit.CONTAIN)
                self.meta = self.defaultMeta
                self.isDcm = False

            self.imageContainer.content = newImage
            self.imageContainer.update()

            if self.on_meta_update:
                self.on_meta_update(self.meta)

    def get_selected_file(self):
        return self.selectedFilePath