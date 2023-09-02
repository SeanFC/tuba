"""Start of execution for runners of Tuba"""
import pickle as pkl
from pathlib import Path

import yt_dlp

from tuba.repos import OnDiskYoutubeRepo
from tuba.services import initialise_channel


def main(repo_path: str):
    ydl_opts = {"skip_download": True}
    if False:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(
                # "https://www.youtube.com/@BPSspace/videos",
                # "https://www.youtube.com/@built-from-scratch/videos"
                # "https://www.youtube.com/watch?v=A-X1PhR1D5Y"
                "https://www.youtube.com/channel/UC7Ay_bxnYWSS9ZDPpqAE1RQ/videos"
            )

        with open("res.pkl", "wb") as f:
            pkl.dump(result, f)

    with open("res.pkl", "rb") as f:
        result = pkl.load(f)

    youtube_repo = OnDiskYoutubeRepo(Path(repo_path))
    initialise_channel(result, youtube_repo)
