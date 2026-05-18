import uuid
from pathlib import Path
from models.medical_document import MedicalDocument

UPLOAD_DIR = Path("uploads")

def save_note_to_uploads(note: str,file_id: str, user_id: str) -> str:
    # ensure folder exists
    UPLOAD_DIR.mkdir(exist_ok=True)

    # generate unique filename
    filename = f"{user_id}_note_{file_id}.txt"

    file_path = UPLOAD_DIR / filename

    # write note into file
    file_path.write_text(note, encoding="utf-8")

    return str(file_path)

def create_note_document_helper(note: str, user_id: str) -> MedicalDocument:
    file_id = str(uuid.uuid4())
    file_path = save_note_to_uploads(note, file_id, user_id)
    return MedicalDocument(
        user_id=user_id,
        file_type="text",
        file_url=file_path,
        file_id=file_id
    )