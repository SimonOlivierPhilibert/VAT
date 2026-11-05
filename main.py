import io
from pathlib import Path
import os

import flet as ft
import h5py
import numpy as np
import tifffile

os.environ['FLET_SECRET_KEY'] = os.urandom(12).hex()

def file_to_dict(file: ft.FilePickerFile) -> dict:
    filename = Path(file.name).stem
    array = tifffile.imread(io.BytesIO(file.bytes))
    return {filename: dict(ang=array)}

files = []

def main(page: ft.Page):

    page.title = 'MICHe Lab\'s Vascular Analysis Tool'
    page.appbar = ft.AppBar(title=ft.Text(page.title), center_title=True)

    projects = {}

    async def handle_result(e: ft.FilePickerResultEvent):

        for file in e.files:
            extension = Path(file.name).suffix
            if extension in ('.tif', '.tiff'):
                array = tifffile.imread(io.BytesIO(file.bytes))
                print(file.name, array.shape)
                tifffile.imwrite(f'{file.name}', array)
            elif extension in ('.h5', '.hdf5'):
                raise NotImplementedError
            else:
                print(f'{file.name} not supported')
                continue

        #await picker.upload(files=[ft.FilePickerUploadFile(name=file.name,
        #                                                   upload_url=page.get_upload_url(file.name, 600))
        #                           for file in e.files])

    picker = ft.FilePicker(on_result=handle_result,
                           on_upload=lambda e: print(e.progress))
    page.services.append(picker)

    def save_tif():
        rng = np.random.default_rng(seed=17)
        array = rng.random((10, 256, 256))*255
        tifffile.imwrite('test.tif', array.astype('uint8'))


    select_button = ft.Button(content='Select files',
                              icon=ft.Icons.FILE_UPLOAD_OUTLINED,
                              action=ft.PickFiles(picker,
                                                  allow_multiple=True,
                                                  file_type=ft.FilePickerFileType.CUSTOM,
                                                  allowed_extensions=['tif', 'tiff', 'h5', 'hdf5']))

    test_button = ft.Button(content='Test',
                            on_click=save_tif)

    
    page.add(ft.Column([select_button, test_button]))

if __name__ == "__main__":
    ft.run(main, upload_dir='projects')
    #uv run flet run --web main.py