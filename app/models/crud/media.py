"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
import os
import tempfile
import uuid

from fastapi import UploadFile
from sqlmodel import Session, select

from app.core.config import settings
from app.models.crud import CRUDNotAllowedException
from app.models.media import AudioFormat, ImageFormat, Media, MediaType
from app.models.user import User, UserRole
from app.util import media as media_utils


logger = getLogger(__name__)


def create_media_from_upload(
    session: Session,
    user: User,
    file: UploadFile,
    name: str,
    supposed_type: MediaType,
    default_format: ImageFormat | AudioFormat | None,
    autocommit: bool = True,
) -> Media:
    # Check for upload size limit
    if user.role == UserRole.USER or settings.MEDIA_LIMIT_SIZE_ADMIN:
        if not file.size:
            raise CRUDNotAllowedException("Failed to determine file size!")
        if file.size > settings.MEDIA_MAX_SIZE_USER:
            actual_size = media_utils.human_readable_filesize(file.size)
            max_size = media_utils.human_readable_filesize(settings.MEDIA_MAX_SIZE_USER)
            logger.error(
                f"User {user.username} tried to upload a {actual_size} ({file.size}) media file ({max_size} [{settings.MEDIA_MAX_SIZE_USER}] allowed)!"
            )
            raise CRUDNotAllowedException(
                f"Uploaded file is larger than the {max_size} upload limit!"
            )

    data = file.file.read()
    actual_type, actual_extension = media_utils.get_media_type(data)

    # check that the uploaded type matches the supposed type
    if supposed_type != MediaType.RAW and supposed_type != actual_type:
        raise CRUDNotAllowedException(
            f"The uploaded file does not seem to be actually an {supposed_type.value} file!"
        )

    # If a file that actuall is audio or image should be handled as a raw file
    if supposed_type == MediaType.RAW:
        actual_type = MediaType.RAW

    # check that the provided default_format matches the uploaded media type
    if (
        actual_type == MediaType.IMAGE and not isinstance(default_format, ImageFormat)
    ) or (
        actual_type == MediaType.AUDIO and not isinstance(default_format, AudioFormat)
    ):
        raise CRUDNotAllowedException(
            "The provideded default format does not match the uploaded file type!"
        )

    # Disallow RAW if configured
    if actual_type == MediaType.RAW and not settings.MEDIA_ALLOW_RAW:
        raise CRUDNotAllowedException("Raw media is not allowed!")

    # create database model
    db_obj = Media(name=name, type=actual_type, created_by_id=user.id, stored_as="")

    # convert to default format and store in media directory
    if not os.path.exists(settings.MEDIA_PATH):
        logger.error(f"Media upload directory {settings.MEDIA_PATH} does not exist!")
        raise RuntimeError(
            f"Media upload directory {settings.MEDIA_PATH} does not exist!"
        )

    # create filename based on uuid and type
    out_filename = db_obj.id.hex
    if actual_type != MediaType.RAW:
        out_filename += f".{default_format.out_type}"
    out_path = os.path.join(settings.MEDIA_PATH, out_filename)
    db_obj.stored_as = out_filename

    if actual_type == MediaType.RAW:
        with open(out_path, "xb") as target:
            target.write(data)
    else:
        with tempfile.NamedTemporaryFile(suffix=f".{actual_extension}") as source:
            source.write(data)
            source.seek(0)
            if actual_type == MediaType.IMAGE:
                media_utils.convert_image(source.name, out_path, default_format)
            elif actual_type == MediaType.AUDIO:
                media_utils.convert_audio(source.name, out_path, default_format)

    session.add(db_obj)
    if autocommit:
        session.commit()
        session.refresh(db_obj)

    logger.info(f"Created media {db_obj} {type(db_obj)}")
    return db_obj


def get_media_by_user(session: Session, user: User) -> list[Media]:
    statement = select(Media).where(Media.created_by_id == user.id)
    return list(session.exec(statement).all())


def get_all_media(session: Session) -> list[Media]:
    return list(session.exec(select(Media)).all())


def get_media_by_id(session: Session, media_id: str) -> Media | None:
    statement = select(Media).where(Media.id == uuid.UUID(media_id))
    return session.exec(statement).first()


def delete_media(session: Session, user: User, media: Media):
    if media.created_by_id != user.id and user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("You are not permitted to delete this media!")

    path = os.path.join(settings.MEDIA_PATH, media.stored_as)
    if not os.path.isfile(path):
        raise CRUDNotAllowedException("The media file was not found!")

    ## TODO: At this point should be checked if the media is in use somewhere

    os.remove(path)
    logger.info(f"rm {path}")
    session.delete(media)
    session.commit()
