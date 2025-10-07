"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.core.db import SessionDep
from app.core.config import settings
from app.models.crud.extension import get_extension_by_id
from app.models.media import AudioFormat, ImageFormat, Media, MediaType
from app.models.crud import CRUDNotAllowedException, media as media_crud
from app.models.user import UserRole
from app.telephoning.main import Telephoning
from app.util.media import get_converted_stream

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


# TODO: Decide if this endpoint should be login only
@router.get("/byid/{media_id}", response_class=FileResponse)
@router.get("/byid/{media_id}.{ext}", response_class=FileResponse)
def get_media_content(session: SessionDep, media_id: str, ext: Optional[str] = None):
    media = media_crud.get_media_by_id(session, media_id)
    if media is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")

    path = os.path.join(settings.MEDIA_PATH, media.stored_as)
    return path


@router.get("/byextension/{extension_id}/{query}", response_class=StreamingResponse)
def get_media_by_name(session: SessionDep, extension_id: str, query: str):
    extension = get_extension_by_id(session, extension_id, False)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown extension"
        )

    # get extension flavor
    flavor = Telephoning.get_flavor_by_type(extension.type)
    if flavor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown phonetype!"
        )

    # option a: the query is the name of the media (key of the MEDIA dict in flavor)
    name = query.split(".")[0]
    descr = flavor.MEDIA.get(name)
    media = None
    if descr is not None:
        assigned_media = {e.name: e for e in extension.assigned_media}
        media = assigned_media.get(name)

    if media is None:
        # option b: the query is the endpoint_filename of the media descriptor
        for name in flavor.MEDIA.keys():
            descr = flavor.MEDIA[name]
            if descr.endpoint_filename == query:
                assigned_media = {e.name: e for e in extension.assigned_media}
                media = assigned_media.get(name)
                break

    if media is None or descr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if media.media.type != MediaType.RAW:
        mime = f"{media.media.type.value}/{descr.out_format.out_type}"
    else:
        mime = "application/octet-stream"

    return StreamingResponse(
        get_converted_stream(media.media, descr.out_format), media_type=mime
    )
