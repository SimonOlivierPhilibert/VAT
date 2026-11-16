import asyncio
import io
import os
import time
from pathlib import Path

import flet as ft
import h5py
import numpy as np
import tifffile

os.environ['FLET_SECRET_KEY'] = os.urandom(12).hex()
repo_url = "https://github.com/SimonOlivierPhilibert/VAT"


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
                                              border_radius=10,
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
        
    def run_test():
        rng = np.random.default_rng(seed=17)
        array = rng.random((10, 256, 256))*255
        tifffile.imwrite('test.tif', array.astype('uint8'))

        array = tifffile.imread('uploads/ang_mv01.tif')
        print(array.shape, array.dtype)

    test_button = ft.Button(content='run test',
                            icon=ft.Icons.ARROW_FORWARD_IOS_ROUNDED,
                            on_click=run_test)

    def toggle_sidebar():
        sidebar.visible = not sidebar.visible
        toggle_sidebar_button.icon = (ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED if sidebar.visible
                                      else ft.Icons.ARROW_FORWARD_IOS_ROUNDED)

    toggle_sidebar_button = ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                                          on_click=toggle_sidebar)

    def toggle_editor(e: ft.Event[ft.Switch]) -> None:
        viewer_switch.disabled = not e.data
        editor.visible = e.data

    editor_switch = ft.Switch(label=ft.Row(controls=[ft.Icon(ft.Icons.LAYERS), ft.Text('2D Editor  ')]),
                              value=True,
                              on_change=toggle_editor,
                              label_position=ft.LabelPosition.LEFT)

    def toggle_viewer(e: ft.Event[ft.Switch]) -> None:
        editor_switch.disabled = not e.data
        viewer.visible = e.data

    viewer_switch = ft.Switch(label=ft.Row(controls=[ft.Icon(ft.Icons.VIEW_IN_AR), ft.Text('3D Viewer  ')]),
                              value=True,
                              on_change=toggle_viewer,
                              label_position=ft.LabelPosition.LEFT)

    repo_button = ft.Button(content='Github Repository',
                            icon=ft.Icons.OPEN_IN_NEW,
                            action=ft.OpenUrl(url=repo_url))

    page.title = 'MICHe Lab\'s Vascular Analysis Tool'
    page.appbar = ft.AppBar(leading=toggle_sidebar_button,
                            title=ft.Text(page.title),
                            actions=[test_button,
                                     ft.VerticalDivider(),
                                     editor_switch,
                                     ft.VerticalDivider(),
                                     viewer_switch,
                                     ft.VerticalDivider(),
                                     repo_button],
                            actions_padding=10)
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

    view_2d = ft.InteractiveViewer(ft.RawImage(fit=ft.BoxFit.CONTAIN, filter_quality=ft.FilterQuality.NONE), expand=True, min_scale=1, max_scale=10)
    editor = ft.Column(controls=[view_2d], expand=True)

    view_3d = ft.InteractiveViewer(ft.RawImage(fit=ft.BoxFit.CONTAIN, filter_quality=ft.FilterQuality.NONE), expand=True, min_scale=1, max_scale=10)
    viewer = ft.Column(controls=[view_3d], expand=True)


    views = ft.Row([sidebar, editor, viewer], expand=True)

    page.add(views)

    async def update_images():
        await asyncio.sleep(1)
        if editor.visible:
            await view_2d.content.render((np.random.random((10, 10, 3))*255).astype('uint8'))
        if viewer.visible:
            await view_3d.content.render((np.random.random((10, 10, 3))*255).astype('uint8'))

    while True:
        await update_images()
        

if __name__ == "__main__":
    DIR = Path(os.getenv('FLET_APP_STORAGE_DATA'))
    ft.run(main, upload_dir=DIR/'uploads', assets_dir=DIR)
    #uv run flet run --web main.py