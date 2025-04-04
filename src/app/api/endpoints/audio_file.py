import os
import uuid
from http import HTTPStatus

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas.audio_file import AudioFileResponse
from app.core.db import get_async_session
from app.core.user import get_current_user
from app.crud.audio_file import audio_file_crud

router = APIRouter()

UPLOAD_DIR = 'uploads/audio'
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post('/upload-audio/', response_model=AudioFileResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    file_ext = os.path.splitext(file.filename)[1]
    stored_filename = f'{uuid.uuid4()}{file_ext}'
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    try:
        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception:
        raise HTTPException(
            HTTPStatus.INTERNAL_SERVER_ERROR, 'Failed to save file'
        )

    audio_file_data = {
        'name': file.filename,
        'file_path': stored_filename,
        'user_id': user.id,
    }
    audio_file = audio_file_crud.create(session, audio_file_data)

    session.add(audio_file)
    await session.commit()
    await session.refresh(audio_file)

    return AudioFileResponse(
        id=audio_file.id,
        name=audio_file.name,
        file_path=f'/api/download-audio/{audio_file.id}',
    )


@router.get('/download-audio/{file_id}')
async def download_audio_file(
    file_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    extra_data = {'user_id': user.id}
    audio_file = audio_file_crud.get_or_404(session, file_id, extra_data)
    file_path = os.path.join(UPLOAD_DIR, audio_file.file_path)

    if not os.path.exists(file_path):
        raise HTTPException(HTTPStatus.NOT_FOUND, 'File not found on server')

    return FileResponse(
        file_path,
        filename=audio_file.name,
    )
