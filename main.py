import io
from pathlib import Path

import flet as ft
import h5py
import numpy as np
import tifffile


def file_to_dict(file: ft.FilePickerFile) -> dict:
    filename = Path(file.name).stem
    array = tifffile.imread(io.BytesIO(file.bytes))
    return {filename: dict(ang=array)}


def main(page: ft.Page):
    page.title = 'MICHe Lab\'s Vascular Analysis Tool'
    page.appbar = ft.AppBar(title=ft.Text(page.title), center_title=True)

    loaded_files = dict()

    def handle_result(e: ft.FilePickerResultEvent):
        for file in e.files:
            loaded_files.update(file_to_dict(file))
        upload_button.disabled = not loaded_files
        page.update()

    def handle_upload():
        for filename, data in loaded_files.items():
            print(filename, data.keys())

    picker = ft.FilePicker(on_result=handle_result)
    page.services.append(picker)

    load_button = ft.Button(content='Load files...',
                            icon=ft.Icons.FILE_UPLOAD_OUTLINED,
                            action=ft.PickFiles(picker,
                                                allow_multiple=True,
                                                file_type=ft.FilePickerFileType.CUSTOM,
                                                allowed_extensions=['tif', 'tiff'],
                                                with_data=True))

    upload_button = ft.Button(content='Share files...',
                              icon=ft.Icons.FOLDER_SHARED_OUTLINED,
                              on_click=handle_upload,
                              disabled=True)
    
    page.add(load_button, upload_button)


if __name__ == "__main__":
    ft.run(main)
    #uv run flet run --web main.py