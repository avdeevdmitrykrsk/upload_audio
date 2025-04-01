from pydantic import BaseModel


class AudioFileCreate(BaseModel):
    original_filename: str
    user_id: int


class AudioFileResponse(BaseModel):
    id: int
    name: str
    file_path: str

    class Config:
        from_attributes = True
