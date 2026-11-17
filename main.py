import asyncio
import os
from pathlib import Path

import flet as ft
import numpy as np
import tifffile

os.environ['FLET_SECRET_KEY'] = os.urandom(12).hex()
repo_url = "https://github.com/SimonOlivierPhilibert/VAT"
radius = 20


class Projects:

    def __init__(self) -> None:
        self.name_to_idx = {}
        self.paths = []
        self.progress = []
        self.gui_rows = []
        self.selected = None

    def __len__(self):
        return len(self.name_to_idx)

    def add(self, name: str) -> None:
        if name in self.name_to_idx:
            raise ValueError(f'{name} already exists')
        else:
            self.name_to_idx[name] = len(self)
            self.paths.append(None)
            self.progress.append(ft.ProgressRing(value=0., height=20, width=20, stroke_width=2, margin=1))
            self.gui_rows.append(ft.Container(ft.Row([self.progress[-1], ft.Text(name)]),
                                              padding=5,
                                              border_radius=radius,
                                              on_click=lambda _: self.select(name)))

    def update_progress(self, name: str, value: float) -> None:
        idx = self.name_to_idx[name]
        self.progress[idx].value = value
        if value == 1.:
            self.gui_rows[idx].content.controls[0] = ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN, size=24)
        else:
            self.gui_rows[idx].content.controls[0] = self.progress[idx]

    def select(self, name: str) -> None:
        if self.selected:
            idx = self.name_to_idx[self.selected]
            self.gui_rows[idx].bgcolor = None
        self.selected = name
        idx = self.name_to_idx[self.selected]
        self.gui_rows[idx].bgcolor = ft.Colors.PRIMARY_CONTAINER


async def main(page: ft.Page):

    radius = 20

    def toggle_sidebar() -> None:
        sidebar.visible = not sidebar.visible
        sidebar_switch.icon = (ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED
                               if sidebar.visible
                               else ft.Icons.ARROW_FORWARD_IOS_ROUNDED)

    sidebar_switch = ft.IconButton(
        icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
        on_click=toggle_sidebar,
    )

    def toggle_editor(
        e: ft.Event[ft.Switch],
    ) -> None:
        viewer_switch.disabled = not e.data
        editor_layout.visible = e.data

    editor_switch = ft.Switch(
        value=True,
        on_change=toggle_editor,
        label_position=ft.LabelPosition.LEFT,
        label=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LAYERS),
                ft.Text('2D Editor  '),
            ],
        ),
    )

    def toggle_viewer(
        e: ft.Event[ft.Switch],
    ) -> None:
        editor_switch.disabled = not e.data
        viewer_layout.visible = e.data

    viewer_switch = ft.Switch(
        value=True,
        on_change=toggle_viewer,
        label_position=ft.LabelPosition.LEFT,
        label=ft.Row(
            controls=[
                ft.Icon(ft.Icons.VIEW_IN_AR),
                ft.Text('3D Viewer  '),
            ],
        ),
    )

    repo_button = ft.Button(
        content='Github Repository',
        icon=ft.Icons.OPEN_IN_NEW,
        action=ft.OpenUrl(url=repo_url),
    )

    page.title = 'MICHe Lab\'s Vascular Analysis Tool'
    page.appbar = ft.AppBar(
        leading=sidebar_switch,
        title=ft.Text(page.title),
        actions=[
            editor_switch,
            ft.VerticalDivider(),
            viewer_switch,
            ft.VerticalDivider(),
            repo_button],
        actions_padding=10,
        bgcolor=ft.Colors.SHADOW,
        elevation_on_scroll=0,
    )
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
    page.theme_mode = ft.ThemeMode.DARK

    projects = Projects()

    async def handle_result(e: ft.FilePickerResultEvent):
        files = []
        for file in e.files:
            project_name = Path(file.name).stem
            try:
                projects.add(project_name)
                files.append(ft.FilePickerUploadFile(name=file.name, upload_url=page.get_upload_url(file.name, 600)))
            except:
                print('error occured')
        await picker.upload(files=files)

    def handle_upload(e: ft.FilePickerUploadEvent):
        projects.update_progress(Path(e.file_name).stem, e.progress)

    picker = ft.FilePicker(on_result=handle_result,
                           on_upload=handle_upload)
    page.services.append(picker)

    select_button = ft.Button(content='Upload Files',
                              icon=ft.Icons.UPLOAD,
                              action=ft.PickFiles(picker,
                                                  allow_multiple=True,
                                                  file_type=ft.FilePickerFileType.CUSTOM,
                                                  allowed_extensions=['tif', 'tiff', 'h5', 'hdf5']))
    
    sidebar = ft.Column([select_button, ft.Column(projects.gui_rows, scroll=ft.ScrollMode.ADAPTIVE, expand=True)], expand=True)
    
    def display_value(
        e: ft.Event[ft.Slider],
        values: list[int] | None = None,
    ) -> None:
        print(e.data)
        e.control.label = int(e.data) if values is None else values[int(e.data)]
    
    editor_controls = dict(
        image_contrast=ft.RangeSlider(
            start_value=0,
            end_value=1,
            expand=True,
        ),
        brush_radius=ft.Slider(
            value=0,
            min=0,
            max=10,
            divisions=10,
            on_change=lambda e: display_value(e, [1, 2, 3, 4, 5, 10, 20, 30, 50, 75, 100]),
            expand=True,
        ),
        clear_layer=ft.IconButton(
            icon=ft.Icons.CLEAR,
            tooltip=ft.Tooltip(
                message='Clear active layer'
            ),
        ),
        clear_all=ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP,
            tooltip=ft.Tooltip(
                message='Clear all layers'
            ),
        ),
        mode=ft.SegmentedButton(
            segments=[
                ft.Segment(
                    value='retouch',
                    icon=ft.Icons.AUTO_AWESOME,
                    label='Retouch'
                ),
                ft.Segment(
                    value='scribble',
                    icon=ft.Icons.GESTURE,
                    label='Scribble'
                ),
            ],
            selected=['retouch'],
            show_selected_icon=False,
        ),
        tool=ft.SegmentedButton(
            segments=[
                ft.Segment(
                    value='move',
                    icon=ft.Icons.PAN_TOOL,
                    label='Pan'
                ),
                ft.Segment(
                    value='edit',
                    icon=ft.Icons.BRUSH,
                    label='Draw'
                ),
            ],
            selected=['move'],
            show_selected_icon=False,
        ),
        frame=ft.Slider(
            value=0,
            min=0,
            max=10,
            divisions=10,
            on_change=display_value,
        ),
        view=ft.InteractiveViewer(
            aspect_ratio=None,
            expand=True,
            min_scale=1,
            max_scale=10,
            content=ft.RawImage(
                fit=ft.BoxFit.CONTAIN,
                filter_quality=ft.FilterQuality.NONE,
            ),
        ),
    )

    editor_layout = ft.Column(
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                padding=10,
                border_radius=radius,
                bgcolor=ft.Colors.SHADOW,
                content=ft.Column(
                    intrinsic_width=True,
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(
                                    expand=True,
                                    spacing=0,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            value='Image Constrast'
                                        ),
                                        editor_controls['image_contrast'],
                                    ],
                                ),
                                ft.Column(
                                    expand=True,
                                    spacing=0,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            value='Brush Radius'
                                        ),
                                        editor_controls['brush_radius'],
                                    ],
                                ),
                            ],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                editor_controls['mode'],
                                editor_controls['tool'],
                                editor_controls['clear_layer'],
                                editor_controls['clear_all'],
                            ],
                        ),
                    ],
                ),
            ),
            ft.Container(
                expand=True,
                border_radius=radius,
                bgcolor=ft.Colors.SHADOW,
                content=ft.Column(
                    spacing=0,
                    controls=[
                        ft.Row(
                            expand=True,
                            controls=[
                                editor_controls['view'],
                            ],
                        ),
                        editor_controls['frame'],
                    ],
                ),
            ),
        ],
    )

    viewer_controls = dict(
        refresh=ft.Button(
            content='Reload Figure',
            icon=ft.Icons.SYNC,
        ),
        graph=ft.Button(
            content='Extract Graph',
            icon=ft.Icons.SHARE,
        ),
        view=ft.InteractiveViewer(
            aspect_ratio=None,
            expand=True,
            min_scale=1,
            max_scale=10,
            content=ft.RawImage(
                fit=ft.BoxFit.CONTAIN,
                filter_quality=ft.FilterQuality.NONE
            ),
        ),
    )

    viewer_layout = ft.Column(
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                padding=10,
                border_radius=radius,
                bgcolor=ft.Colors.SHADOW,
                content=ft.Row(
                    tight=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        viewer_controls['graph'],
                        viewer_controls['refresh'],
                    ],
                ),
            ),
            ft.Container(
                expand=True,
                border_radius=radius,
                bgcolor=ft.Colors.SHADOW,
                content=ft.Row(
                    expand=True,
                    controls=[
                        viewer_controls['view'],
                    ],
                ),
            ),
        ],
    )

    views = ft.Row(
        spacing=20,
        expand=True,
        controls=[
            sidebar,
            editor_layout,
            viewer_layout,
        ],
    )

    page.add(views)

    async def update_images():
        await asyncio.sleep(1)
        if editor_layout.visible:
            await editor_controls['view'].content.render((np.random.random((10, 10, 3))*255).astype('uint8'))
        if viewer_layout.visible:
            await viewer_controls['view'].content.render((np.random.random((10, 10, 3))*255).astype('uint8'))

    while True:
        await update_images()
        

if __name__ == "__main__":
    DIR = Path(os.getenv('FLET_APP_STORAGE_DATA', './'))
    ft.run(main, upload_dir=DIR/'uploads', assets_dir=DIR)
    #uv run flet run --web main.py