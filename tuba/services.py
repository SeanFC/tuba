"""
Take inputs and pull info from the repos, perform domain logic and sort results
in the repos. Results can also be output to the caller.
"""
from tuba.domain import ChannelID
from tuba.repos import SubscriptionRepo, YoutubeRepo


def add_channel(
    channel_url: str, youtube_repo: YoutubeRepo, subscription_repo: SubscriptionRepo
) -> ChannelID:
    channel = youtube_repo.get_channel_from_url(channel_url)
    subscription_repo.add_new_channel(channel)
    return channel.id_


def update_channel(
    id_: ChannelID, youtube_repo: YoutubeRepo, subscription_repo: SubscriptionRepo
):
    channel = subscription_repo.get_channel(id_)
    videos = youtube_repo.get_channel_videos(channel)
    subscription_repo.add_videos_to_channel(channel, videos)
