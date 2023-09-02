"""
Tuba services

These take inputs and pull info from the repos, perform domain logic and sort
results in the repos. Results can also be output to the caller.
"""

from tuba.domain import Channel, ChannelID, Video, VideoID
from tuba.repos import SubscriptionRepo, YoutubeRepo


def initialise_channel(
    channel_url: str, youtube_repo: YoutubeRepo, subscription_repo: SubscriptionRepo
):
    channel = youtube_repo.get_channel(channel_url)
    subscription_repo.add_new_channel(channel)
