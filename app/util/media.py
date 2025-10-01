"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

import filetype

from PIL import Image
import sox

from app.models.media import AudioFormat, ImageFormat, MediaType


SUPPORTED_IMAGE_FORMATS = ["avif", "bmp", "gif", "jpeg", "png", "tiff", "webp"]
SUPPORTED_AUDIO_FORMATS = ["gsm", "wav", "ogg", "mp3", "flac"]


def human_readable_filesize(num_bytes) -> str:
    """
    returns a human readable representation of the given amount
    of bytes as string
    """
    for prefix in ("", "Ki", "Mi", "Gi"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:3.1f} {prefix}B"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TiB"


def get_media_type(buffer: bytes) -> tuple[MediaType, str | None]:
    """
    guesses the media type based on the actual data
    and return that. If it failes to guess it falls back to RAW
    """
    kind = filetype.guess(buffer)

    if kind is not None:
        ext = kind.EXTENSION
        if ext == "jpg":  # pillow uses 'jpeg' instead of 'jpg'
            ext = "jpeg"
        if ext in SUPPORTED_IMAGE_FORMATS:
            return MediaType.IMAGE, ext
        elif ext in SUPPORTED_AUDIO_FORMATS:
            return MediaType.AUDIO, ext

    return MediaType.RAW, None


def convert_image(source_path: str, target_path: str, target_format: ImageFormat):
    """
    reads an image from the source path, converts it based on the given
    target_format and stores it at target_path
    """
    with Image.open(source_path) as im:
        im = im.convert(mode=target_format.colormode)

        if target_format.width is not None and target_format.height is not None:
            im = im.resize(
                (target_format.width, target_format.height), Image.Resampling.NEAREST
            )
        elif target_format.width is not None:
            ratio = im.size[1] / im.size[0]
            new_height = int(ratio * target_format.width)
            im = im.resize((target_format.width, new_height), Image.Resampling.NEAREST)
        elif target_format.height is not None:
            ratio = im.size[0] / im.size[1]
            new_width = int(ratio * target_format.height)
            im = im.resize((new_width, target_format.height), Image.Resampling.NEAREST)

        im.save(target_path, target_format.out_type)


def convert_audio(
    source_path: str, target_path: str, target_format: AudioFormat
) -> bool:
    """
    reads an audio from the source path, converts it based on the given
    target_format and stores it at target_path
    """

    tfm = sox.Transformer()
    tfm.convert(
        target_format.samplerate, target_format.channels, target_format.bitdepth
    )
    return tfm.build(source_path, target_path)
