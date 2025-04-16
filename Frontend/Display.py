import flet as ft
from Frontend.FileLoader import FileLoader
from Frontend.FileSaver import FileSaver
from Backend.Tomograph import Tomograph
from flet.matplotlib_chart import MatplotlibChart
import matplotlib.pyplot as plt

# global
plotData = [{}, {}]
sinogram = ft.Container(width=400, height=400)
reconstructedImages = ft.Container(width=400, height=400)
currentIteration = 1
maxIteration = 1
iterSliderContainer = ft.Container()

def get_slider(isVisible):
    global maxIteration

    def slider_changed(e):
        global currentIteration, sinogram, reconstructedImages, plotData
        currentIteration = int(e.control.value)

        sinogram.content = draw_plt_image(plotData[0], currentIteration)
        reconstructedImages.content = draw_plt_image(plotData[1], currentIteration)

        sinogram.update()
        reconstructedImages.update()

    slider = ft.Slider(
        min=1, max=maxIteration, divisions=maxIteration - 1, label="{value}",
        on_change_end=slider_changed, value=maxIteration, width=600
    )

    return ft.Column(
        controls=[ft.Text("View iteration:", size=15, bgcolor=ft.Colors.GREEN_200), slider],
        visible=isVisible,
        expand=True
    )

def draw_plt_image(imgSource, iteration):
    fig, ax = plt.subplots(figsize=(8, 8), tight_layout=True)
    ax.imshow(imgSource[iteration], cmap='gray')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    chart = MatplotlibChart(fig)
    return chart

def get_details_field(fileSaver: FileSaver, fileSelector: FileLoader):
    def save_as_dicom(e):
        currentImage = plotData[1][currentIteration]
        dicomParams = {
            'PatientName': nameField.value,
            'PatientID': patientIdField.value,
            'ImageComments': commentField.value,
            'StudyDate': dateField.value,
        }
        fileSaver.set_data(currentImage, dicomParams)
        fileSaver.pick_file()

    def update_fields(meta):
        nameField.value = meta['PatientName']
        patientIdField.value = meta['PatientID']
        commentField.value = meta['ImageComments']
        dateField.value = meta['StudyDate']

        nameField.update()
        patientIdField.update()
        commentField.update()
        dateField.update()

    fileSelector.on_meta_update = update_fields

    textFieldColor = "white"

    nameValue = fileSelector.meta['PatientName']
    patientIdValue = fileSelector.meta['PatientID']
    commentValue = fileSelector.meta['ImageComments']
    dateValue = fileSelector.meta['StudyDate']

    nameField = ft.TextField(label="Patient Name", value=nameValue, width=280,
                             color=textFieldColor, border_color=textFieldColor,
                             label_style=ft.TextStyle(color=textFieldColor), cursor_color=textFieldColor)
    patientIdField = ft.TextField(label="Patient ID", value=patientIdValue, width=280,
                                  color=textFieldColor, border_color=textFieldColor,
                                  label_style=ft.TextStyle(color=textFieldColor), cursor_color=textFieldColor,
                                  input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$",replacement_string="" ))
    commentField = ft.TextField(label="Image Comments", value=commentValue, width=280,
                                color=textFieldColor, border_color=textFieldColor,
                                label_style=ft.TextStyle(color=textFieldColor), cursor_color=textFieldColor)
    dateField = ft.TextField(label="Study Date", value=dateValue, width=280,
                             color=textFieldColor, border_color=textFieldColor,
                             label_style=ft.TextStyle(color=textFieldColor), cursor_color=textFieldColor,
                             input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,8}$", replacement_string="" )
                             )

    saveButton = ft.ElevatedButton("Save as DICOM", on_click=save_as_dicom, disabled=True)

    patientDetails = ft.Column(
        controls=[
            nameField,
            patientIdField,
            commentField,
            dateField
        ],
        spacing=10
    )

    expansionDetailsTile = ft.ExpansionTile(
        title=ft.Text(
            "Patient details",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE,
            text_align=ft.TextAlign.CENTER
        ),
        affinity=ft.TileAffinity.PLATFORM,
        maintain_state=True,
        text_color=ft.Colors.BLACK,
        bgcolor=ft.Colors.GREEN_300,
        collapsed_bgcolor=ft.Colors.GREEN_300,
        controls=[
            ft.Divider(),
            patientDetails,
            ft.Container(
                saveButton,
                alignment=ft.alignment.bottom_center,
                padding=10
            )
        ],
        width=300,
        visible=True
    )

    return expansionDetailsTile, saveButton

def get_appbar(page: ft.Page, fileSelector: FileLoader, saveButton: ft.ElevatedButton):
    def run_tomograph(e, alpha, numEmittersDetectors, angSpread, isFiltered, saveButton):
        global plotData, sinogram, reconstructedImages, maxIteration, currentIteration, iterSliderContainer

        tomograph = Tomograph()

        def validate_parameters(param):
            if param.isdigit():
                res = int(param)
                return res
            else:
                page.open(alertDialogBadInput)
                return False

        alpha = float(alpha)
        numEmittersDetectors = validate_parameters(numEmittersDetectors)
        angSpread = validate_parameters(angSpread)

        if not alpha or not numEmittersDetectors or not angSpread:
            return

        runButton.visible = False
        loader.visible = True
        page.update()

        saveButton.disabled = True
        saveButton.update()

        try:
            if fileSelector.isDcm == False:
                plotData[0], plotData[1] = tomograph.run(fileSelector.selectedFilePath, alpha,
                                                         numEmittersDetectors, angSpread, isFiltered)
            else:
                plotData[0], plotData[1] = tomograph.run(fileSelector.selectedFilePath, alpha,
                                                         numEmittersDetectors, angSpread, isFiltered,
                                                         imageArray=fileSelector.imageDcm)

            maxIteration = max(plotData[0].keys())
            currentIteration = maxIteration

            sinogram.content = draw_plt_image(plotData[0], currentIteration)
            reconstructedImages.content = draw_plt_image(plotData[1], currentIteration)
            iterSliderContainer.content = get_slider(True)

            iterSliderContainer.update()
            sinogram.update()
            reconstructedImages.update()

            saveButton.disabled = False
            saveButton.update()
        except:
            page.open(alertDialogTomographRun)

        runButton.visible = True
        loader.visible = False
        page.update()

    alertDialogTomographRun = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text("There was an error in the tomograph process", color=ft.colors.BLACK)
    )

    alertDialogBadInput = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text("Input parameters are wrong type", color=ft.colors.BLACK)
    )

    filteredCheckbox = ft.Switch(value=False, inactive_track_color=ft.colors.GREEN_200, scale=0.8)

    paramNumEmittersDetectors = ft.TextField(width=75, scale=0.8, value='180')
    paramAngSpread = ft.TextField(width=75, scale=0.8, value='180')
    paramAlpha = ft.TextField(width=75, scale=0.8, value='4')

    runButton = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW_OUTLINED,
        on_click=lambda e: run_tomograph(
            e,
            isFiltered=filteredCheckbox.value,
            alpha=paramAlpha.value,
            numEmittersDetectors=paramNumEmittersDetectors.value,
            angSpread=paramAngSpread.value,
            saveButton=saveButton
        )
    )

    loader = ft.ProgressRing(visible=False)

    appbar = ft.AppBar(
        bgcolor=ft.colors.GREEN_300,
        title=ft.Row(
            controls=[
                ft.Text("TommyGraph", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                ft.Container(width=20),
                ft.MenuItemButton(
                    content=fileSelector.fileName,
                    leading=ft.Icon(ft.Icons.FOLDER),
                    style=ft.ButtonStyle(),
                    on_click=fileSelector.pick_file,
                )
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        actions=[
            paramNumEmittersDetectors,
            ft.Text("No. of detectors", size=14),
            paramAngSpread,
            ft.Text("Angular spread", size=14),
            paramAlpha,
            ft.Text("Alpha step", size=14),
            filteredCheckbox,
            ft.Text("Filtered", size=14),
            ft.Container(width=10),
            loader,
            runButton,
            ft.Container(width=10)
        ]
    )

    return appbar

def set_page_properties(page: ft.Page, fileSelector: FileLoader, saveButton: ft.ElevatedButton):
    page.title = "TommyGraph"
    page.theme_mode = "light"
    page.bgcolor = ft.Colors.GREEN_100
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN,
                          text_theme=ft.TextTheme(
                              body_medium=ft.TextStyle(font_family="Roboto")))
    page.appbar = get_appbar(page, fileSelector, saveButton)

def draw(page: ft.Page):
    global sinogram, reconstructedImages, currentIteration, maxIteration, iterSlider

    fileSelector = FileLoader(page)
    fileSaver = FileSaver(page)

    expansionDetailsTile, saveButton = get_details_field(fileSaver, fileSelector)
    set_page_properties(page, fileSelector, saveButton)

    leftColumn = ft.Container(
        content=ft.Column(
            [fileSelector.imageContainer,
             ft.Text("Source Image", bgcolor=ft.Colors.GREEN_200),
             expansionDetailsTile],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        ),
        width=350,
        padding=10,
    )

    mainContent = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                sinogram,
                                ft.Text("Sinogram", size=20, bgcolor=ft.Colors.GREEN_200),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        ),
                        ft.Column(
                            [
                                reconstructedImages,
                                ft.Text("Reconstructed Image", size=20, bgcolor=ft.Colors.GREEN_200)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                ft.Row([iterSliderContainer], expand=True)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        expand=True,
        padding=10
    )

    layout = ft.Row([leftColumn, mainContent], expand=True)
    page.add(layout)
    page.update()
