"""
Tuba services

These take inputs and pull info from the repos, perform domain logic and sort
results in the repos. Results can also be output to the caller.
"""
from tuba.domain import Channel, ChannelID, Video, VideoID
from tuba.repos import YoutubeRepo


def initialise_channel(report: dict, repo: YoutubeRepo):
    repo.add_new_channel(
        Channel(
            name=report["channel"],
            id_=ChannelID(report["channel_id"]),
            known_videos=set(
                [
                    Video(
                        url=video_report["webpage_url"],
                        id_=VideoID(video_report["id"]),
                        channel_id=report["channel_id"],
                    )
                    for video_report in report["entries"]
                ]
            ),
        )
    )
