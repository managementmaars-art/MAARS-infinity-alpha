"""
File Upload and Processing - Demonstrates file handling in Reflex

Shows: File uploads, async processing, file type validation, progress feedback
"""

import reflex as rx
import asyncio
from pathlib import Path


class FileUploadState(rx.State):
    """State for file upload functionality."""

    # Upload state
    uploaded_files: list[dict[str, str]] = []
    upload_progress: str = ""
    is_uploading: bool = False

    # Allowed file types
    allowed_extensions: list[str] = [".txt", ".csv", ".json", ".pdf", ".png", ".jpg"]

    @rx.var
    def file_count(self) -> int:
        """Get count of uploaded files."""
        return len(self.uploaded_files)

    @rx.var
    def total_size(self) -> str:
        """Calculate total size of uploaded files."""
        total_bytes = sum(int(f.get("size", 0)) for f in self.uploaded_files)
        if total_bytes < 1024:
            return f"{total_bytes} B"
        elif total_bytes < 1024 * 1024:
            return f"{total_bytes / 1024:.2f} KB"
        else:
            return f"{total_bytes / (1024 * 1024):.2f} MB"

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Process uploaded files."""
        self.is_uploading = True
        self.upload_progress = "Processing files..."

        # Create uploads directory if it doesn't exist
        upload_dir = Path("./uploads")
        upload_dir.mkdir(exist_ok=True)

        for i, file in enumerate(files):
            # Update progress
            self.upload_progress = f"Processing {i+1}/{len(files)}: {file.filename}"

            # Validate file type
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                self.upload_progress = f"Skipped {file.filename}: Invalid file type"
                await asyncio.sleep(1)
                continue

            # Read file data
            upload_data = await file.read()
            file_size = len(upload_data)

            # Save file
            outfile = upload_dir / file.filename
            with open(outfile, "wb") as f:
                f.write(upload_data)

            # Add to uploaded files list
            self.uploaded_files.append({
                "name": file.filename,
                "size": str(file_size),
                "type": file_ext,
                "path": str(outfile),
            })

            # Simulate processing time
            await asyncio.sleep(0.5)

        self.upload_progress = f"Successfully uploaded {len(files)} file(s)"
        self.is_uploading = False

        # Clear progress after 3 seconds
        await asyncio.sleep(3)
        self.upload_progress = ""

    def clear_file(self, filename: str):
        """Remove a file from the list."""
        self.uploaded_files = [
            f for f in self.uploaded_files if f["name"] != filename
        ]

    def clear_all(self):
        """Clear all uploaded files."""
        self.uploaded_files = []
        self.upload_progress = ""


def file_item(file: dict) -> rx.Component:
    """Render a single uploaded file."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(file["name"], font_weight="bold"),
                rx.hstack(
                    rx.badge(file["type"], color_scheme="blue"),
                    rx.text(
                        f"{int(file['size']) / 1024:.2f} KB",
                        color="gray.600",
                        font_size="sm",
                    ),
                    spacing="2",
                ),
                align="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.button(
                "Remove",
                on_click=lambda: FileUploadState.clear_file(file["name"]),
                size="sm",
                color_scheme="red",
                variant="outline",
            ),
            width="100%",
            align="center",
        ),
        padding="4",
        border="1px solid #e2e8f0",
        border_radius="md",
        bg="white",
        width="100%",
    )


def index() -> rx.Component:
    """Main page with file upload."""
    return rx.container(
        rx.vstack(
            rx.heading("File Upload Manager", size="2xl", mb="6"),

            # Upload area
            rx.box(
                rx.vstack(
                    rx.icon("upload", size=48, color="gray.400"),
                    rx.heading("Upload Files", size="lg"),
                    rx.text(
                        f"Allowed types: {', '.join(FileUploadState.allowed_extensions)}",
                        color="gray.600",
                        font_size="sm",
                    ),

                    rx.upload(
                        rx.button(
                            "Select Files",
                            color_scheme="blue",
                            size="lg",
                        ),
                        id="file_upload",
                        multiple=True,
                        accept={
                            "text/plain": [".txt"],
                            "text/csv": [".csv"],
                            "application/json": [".json"],
                            "application/pdf": [".pdf"],
                            "image/png": [".png"],
                            "image/jpeg": [".jpg"],
                        },
                    ),

                    rx.button(
                        "Upload Selected Files",
                        on_click=FileUploadState.handle_upload(
                            rx.upload_files(upload_id="file_upload")
                        ),
                        color_scheme="green",
                        size="lg",
                        disabled=FileUploadState.is_uploading,
                    ),

                    # Progress message
                    rx.cond(
                        FileUploadState.upload_progress != "",
                        rx.text(
                            FileUploadState.upload_progress,
                            color="blue.600",
                            font_weight="bold",
                        ),
                        rx.box(),
                    ),

                    spacing="4",
                    align="center",
                ),
                padding="8",
                border="2px dashed #cbd5e0",
                border_radius="lg",
                bg="gray.50",
                width="100%",
                text_align="center",
            ),

            # Statistics
            rx.cond(
                FileUploadState.file_count > 0,
                rx.box(
                    rx.hstack(
                        rx.stat(
                            rx.stat_label("Files Uploaded"),
                            rx.stat_number(FileUploadState.file_count),
                        ),
                        rx.stat(
                            rx.stat_label("Total Size"),
                            rx.stat_number(FileUploadState.total_size),
                        ),
                        rx.button(
                            "Clear All",
                            on_click=FileUploadState.clear_all,
                            color_scheme="red",
                            variant="outline",
                        ),
                        spacing="8",
                        width="100%",
                        justify="space-between",
                        align="center",
                    ),
                    padding="6",
                    bg="blue.50",
                    border_radius="md",
                    width="100%",
                ),
                rx.box(),
            ),

            # Uploaded files list
            rx.cond(
                FileUploadState.file_count > 0,
                rx.vstack(
                    rx.heading("Uploaded Files", size="lg", mb="2"),
                    rx.foreach(FileUploadState.uploaded_files, file_item),
                    spacing="3",
                    width="100%",
                ),
                rx.box(),
            ),

            spacing="6",
            width="100%",
            padding_y="8",
        ),
        max_width="800px",
    )


app = rx.App()
app.add_page(index)
