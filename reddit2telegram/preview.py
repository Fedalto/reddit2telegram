from dataclasses import dataclass


@dataclass
class ImagePreview:
    title: str
    image_url: str


@dataclass
class VideoPreview:
    title: str
    video_url: str
    duration: int
    height: int
    width: int
