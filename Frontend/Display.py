import flet as ft
from Frontend.Fileselector import FileSelector
from Backend.Tomograph import Tomograph

''' unused
def get_loading_overlay(page: ft.Page):
    overlay = ft.Container(
        ft.Column([
            ft.Text("Processing...", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD, size=40),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ft.colors.BLACK54,
        visible=False,
        width=page.width,
        height=page.height,
        alignment=ft.alignment.center,
    )

    return overlay
'''

def get_appbar(page: ft.Page):
    def run_tomograph(e):
        tomograph = Tomograph()

        runButton.visible = False
        loader.visible = True
        page.update()

        try:
            tomograph.run(fileSelector.selectedFilePath, 4, 180, 180, False)
        except:
            page.open(alertDialogNoFileSelected)

        runButton.visible = True
        loader.visible = False
        page.update()

    fileSelector = FileSelector(page)

    alertDialogNoFileSelected = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text("No .jpg file selected", color=ft.colors.BLACK)
    )

    runButton = ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW_OUTLINED,
                    on_click=run_tomograph
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
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        actions = [
            loader,
            ft.Container(
                runButton,
                padding=ft.padding.only(right=10),
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
