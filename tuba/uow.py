"""Unit of work to connect to repositories"""
from abc import ABC, abstractmethod
from pathlib import Path
from types import TracebackType

from tuba.repos import (
    BookmarkRepo,
    GoogleYoutubeRepo,
    OnDiskBookmarkRepo,
    OnDiskSubscriptionRepo,
    SubscriptionRepo,
    YoutubeRepo,
)


class UnitOfWork(ABC):
    """Make connections to all the repositories with a context manager"""

    subscription: SubscriptionRepo
    youtube: YoutubeRepo
    bookmark: BookmarkRepo

    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        """
        Open all the connections

        :return: The open manager
        """

    def __exit__(self, exc_type: type, exc_value: BaseException, exc_traceback: TracebackType):
        """Close all connections"""


class MainUnitOfWork(UnitOfWork):
    """Unit of work with a focus on disk and google's youtube API"""

    def __init__(self, subscription_path: Path, bookmark_path: Path):
        """
        :param subscription_path: The directory to store subscription information
        :param bookmark_path: The path to the bookmark file
        """
        self._subscription_path = subscription_path
        self._bookmark_path = bookmark_path

    def __enter__(self) -> UnitOfWork:
        """
        Open all the connections

        :return: The open manager
        """
        self.youtube = GoogleYoutubeRepo()
        self.subscription = OnDiskSubscriptionRepo(self._subscription_path)
        self.bookmark = OnDiskBookmarkRepo(self._bookmark_path)
        return self
