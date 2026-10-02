import flet as ft
import numpy as np


def main(page: ft.Page):
    counter = ft.Text("0", size=50, data=0)

    def increment_click(e):
        counter.data = np.random.random()
        counter.value = str(counter.data)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                content=counter,
                alignment=ft.Alignment.CENTER,
            ),
        )
    )


ft.run(main)