"""Adapaters to data stored in some fashion to domain objects"""
import json
import pickle as pkl
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL

from tuba.domain import Channel, ChannelID, Video, VideoID


class SubscriptionRepo(ABC):
    """Store subscriptions to youtube channels and seen videos"""

    @abstractmethod
    def add_new_channel(self, channel: Channel):
        """
        Add a channel to the subscriptions

        :param channel: The channel to add
        """

    @abstractmethod
    def update_seen_videos(self, video_ids: Iterable[VideoID]):
        """
        Update all the videos that have been seen

        :param video_ids: The videos have been seen
        """

    @abstractmethod
    def add_videos_to_channel(self, channel: Channel, videos: Iterable[Video]):
        """
        Register videos with a particular channel

        :param channel: The channel to assocate with
        :param videos: The videos to associate with the channel
        """

    @abstractmethod
    def get_channel(self, id_: ChannelID) -> Channel:
        """
        Get a channel from an ID

        :param id_: The ID to get

        :return: The channel matching the ID
        """

    @abstractmethod
    def get_all_channels(self) -> Iterable[ChannelID]:
        """
        Get all known channels

        :return: The IDs of all the known channels
        """

    @abstractmethod
    def get_unseen_videos(self) -> Iterator[Video]:
        """
        :return: The videos
        """


class YoutubeRepo(ABC):
    """Connect to the Youtube API"""

    @abstractmethod
    def get_channel_from_url(self, channel_url: str) -> Channel:
        """
        :param channel_url: The URL of the channel to get

        :return: The channel
        """

    @abstractmethod
    def get_channel_videos(self, channel: Channel) -> Iterator[Video]:
        """
        :param channel: The channel to get videos from

        :return: The videos of the channel
        """


class BookmarkRepo:
    """Access bookmark information"""

    @abstractmethod
    def get_channels(self) -> Iterable[str]:
        """
        :return: All the youtubes channels in bookmarks
        """


class OnDiskSubscriptionRepo(SubscriptionRepo):
    """Store subscriptions locally on disk"""

    _CHANNEL_PATH = "channel"
    _VIDEO_PATH = "video"
    _SEEN_VIDEOS_FILE = "seen.json"

    def __init__(self, path: Path):
        """
        :param path: The file path to the directory to store subscription data
        """
        self._base_path = path
        (self._base_path / self._CHANNEL_PATH).mkdir(exist_ok=True)
        (self._base_path / self._VIDEO_PATH).mkdir(exist_ok=True)

        seen_videos_file_path = self._base_path / self._SEEN_VIDEOS_FILE
        if not seen_videos_file_path.exists():
            with open(seen_videos_file_path, "w") as f:
                json.dump({"seen": []}, f)

    def add_new_channel(self, channel: Channel):
        """
        Add a channel to the subscriptions

        :param channel: The channel to add
        """
        for video in channel.known_videos:
            self._add_video(video)

        channel_dict = asdict(channel)
        channel_dict["known_videos"] = [video.id_ for video in channel_dict["known_videos"]]

        with open(str(self._base_path / self._CHANNEL_PATH / channel.id_) + ".json", "w") as f:
            json.dump(channel_dict, f)

    def update_seen_videos(self, video_ids: Iterable[VideoID]):
        """
        Update all the videos that have been seen

        :param video_ids: The videos have been seen
        """
        with open(self._base_path / self._SEEN_VIDEOS_FILE, "r") as f:
            current_seen = json.load(f)

        current_seen["seen"].extend(list(video_ids))
        current_seen["seen"] = list(set(current_seen["seen"]))
        with open(self._base_path / self._SEEN_VIDEOS_FILE, "w") as f:
            json.dump(current_seen, f)

    def _add_video(self, video: Video):
        with open(str(self._base_path / self._VIDEO_PATH / video.id_) + ".json", "w") as f:
            json.dump(asdict(video), f)

    def _get_video(self, id_: VideoID) -> Video:
        with open(str(self._base_path / self._VIDEO_PATH / id_) + ".json", "r") as f:
            video_dict = json.load(f)

        return Video(**video_dict)

    def _known_video(self, video: Video) -> bool:
        return (self._base_path / self._VIDEO_PATH / video.id_).with_suffix(".json").exists()

    def add_videos_to_channel(self, channel: Channel, videos: Iterable[Video]):
        """
        Register videos with a particular channel

        :param channel: The channel to assocate with
        :param videos: The videos to associate with the channel
        """
        with open(str(self._base_path / self._CHANNEL_PATH / channel.id_) + ".json", "r") as f:
            channel_dict = json.load(f)

        for video in videos:
            channel_dict["known_videos"] = list(set(channel_dict["known_videos"] + [video.id_]))

            if self._known_video(video):
                continue

            self._add_video(video)

        with open(str(self._base_path / self._CHANNEL_PATH / channel.id_) + ".json", "w") as f:
            json.dump(channel_dict, f)

    def get_channel(self, id_: ChannelID) -> Channel:
        """
        Get a channel from an ID

        :param id_: The ID to get

        :return: The channel matching the ID
        """
        with open(str(self._base_path / self._CHANNEL_PATH / id_) + ".json", "r") as f:
            channel_dict = json.load(f)

        video_ids = channel_dict.pop("known_videos")
        return Channel(
            **channel_dict, known_videos=set([self._get_video(video_id) for video_id in video_ids])
        )

    def get_all_channels(self) -> Iterator[ChannelID]:
        """
        Get all known channels

        :return: The IDs of all the known channels
        """
        for path in (self._base_path / self._CHANNEL_PATH).iterdir():
            yield ChannelID(path.stem)

    def get_unseen_videos(self) -> Iterator[Video]:
        """
        :return: The videos
        """
        with open(self._base_path / self._SEEN_VIDEOS_FILE, "r") as f:
            current_seen = json.load(f)

        for video_path in (self._base_path / self._VIDEO_PATH).iterdir():
            video_id = video_path.stem
            if video_id not in current_seen["seen"]:
                yield self._get_video(video_id)


class GoogleYoutubeRepo(YoutubeRepo):
    """Connect to Google's Youtube API"""

    def get_channel_from_url(self, channel_url: str) -> Channel:
        """
        :param channel_url: The URL of the channel to get

        :return: The channel
        """
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
                        channel_id=ChannelID(report["channel_id"]),
                    )
                    for video_report in report["entries"]
                ]
            ),
        )

    def get_channel_videos(self, channel: Channel) -> Iterator[Video]:
        """
        :param channel: The channel to get videos from

        :return: The videos of the channel
        """
        report = self._ask_google_for_channel(channel.url)
        for video_report in report["entries"]:
            yield Video(
                url=video_report["webpage_url"],
                id_=VideoID(video_report["id"]),
                channel_id=ChannelID(report["channel_id"]),
            )

    def _ask_google_for_channel(self, url: str) -> Mapping[str, str]:
        # TODO; Maybe do some better logging than this. It can also take forever so log some updates
        def _pass_through(self: Any, x: Any) -> Any:
            return x

        class Logger:
            debug = _pass_through
            warning = _pass_through
            error = _pass_through

        # TODO: Delete all this pickling
        if False:
            with YoutubeDL(dict(skip_download=True, logger=Logger())) as ydl:
                report: Mapping[str, str] = ydl.extract_info(url)

            with open("/tmp/res.pkl", "wb") as f:
                pkl.dump(report, f)

        with open("/tmp/res.pkl", "rb") as f:
            report: Mapping[str, str] = pkl.load(f)

        return report


class OnDiskBookmarkRepo:
    """Access bookmark information on disk"""

    def __init__(self, bookmark_path: Path):
        """
        :param bookmark_path: Path to the bookmarks path
        """
        self._bookmark_path = bookmark_path

    def get_channels(self) -> Iterable[str]:
        """
        :return: All the youtubes channels in bookmarks
        """
        with open(Path(self._bookmark_path)) as f:
            data = f.read()

        for h3 in BeautifulSoup(data, "html.parser").find_all("h3"):
            if not h3.text == "Channels":
                continue
            idx = 0
            for sib in h3.next_siblings:
                idx += 1

                if idx == 2:
                    break
            for cur_a in sib.find_all("a"):
                yield cur_a["href"]
            break
