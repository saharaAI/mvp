# --- src/utils/helpers.py ---
import zipfile
import io

def _create_project_zip(project_name, folder_structure, code_blocks):
    """Create a zip file containing project files."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder in folder_structure:
            zipf.writestr(f"{folder}/", "")
        for file_name, content in code_blocks:
            zipf.writestr(file_name, content)
    buffer.seek(0)
    return buffer
