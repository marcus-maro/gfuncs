import os
from pathlib import Path

from gfuncs import drive


def test_create_folder_folder_exists_root():
    """Test that a folder is created in the root directory."""
    path = Path("test_root")
    folder_id = drive.create_folder(path)
    assert drive.folder_exists(path) == folder_id


def test_create_folder_folder_exists_nested():
    """Test that a folder is created in a nested directory."""
    path = Path("test_root/test_nested/test_nested")
    folder_id = drive.create_folder(path)
    assert drive.folder_exists(path) == folder_id


def test_folder_exists_root_false():
    """Test that a folder does not exist in the root directory."""
    path = Path("does_not_exist")
    folder_id = drive.folder_exists(path)
    assert folder_id == ""


def test_folder_exists_nested_false():
    """Test that a folder does not exist in a nested directory."""
    path = Path("test_root/does_not_exist/does_not_exist")
    folder_id = drive.folder_exists(path)
    assert folder_id == ""


def test_upload_file_file_exists():
    """Test that a file is uploaded to Google Drive."""
    file_path_local = Path(__file__)
    folder_path_remote = Path("test_root")
    file_id = drive.upload_file(file_path_local, folder_path_remote)
    assert drive.file_exists(folder_path_remote / file_path_local.name) == file_id


def test_download_file():
    """Test that a file is downloaded from Google Drive."""
    file_path_local = Path(__file__).parent / "test_download_file.py"
    file_path_remote = Path("test_root") / "test_drive.py"
    drive.download_file(file_path_local, file_path_remote)
    assert file_path_local.exists()
    os.remove(file_path_local)
