"""Start of execution for runners of Tuba"""
import logging
from pathlib import Path

from tuba.services import add_channel, set_channel_as_seen, update_channel
from tuba.uow import MainUnitOfWork


def main(simulation_path: str, bookmark_path: str):
    """
    Run through all the major functions

    :param simulation_path: Path the directory where to store simulaton data
    :param bookmark_path: Path to bookmark file
    """
    uow = MainUnitOfWork(Path(simulation_path), Path(bookmark_path))

    # Get a channel url from the bookmarks
    with uow:
        channel_urls = list(uow.bookmark.get_channels())
    channel_url = channel_urls[4]
    # "https://www.youtube.com/@BPSspace/videos",
    # "https://www.youtube.com/@built-from-scratch/videos"
    # "https://www.youtube.com/watch?v=A-X1PhR1D5Y"
    # channel_url = "https://www.youtube.com/channel/UC7Ay_bxnYWSS9ZDPpqAE1RQ/videos"

    logging.info(f"Adding channel {channel_url}")
    channel_id = add_channel(channel_url, uow)

    logging.info(f"Setting channel {channel_id} videos as seen")
    set_channel_as_seen(channel_id, uow)

    logging.info("Updating all channels")
    with uow:
        for channel_id in uow.subscription.get_all_channels():
            update_channel(channel_id, uow)

    logging.info("Finding unseen videos")
    with uow:
        for new_video in uow.subscription.get_unseen_videos():
            print(new_video)
