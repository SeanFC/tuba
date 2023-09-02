"""Repositories available to tuba"""
import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path

from tuba.domain import Channel, Video, VideoID


class YoutubeRepo(ABC):
    @abstractmethod
    def add_new_channel(self, channel: Channel):
        pass

    @abstractmethod
    def update_seen_video(self, video_id: VideoID):
        pass


class OnDiskYoutubeRepo(YoutubeRepo):
    _CHANNEL_PATH = "channel"
    _VIDEO_PATH = "video"
    _SEEN_VIDEOS_FILE = "seen.json"

    def __init__(self, path: Path):
        self._base_path = path
        (self._base_path / self._CHANNEL_PATH).mkdir(exist_ok=True)
        (self._base_path / self._VIDEO_PATH).mkdir(exist_ok=True)

    def add_new_channel(self, channel: Channel):
        for video in channel.known_videos:
            self._add_video(video)

        channel_dict = asdict(channel)
        channel_dict["known_videos"] = [
            video.id_ for video in channel_dict["known_videos"]
        ]

        with open(
            str(self._base_path / self._CHANNEL_PATH / channel.id_) + ".json", "w"
        ) as f:
            json.dump(channel_dict, f)

    def update_seen_video(self, video_id: VideoID):
        with open(self._base_path / self._SEEN_VIDEOS_FILE, "r") as f:
            current_seen = json.load(f)
        current_seen["seen"].append(video_id)

        with open(self._base_path / self._SEEN_VIDEOS_FILE, "w") as f:
            json.dump(f, current_seen)

    def _add_video(self, video: Video):
        with open(
            str(self._base_path / self._VIDEO_PATH / video.id_) + ".json", "w"
        ) as f:
            json.dump(asdict(video), f)
