# Media Management

µURU has a media management feature where users can upload media and use the
uploaded media for various purposes (for example as a telephone background image).

## Overview

µURU supports three kinds of media: `Audio`, `Image` and `Raw`. You can create
and delete your own (or if you're an admin all) media files in the media tab.

Media is stored at the configured `UURU_MEDIA_PATH` directory which must exist
before application startup. All uploaded media is converted to a default storage
format directly after it is uploaded and stored in this format.

The phone flavor class defines how media will be used and in which format it is
required for the phone. When media is assigned to a extension and the assigned
media is requested it gets automatically converted to the specified output type of
the phoneflavor.

## Implementation in Phone Flavor

To use media files a phoneflavor can define a dictionary with information
about required media. The dict is called `MEDIA`.

Example:

```python
class ExamplePhone(PhoneFlavor):
  # ... ommited other flavor specific code

  MEDIA = {

    "background_image": MediaDescriptor(
      media_type=MediaType.IMAGE,
      required=True,
      label="Background Image",
      out_format=ImageFormat(
        out_type="png", colormode="RGB", width=320, height=240
      )
    ),

    "ringtone": MediaDescriptor(
      media_type=MediaType.AUDIO,
      required=False,
      label="Ringtone",
      out_format=AudioFormat(
        out_type="wav", samplerate=44100, channels=1, bitdepth=8
      ),
      endpoint_filename="ringtone_xyz.wav"
    ),

    "firmware": MediaDescriptor(
      media_type=MediaType.RAW,
      required=False,
      label="Firmware",
      out_format=None
    )

  }
```

- `MediaDescriptor` attributes:
    - `media_type`: one of `MediaType.AUDIO`, `MediaType.IMAGE`, `MediaType.RAW`
    - `required`: `True` / `False`
    - `label`: `str` used as form label in the frontend
    - `endpoint_filename`: optional `str` that is used to build the request endpoint (see below)
    - `out_format`: one of `ImageFormat`, `AudioFormat` or `None` depending on the `media_type`

- `ImageFormat` attributes:
    - `out_type`: one of `avif`, `bmp`, `gif`, `jpeg`, `png`, `tiff`, `webp`
    - `samplerate`: `int` defaults to 44100
    - `channels`: `int` defaults to 2
    - `bitdepth`: `int` defaults to 16

- `AudioFormat` attributes:
    - `out_type`: one of `gsm`, `wav`, `ogg`, `mp3`, `flac`
    - `colormode`: one of `1` (monochrome), `L` (grayscale), `RGB` (default)
    - `width`: optional `int`
    - `height`: optional `int`
        - if only one of `width` or `height` is set, the aspect ratio is maintained

### Endpoints

Media files that were assigned to an extension can be requested via two (three) methods:

```
# By name (the key used in the MEDIA dict)
# the response is in the specified audio/image format of the flavor
   /api/v1/media/byextension/{extension}/{name}[.ext]

# By endpoint_filename (as in the MediaDescriptor)
# the response is in the specified audio/image format of the flavor
   /api/v1/media/byextension/{extension}/{endpoint_filename}

# Unconverted, static media file:
# the response is in the default storage format
   /api/v1/media/byid/{media_id}[.ext]
```

If the endpoint is marked with `[.ext]` you can optionally add any file-suffix you'd like to the request, this will be ignored.
