"""Unit of work to connect to repositories"""
from abc import ABC, abstractmethod
from pathlib import Path

from tuba.repos import GoogleYoutubeRepo, OnDiskSubscriptionRepo, SubscriptionRepo, YoutubeRepo


class UnitOfWork(ABC):
    subscription: SubscriptionRepo
    youtube: YoutubeRepo

    @abstractmethod
    def __enter__(self) -> "self":
        """TODO"""

    def __exit__(self):
        pass


class MainUnitOfWork(UnitOfWork):
    def __init__(self, repo_path: Path):
        self._repo_path = repo_path

    def __enter__(self) -> "self":
        self.youtube_repo = GoogleYoutubeRepo()
        self.subscription_repo = OnDiskSubscriptionRepo(self._repo_path)
        return self
