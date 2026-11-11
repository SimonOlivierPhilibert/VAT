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
            self.gui_rows.append(ft.Container(ft.Row([self.progress[-1], ft.Text(name)]), padding=5, border_radius=10, on_click=lambda _: self.select(name)))

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

    def toggle_sidebar():
        print(sidebar.visible)
        sidebar.visible = not sidebar.visible

    page.title = 'MICHe Lab\'s Vascular Analysis Tool'
    page.appbar = ft.AppBar(leading=ft.IconButton(ft.Icons.FORMAT_LIST_BULLETED, on_click=toggle_sidebar), title=ft.Text(page.title))
    page.theme = ft.Theme(color_scheme=ft.ColorScheme(primary=ft.Colors.GREEN))
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
    
    def run_test():
        rng = np.random.default_rng(seed=17)
        array = rng.random((10, 256, 256))*255
        tifffile.imwrite('test.tif', array.astype('uint8'))
        
        array = tifffile.imread('uploads/ang_mv01.tif')
        print(array.shape, array.dtype)

    test_button = ft.Button(content='Test', on_click=run_test)

    sidebar = ft.Column([ft.Row([select_button, test_button]), ft.Column(projects.gui_rows, scroll=ft.ScrollMode.ADAPTIVE, expand=True)], expand=True)
    view_2d = ft.InteractiveViewer(ft.RawImage(fit=ft.BoxFit.CONTAIN, filter_quality=ft.FilterQuality.NONE), expand=True, min_scale=1, max_scale=10)
    view_3d = ft.InteractiveViewer(ft.RawImage(fit=ft.BoxFit.CONTAIN, filter_quality=ft.FilterQuality.NONE), expand=True, min_scale=1, max_scale=10)

    page.add(ft.Row([sidebar, view_2d, view_3d], expand=True))

    async def update_images():
        await asyncio.sleep(1)
        await view_2d.content.render((np.random.random((10, 10, 3))*255).astype('uint8'))
        await view_3d.content.render((np.random.random((10, 10, 3))*255).astype('uint8'))

    while True:
        await update_images()
        

if __name__ == "__main__":
    DIR = Path(os.getenv('FLET_APP_STORAGE_DATA'))
    ft.run(main, upload_dir=DIR/'uploads', assets_dir=DIR)
    #uv run flet run --web main.py