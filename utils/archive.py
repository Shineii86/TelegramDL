import os


def create_zip(files, zip_name):
    """Create a zip archive from files."""
    import zipfile
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))
    return zip_name
