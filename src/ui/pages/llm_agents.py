# --- src/ui/pages/llm_agents.py --- 
import streamlit as st
import os
import re
import json
import io
import zipfile
from core_logic.tasks.tasks import TaskManager

task_manager = TaskManager()


def display_llm_agents():
    """Renders the page for interacting with LLM agents."""
    #from app import task_manager  # Import inside the function to avoid circular import

    st.title("🤖 AI Task Orchestrator - Sahara Analytics")
    objective = st.text_area("Enter your objective:")
    file_content = st.text_area("Enter file content (optional):")
    use_search = st.checkbox("Use search")

    if st.button("Start Task"):
        with st.spinner("Processing your task..."):
            sub_task_results = task_manager.start_task(objective, file_content, use_search)
            refined_output = task_manager.generate_report(objective, sub_task_results)

            project_name = _extract_project_name(refined_output) or "default_project"
            folder_structure = _extract_folder_structure(refined_output)
            code_blocks = _extract_code_blocks(refined_output)
            zip_buffer = _create_project_zip(project_name, folder_structure, code_blocks)

            # --- Download and Display ---
            st.success("Task completed successfully!")

            # Offer the zip file for download
            st.download_button(
                label="Download Project Files",
                data=zip_buffer.getvalue(),
                file_name=f"{project_name}.zip",
                mime="application/zip"
            )

            # Display the full refined output
            st.subheader("Refined Output")
            st.text_area("", value=refined_output, height=300)

def _extract_project_name(refined_output):
    """Extracts the project name from the refined output."""
    match = re.search(r'Project Name: (.*)', refined_output)
    return match.group(1).strip() if match else None

def _extract_folder_structure(refined_output):
    """Extracts the folder structure from the refined output."""
    match = re.search(
        r'<folder_structure>(.*?)</folder_structure>', refined_output, re.DOTALL
    )
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON: {e}")
    return {}

def _extract_code_blocks(refined_output):
    """Extracts code blocks from the refined output."""
    return re.findall(r'Filename: (\S+)\s*```[\w]*\n(.*?)\n```', refined_output, re.DOTALL)

def _create_project_zip(project_name, folder_structure, code_blocks):
    """Creates a zip file containing the generated project."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        _create_folders_and_files_recursive(
            zip_file, project_name, folder_structure, code_blocks
        )
    return zip_buffer

def _create_folders_and_files_recursive(zip_file, current_path, structure, code_blocks):
    """Recursively creates folders and files in the zip archive."""
    for key, value in structure.items():
        path = os.path.join(current_path, key)
        if isinstance(value, dict):
            zip_file.writestr(path + '/', '')  # Create a directory in the zip
            _create_folders_and_files_recursive(
                zip_file, path, value, code_blocks
            )
        else:
            code_content = next(
                (code for file, code in code_blocks if file == key), None
            )
            if code_content:
                zip_file.writestr(path, code_content)
