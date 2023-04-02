from pathlib import Path

from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

from gfuncs import auth


def _create_file(file_path_local: Path, folder_id: str) -> str:
    """Upload a non-existent file to Google Drive.

    Args:
        file_path_local (Path): Path to file on local machine.
        folder_id (str): Folder ID of parent folder on Google Drive.

    Returns:
        str: File ID of uploaded file.
    """
    service = auth.service("drive")
    file_metadata = {"name": file_path_local.name, "parents": [folder_id]}
    media = MediaFileUpload(str(file_path_local), resumable=True)
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    return file.get("id")


def _update_file(file_path_local: Path, file_id: str) -> str:
    """Update an existing file on Google Drive.

    Args:
        file_path_local (Path): Path to file on local machine.
        file_id (str): File ID of file on Google Drive.

    Returns:
        str: File ID of updated file.
    """
    service = auth.service("drive")
    media = MediaFileUpload(str(file_path_local), resumable=True)
    file = service.files().update(fileId=file_id, media_body=media).execute()

    return file.get("id")


def create_folder(path: Path) -> str:
    """Create a folder on Google Drive.

    Args:
        path (Path): Path of folder to create.

    Returns:
        str: Folder ID of created folder.
    """
    service = auth.service("drive")

    folder_names = path.parts
    parent_folder_id = "root"
    for folder_name in folder_names:
        query = (
            "mimeType='application/vnd.google-apps.folder' and name='"
            + folder_name
            + "' and trashed=false and '"
            + parent_folder_id
            + "' in parents"
        )
        response = (
            service.files()
            .list(q=query, fields="nextPageToken, files(id, name)")
            .execute()
        )
        if not response.get("files"):
            # Create a new folder if it doesn't exist
            file_metadata = {
                "name": folder_name,
                "parents": [parent_folder_id],
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = service.files().create(body=file_metadata, fields="id").execute()
            parent_folder_id = folder.get("id")
        else:
            # Use the existing folder if it already exists
            folder = response.get("files")[0]
            parent_folder_id = folder.get("id")

    return parent_folder_id


def download_file(file_path_local: Path, file_path_remote: Path) -> None:
    """Download a file from Google Drive.

    Args:
        file_path_local (Path): Path to file on local machine.
        file_path_remote (Path): Path to file on Google Drive.
    """
    service = auth.service("drive")

    file_id = file_exists(file_path_remote)
    if file_id:
        request = service.files().get_media(fileId=file_id)
        fh = open(str(file_path_local), "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.close()
    else:
        raise FileNotFoundError(f"File {file_path_remote} does not exist.")


def file_exists(path: Path) -> str:
    """Check if a file exists on Google Drive.

    Args:
        path (Path): Path of file to check.

    Returns:
        str: File ID of file if it exists, else empty string.
    """
    service = auth.service("drive")

    parent_id = folder_exists(path.parent)

    if parent_id:
        # check if the file exists in the parent folder
        query = f"name='{path.name}' and '{parent_id}' in parents"
        results = (
            service.files()
            .list(q=query, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        if not items:
            return ""  # file doesn't exist

        # return file id
        return items[0]["id"]

    return ""


def folder_exists(path: Path) -> str:
    """Check if a folder exists on Google Drive.

    Args:
        path (Path): Path of folder to check.

    Returns:
        str: Folder ID of folder if it exists, else empty string.
    """
    service = auth.service("drive")

    folder_names = path.parts
    parent_id = None

    # check each subfolder to see if it exists in the parent folder
    for folder_name in folder_names:
        query = (
            f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        )
        if parent_id:
            query += f" and '{parent_id}' in parents"
        results = (
            service.files()
            .list(q=query, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        if not items:
            return ""  # folder doesn't exist
        folder = items[0]
        parent_id = folder["id"]

    return parent_id


def upload_file(file_path_local: Path, folder_path_remote: Path) -> str:
    """Upload a file to Google Drive. If the file already exists, it will be
    updated. If the folder doesn't exist, it will be created.

    Args:
        file_path_local (Path): Path to file on local machine.
        folder_path_remote (Path): Path to folder on Google Drive.

    Returns:
        str: File ID of uploaded file.
    """
    if file_id := file_exists(folder_path_remote / file_path_local.name):
        return _update_file(file_path_local, file_id)
    else:
        if not (folder_id := folder_exists(folder_path_remote)):
            folder_id = create_folder(folder_path_remote)

        return _create_file(file_path_local, folder_id)
