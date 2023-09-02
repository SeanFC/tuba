"""Data stores"""
import json
import pickle as pkl
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Iterator

from yt_dlp import YoutubeDL

from tuba.domain import Channel, ChannelID, Video, VideoID


class SubscriptionRepo(ABC):
    @abstractmethod
    def add_new_channel(self, channel: Channel):
        pass

    @abstractmethod
    def update_seen_video(self, video_id: VideoID):
        pass

    @abstractmethod
    def add_videos_to_channel(self, channel: Channel, videos: Iterable[Video]):
        pass

    @abstractmethod
    def get_channel(self, id_: ChannelID) -> Channel:
        pass


class YoutubeRepo(ABC):
    @abstractmethod
    def get_channel_from_url(self, channel_url: str):
        pass

    @abstractmethod
    def get_channel_videos(self, channel: Channel) -> Iterator[Video]:
        pass


class OnDiskSubscriptionRepo(SubscriptionRepo):
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

    def _get_video(self, id_: VideoID) -> Video:
        with open(str(self._base_path / self._VIDEO_PATH / id_) + ".json", "r") as f:
            video_dict = json.load(f)

        return Video(**video_dict)

    def _known_video(self, video: Video) -> bool:
        return (
            (self._base_path / self._VIDEO_PATH / video.id_)
            .with_suffix(".json")
            .exists()
        )

    def add_videos_to_channel(self, channel: Channel, videos: Iterable[Video]):
        with open(
            str(self._base_path / self._CHANNEL_PATH / channel.id_) + ".json", "r"
        ) as f:
            channel_dict = json.load(f)

        print(channel_dict)
        for video in videos:
            channel_dict["known_videos"] = list(
                set(channel_dict["known_videos"] + [video.id_])
            )

            if self._known_video(video):
                continue

            self._add_video(video)

        with open(
            str(self._base_path / self._CHANNEL_PATH / channel.id_) + ".json", "w"
        ) as f:
            json.dump(channel_dict, f)

    def get_channel(self, id_: ChannelID) -> Channel:
        with open(str(self._base_path / self._CHANNEL_PATH / id_) + ".json", "r") as f:
            channel_dict = json.load(f)

        video_ids = channel_dict.pop("known_videos")
        return Channel(
            **channel_dict,
            known_videos=[self._get_video(video_id) for video_id in video_ids]
        )


class GoogleYoutubeRepo(YoutubeRepo):
    def get_channel_from_url(self, channel_url: str) -> Channel:
        report = self._ask_google_for_channel(channel_url)

        return Channel(
            name=report["channel"],
            id_=ChannelID(report["channel_id"]),
            url=channel_url,
            known_videos=set(
                [
                    Video(
                        url=video_report["webpage_url"],
                        id_=VideoID(video_report["id"]),
                        channel_id=report["channel_id"],
                    )
                    for video_report in report["entries"]
                ]
            ),
        )

    def get_channel_videos(self, channel: Channel) -> Iterator[Video]:
        report = self._ask_google_for_channel(channel.url)

        return [
            Video(
                url=video_report["webpage_url"],
                id_=VideoID(video_report["id"]),
                channel_id=report["channel_id"],
            )
            for video_report in report["entries"]
        ]

    def _ask_google_for_channel(self, url) -> dict:
        if False:
            with YoutubeDL({"skip_download": True}) as ydl:
                report = ydl.extract_info(url)

            with open("/tmp/res.pkl", "wb") as f:
                pkl.dump(report, f)

        with open("/tmp/res.pkl", "rb") as f:
            report = pkl.load(f)

        return report
