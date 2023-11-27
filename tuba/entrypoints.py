"""Start of execution for runners of Tuba"""
import logging
from pathlib import Path

from tuba.repos import GoogleYoutubeRepo, OnDiskSubscriptionRepo
from tuba.services import add_channel, set_channel_as_seen, update_channel


def main(repo_path: str):
    youtube_repo = GoogleYoutubeRepo()
    subscription_repo = OnDiskSubscriptionRepo(Path(repo_path))

    from bs4 import BeautifulSoup

    with open("/home/sean/bookmarks.html") as f:
        data = f.read()

    soup = BeautifulSoup(data, "html.parser")
    channel_links = []
    for h3 in soup.find_all("h3"):
        if not h3.text == "Channels":
            continue
        idx = 0
        for sib in h3.next_siblings:
            idx += 1

            if idx == 2:
                break
        for cur_a in sib.find_all("a"):
            channel_links.append(cur_a["href"])
        break
    print(channel_links)

    # "https://www.youtube.com/@BPSspace/videos",
    # "https://www.youtube.com/@built-from-scratch/videos"
    # "https://www.youtube.com/watch?v=A-X1PhR1D5Y"
    # channel_url = "https://www.youtube.com/channel/UC7Ay_bxnYWSS9ZDPpqAE1RQ/videos"

    channel_url = list(channel_links)[4]
    logging.info(f"Adding channel {channel_url}")
    channel_id = add_channel(channel_url, youtube_repo, subscription_repo)

    logging.info(f"Setting channel {channel_id} videos as seen")
    set_channel_as_seen(channel_id, subscription_repo)

    logging.info("Updating all channels")
    for channel_id in subscription_repo.get_all_channels():
        update_channel(channel_id, youtube_repo, subscription_repo)

    logging.info("Finding unseen videos")
    for new_video in subscription_repo.get_unseen_videos():
        print(new_video)
