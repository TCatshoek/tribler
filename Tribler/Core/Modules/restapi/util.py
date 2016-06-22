"""
This file contains some utility methods that are used by the API.
"""
from Tribler.Core.Modules.restapi import VOTE_SUBSCRIBE


def convert_torrent_to_json(torrent):
    """
    Converts a given torrent to a JSON dictionary. Note that the torrent might be either a result from the local
    database in which case it is a tuple or a remote search result in which case it is a dictionary.
    """
    if isinstance(torrent, dict):
        return convert_remote_torrent_to_json(torrent)
    return convert_db_torrent_to_json(torrent)


def convert_db_channel_to_json(channel):
    """
    This method converts a channel in the database to a JSON dictionary.
    """
    relevance_score = 0.0
    if len(channel) >= 9: # The relevance score is not always present
        relevance_score = channel[8]

    return {"id": channel[0], "dispersy_cid": channel[1].encode('hex'), "name": channel[2], "description": channel[3],
            "votes": channel[5], "torrents": channel[4], "spam": channel[6], "modified": channel[8],
            "subscribed": (channel[7] == VOTE_SUBSCRIBE), "relevance_score": relevance_score}


def convert_db_torrent_to_json(torrent):
    """
    This method converts a torrent in the database to a JSON dictionary.
    """
    torrent_name = torrent[2] if torrent[2] is not None else "Unnamed torrent"

    relevance_score = 0.0
    if len(torrent) >= 10: # The relevance score is not always present
        relevance_score = torrent[9]

    return {"id": torrent[0], "infohash": torrent[1].encode('hex'), "name": torrent_name, "size": torrent[3],
            "category": torrent[4], "num_seeders": torrent[5] or 0, "num_leechers": torrent[6] or 0,
            "last_tracker_check": torrent[7] or 0, 'relevance_score': relevance_score}


def convert_remote_torrent_to_json(torrent):
    """
    This method converts a torrent that has been received by remote peers in the network to a JSON dictionary.
    """
    torrent_name = torrent['name'] if torrent['name'] is not None else "Unnamed torrent"

    return {'id': torrent['torrent_id'], "infohash": torrent['infohash'].encode('hex'), "name": torrent_name,
            'size': torrent['length'], 'category': torrent['category'], 'num_seeders': torrent['num_seeders'],
            'num_leechers': torrent['num_leechers'], 'last_tracker_check': 0, 'relevance_score': 0.0}
