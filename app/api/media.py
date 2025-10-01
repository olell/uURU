"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.core.db import SessionDep
from app.core.config import settings
from app.models.media import AudioFormat, ImageFormat, Media, MediaType
from app.models.crud import CRUDNotAllowedException, media as media_crud
from app.models.user import UserRole

router = APIRouter(prefix="/media", tags=["media"])
logger = getLogger(__name__)


class MediaCreateMeta(BaseModel):
    name: str
    supposed_type: MediaType


class MediaUpdateMeta(BaseModel):
    name: str


@router.post("/")
def create_media(
    session: SessionDep,
    user: CurrentUser,
    file: UploadFile,
    meta: MediaCreateMeta = Depends(),
) -> Media:
    default_format = None
    if meta.supposed_type == MediaType.IMAGE:
        default_format = ImageFormat(out_type=settings.MEDIA_IMAGE_STORAGE_FORMAT)
    elif meta.supposed_type == MediaType.AUDIO:
        default_format = AudioFormat(out_type=settings.MEDIA_AUDIO_STORAGE_FORMAT)

    try:
        media = media_crud.create_media_from_upload(
            session,
            user,
            file,
            meta.name,
            meta.supposed_type,
            default_format=default_format,
        )
        return media
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error("Encountered exception while processing uploaded media")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your media!",
        )


@router.get("/")
def get_media(
    session: SessionDep, user: CurrentUser, all_media: bool = False
) -> list[Media]:
    if all_media and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are permitted to request all media!",
        )
    try:
        if all_media:
            return media_crud.get_all_media(session)
        else:
            return media_crud.get_media_by_user(session, user)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(session: SessionDep, user: CurrentUser, media_id: str):
    media = media_crud.get_media_by_id(session, media_id)
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown media!"
        )

    try:
        media_crud.delete_media(session, user, media)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error("Encountered exception while deleting media")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete your media!",
        )


@router.put("/{media_id}")
def update_media(
    session: SessionDep, user: CurrentUser, media_id: str, data: MediaUpdateMeta
) -> Media:
    media = media_crud.get_media_by_id(session, media_id)
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown media!"
        )

    try:
        return media_crud.update_media(session, user, media, new_name=data.name)
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error("Encountered exception while updating media")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete your media!",
        )
