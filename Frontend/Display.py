import flet as ft
from Frontend.Fileselector import FileSelector
from Backend.Tomograph import Tomograph

def get_details_field():
    def save_as_dicom():
        return

    saveButton = ft.ElevatedButton("Save as DICOM", on_click=save_as_dicom())
    patientDetails = ft.Text("No patient details yet.")

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
        # NOTE: should be false on deploy
        visible=True
    )

    return expansionDetailsTile

def get_appbar(page: ft.Page, fileSelector: FileSelector):
    # Appbar functions------------------
    def run_tomograph(e, alpha, numEmittersDetectors, angSpread, isFiltered):
        tomograph = Tomograph()

        def validate_parameters(param):
            if param.isdigit():
                res = int(param)
                return res
            else:
                page.open(alertDialogBadInput)
                return False

        alpha = validate_parameters(alpha)
        numEmittersDetectors = validate_parameters(numEmittersDetectors)
        angSpread = validate_parameters(angSpread)

        if not alpha or not numEmittersDetectors or not angSpread:
            return None

        runButton.visible = False
        loader.visible = True
        page.update()

        try:
            tomograph.run(fileSelector.selectedFilePath, alpha, numEmittersDetectors,
                          angSpread, isFiltered)
        except:
            page.open(alertDialogNoFileSelected)

        runButton.visible = True
        loader.visible = False
        page.update()

    # Appbar components----------------

    alertDialogNoFileSelected = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text("No .jpg file selected", color=ft.colors.BLACK)
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
        on_click=lambda e: run_tomograph(e, isFiltered=filteredCheckbox.value,
                                         alpha=paramAlpha.value,
                                         numEmittersDetectors=paramNumEmittersDetectors.value,
                                         angSpread=paramAngSpread.value
                                         )
    )

    loader = ft.ProgressRing(visible=False)

    # Appbar-------------------------
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

def set_page_properties(page: ft.Page, fileSelector: FileSelector):
    page.title = "TommyGraph"
    page.theme_mode = "light"
    page.bgcolor = ft.Colors.GREEN_100
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN,
                          text_theme=ft.TextTheme(
                              body_medium=ft.TextStyle(font_family="Roboto")))
    page.appbar = get_appbar(page, fileSelector)


def draw(page: ft.Page):
    fileSelector = FileSelector(page)
    set_page_properties(page, fileSelector)

    expansionDetailsTile = get_details_field()

    leftColumn = ft.Container(
        content=ft.Column(
            [expansionDetailsTile],
            expand=True
        ),
        width=350,
        padding=10,
    )

    mainContent = ft.Container(
        content=ft.Column(
            [fileSelector.image],
            alignment=ft.MainAxisAlignment.START,
        ),
        expand=True,
        padding=20
    )

    layout = ft.Row(
        [leftColumn, mainContent],
        expand=True
    )

    page.add(layout)

    # expansionDetailsTile = get_details_field()
    # page.add(expansionDetailsTile)
    page.update()
