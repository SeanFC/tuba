"""Start of execution for runners of Tuba"""
import logging
from pathlib import Path

from tuba.repos import GoogleYoutubeRepo, OnDiskSubscriptionRepo
from tuba.services import add_channel, update_channel


def main(repo_path: str):
    youtube_repo = GoogleYoutubeRepo()
    subscription_repo = OnDiskSubscriptionRepo(Path(repo_path))

    # "https://www.youtube.com/@BPSspace/videos",
    # "https://www.youtube.com/@built-from-scratch/videos"
    # "https://www.youtube.com/watch?v=A-X1PhR1D5Y"
    channel_url = "https://www.youtube.com/channel/UC7Ay_bxnYWSS9ZDPpqAE1RQ/videos"
    logging.info(f"Adding channel {channel_url}")
    channel_id = add_channel(channel_url, youtube_repo, subscription_repo)
    update_channel(channel_id, youtube_repo, subscription_repo)
