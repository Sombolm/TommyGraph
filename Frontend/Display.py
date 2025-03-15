import flet as ft

def get_appbar():
    appbar = ft.AppBar(
        title=ft.Text("TommyGraph", color=ft.colors.WHITE),
        bgcolor=ft.colors.GREEN_300
    )
    return appbar

def set_page_properties(page: ft.Page):
    page.title = "TommyGraph"
    page.theme_mode = "light"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN,
                          text_theme=ft.TextTheme(
                              body_medium=ft.TextStyle(font_family="Roboto")))
    page.appbar = get_appbar()

def draw(page: ft.Page):
    set_page_properties(page)
    page.update()
