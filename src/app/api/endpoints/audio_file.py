import os
import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, UserAudioFile
from app.schemas.audio_file import AudioFileResponse
from app.core.db import get_async_session
from app.core.user import get_current_user, user_manager

router = APIRouter()

UPLOAD_DIR = 'uploads/audio'
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post('/upload-audio/', response_model=AudioFileResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    file_ext = os.path.splitext(file.filename)[1]
    stored_filename = f'{uuid.uuid4()}{file_ext}'
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    try:
        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception:
        raise HTTPException(500, 'Failed to save file')

    audio_file = UserAudioFile(
        name=file.filename,
        file_path=stored_filename,
        user_id=user.id
    )

    session.add(audio_file)
    await session.commit()
    await session.refresh(audio_file)

    return AudioFileResponse(
        id=audio_file.id,
        name=audio_file.name,
        file_path=f'/api/download-audio/{audio_file.id}'
    )


@router.get('/download-audio/{file_id}')
async def download_audio_file(
    file_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(UserAudioFile).where(
            (UserAudioFile.id == file_id)
            & (UserAudioFile.user_id == user.id)
        )
    )
    audio_file = result.scalars().first()

    if not audio_file:
        raise HTTPException(404, 'File not found')

    file_path = os.path.join(UPLOAD_DIR, audio_file.file_path)

    if not os.path.exists(file_path):
        raise HTTPException(404, 'File not found on server')

    return FileResponse(
        file_path,
        filename=audio_file.name,
    )
