from fastapi import UploadFile, HTTPException
from supabase import create_client, Client
from config import settings
import uuid
from typing import Optional
from pathlib import Path


# Initialize Supabase client for storage
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


# Allowed file types for PDFs
ALLOWED_PDF_MIME_TYPES = [
    "application/pdf",
]

ALLOWED_PDF_EXTENSIONS = [".pdf"]


def validate_pdf_file(file: UploadFile) -> None:
    """Validate that the uploaded file is a PDF"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_PDF_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    # Check MIME type
    if file.content_type not in ALLOWED_PDF_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed"
        )


async def save_upload_file(
    file: UploadFile,
    bucket: str,
    folder: str = "",
    max_size: Optional[int] = None,
    validate_pdf: bool = True
) -> str:
    """
    Upload a file to Supabase Storage
    
    Args:
        file: The uploaded file
        bucket: Supabase storage bucket name (e.g., 'test-reports', 'certification-documents')
        folder: Optional folder path within the bucket
        max_size: Maximum file size in bytes
        validate_pdf: Whether to validate that file is a PDF
    
    Returns:
        Public URL or storage path of the uploaded file
    """
    if max_size is None:
        max_size = settings.MAX_FILE_SIZE
    
    # Validate PDF if required
    if validate_pdf:
        validate_pdf_file(file)
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB"
        )
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Construct storage path
    storage_path = f"{folder}/{unique_filename}" if folder else unique_filename
    
    try:
        # Upload to Supabase Storage
        response = supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket).get_public_url(storage_path)
        
        return public_url
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )


async def delete_file(bucket: str, file_path: str) -> bool:
    """
    Delete a file from Supabase Storage
    
    Args:
        bucket: Supabase storage bucket name
        file_path: Path to the file within the bucket
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        # Extract the path from public URL if full URL is provided
        if file_path.startswith("http"):
            # Extract path from URL
            path_parts = file_path.split(f"/storage/v1/object/public/{bucket}/")
            if len(path_parts) > 1:
                file_path = path_parts[1]
        
        supabase.storage.from_(bucket).remove([file_path])
        return True
    except Exception:
        return False


def get_file_url(bucket: str, file_path: str) -> str:
    """
    Get public URL for a file in Supabase Storage
    
    Args:
        bucket: Supabase storage bucket name
        file_path: Path to the file within the bucket
    
    Returns:
        Public URL of the file
    """
    try:
        return supabase.storage.from_(bucket).get_public_url(file_path)
    except Exception:
        return file_path  # Return original path if error
