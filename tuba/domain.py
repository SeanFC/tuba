"""Domain logic"""

from dataclasses import dataclass

VideoID = str
ChannelID = str


@dataclass(frozen=True, eq=True)
class Video:
    url: str
    id_: VideoID
    channel_id: ChannelID


@dataclass(frozen=True, eq=True)
class Channel:
    name: str
    id_: ChannelID
    known_videos: set[Video]
