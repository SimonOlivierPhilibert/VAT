import flet as ft

def main(page: ft.Page):
    page.title = "Flet Theme Colors Reference"
    page.scroll = ft.ScrollMode.AUTO
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
    page.theme_mode = ft.ThemeMode.DARK

    # Define the key theme color attributes you want to showcase
    color_keys = [
        "primary", "on_primary", "primary_container", "on_primary_container",
        "secondary", "on_secondary", "secondary_container", "on_secondary_container",
        "tertiary", "on_tertiary", "tertiary_container", "on_tertiary_container",
        "error", "on_error", "error_container", "on_error_container",
        "surface", "on_surface", "surface_variant", "on_surface_variant",
        "outline", "outline_variant", "inverse_surface", "inverse_on_surface",
        "inverse_primary", "shadow", "scrim"
    ]

    def build_palette_grid():
        cards = []
        # Access the active color scheme from the page theme

        for key in color_keys:
            # Dynamically fetch the color value from the ColorScheme object
            color_val = getattr(ft.Colors, key.upper(), None)

            card = ft.Container(ft.Text(key.upper(), weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.WHITE),
                bgcolor=color_val,
                width=160,
                height=90,
                padding=10,
            )
            cards.append(card)

        return ft.Column(controls=cards, spacing=10, run_spacing=10)

    # UI Layout
    page.add(
        ft.Text("Theme Color Reference Palette", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Generated from current page theme color scheme.", italic=True),
        ft.Divider(),
        build_palette_grid()
    )

ft.run(main)