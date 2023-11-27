"""
Take inputs and pull info from the repos, perform domain logic and sort results in the repos.
Results can also be output to the caller.
"""
from tuba.domain import ChannelID
from tuba.uow import UnitOfWork


def add_channel(channel_url: str, uow: UnitOfWork) -> ChannelID:
    """
    Add a channel to the repo

    :param channel_url: The URL of the channel to add
    :param uow: The unit of work to connect to the repositories

    :return: The ID of the channel added
    """
    with uow:
        channel = uow.youtube.get_channel_from_url(channel_url)
        uow.subscription.add_new_channel(channel)
    return channel.id_


def update_channel(id_: ChannelID, uow: UnitOfWork):
    """
    Update all the known videos from a channel

    :param id_: The channel to update
    :param uow: The unit of work to connect to the repositories
    """
    with uow:
        channel = uow.subscription.get_channel(id_)
        videos = uow.youtube.get_channel_videos(channel)
        uow.subscriptiono.add_videos_to_channel(channel, videos)


def set_channel_as_seen(id_: ChannelID, uow: UnitOfWork):
    """
    Mark all the videoes in a channel as seen

    :param id_: The channel to mark
    :param uow: The unit of work to connect to the repositories
    """
    with uow:
        channel = uow.subscription.get_channel(id_)
        uow.subscription.update_seen_videos([video.id_ for video in channel.known_videos])
