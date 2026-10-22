import io

import flet as ft
import tifffile


def main(page: ft.Page):
    page.title = 'MICHe Lab\'s Vascular Analysis Tool'
    page.appbar = ft.AppBar(title=ft.Text(page.title), center_title=True)

    data = dict()
    arrays = []

    def handle_result(e: ft.FilePickerResultEvent):
        arrays.clear()
        arrays.extend([tifffile.imread(io.BytesIO(file.bytes))
                       for file in e.files])
        upload_button.disabled = not arrays

    def handle_upload():
        for array in arrays:
            print(array.shape, array.dtype)

    file_picker = ft.FilePicker(on_result=handle_result)
    page.services.append(file_picker)

    load_button = ft.Button(content='Load files...',
                            icon=ft.Icons.FILE_UPLOAD_OUTLINED,
                            action=ft.PickFiles(file_picker,
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