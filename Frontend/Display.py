import flet as ft
from Frontend.Fileselector import FileSelector
from Backend.Tomograph import Tomograph

def get_appbar(page: ft.Page):
    # Appbar functions------------------
    def run_tomograph(e, alpha, numEmittersDetectors, angSpread, isFiltered):
        tomograph = Tomograph()

        # TODO: Check for valid parameters

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
    fileSelector = FileSelector(page)

    alertDialogNoFileSelected = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text("No .jpg file selected", color=ft.colors.BLACK)
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
        actions = [
            paramNumEmittersDetectors,
            ft.Text("No. of detectors", size=14),
            paramAngSpread,
            ft.Text("Angular spread", size=14),
            paramAlpha,
            ft.Text("Alpha step", size=14),
            filteredCheckbox,
            ft.Text("Filtered", size=14),
            loader,
            ft.Container(
                runButton,
                padding=ft.padding.only(right=10, left=10),
            )
        ]
    )

    return appbar

def set_page_properties(page: ft.Page):
    page.title = "TommyGraph"
    page.theme_mode = "light"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN,
                          text_theme=ft.TextTheme(
                              body_medium=ft.TextStyle(font_family="Roboto")))
    page.appbar = get_appbar(page)


def draw(page: ft.Page):
    set_page_properties(page)
    page.update()
