import flet as ft
import numpy as np


def main(page: ft.Page):
    counter = ft.Text(f'{np.random.random():.8f}', size=50, data=0)

    def increment_click(e):
        counter.value = f'{np.random.random():.8f}'

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.REFRESH, on_click=increment_click
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