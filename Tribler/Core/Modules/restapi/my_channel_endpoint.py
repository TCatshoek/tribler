import json
import base64
import logging

from twisted.web import http, resource

from Tribler.Core.CacheDB.sqlitecachedb import str2bin
from Tribler.Core.TorrentDef import TorrentDef
from Tribler.Core.simpledefs import NTFY_CHANNELCAST
from Tribler.Core.exceptions import DuplicateChannelNameError, DuplicateTorrentFileError


class MyChannelEndpoint(MyChannelBaseEndpoint):
    """
    This endpoint is responsible for handing all requests regarding your channel such as getting and updating
    torrents, playlists and rss-feeds.
    """

    def __init__(self, session):
        MyChannelBaseEndpoint.__init__(self, session)
        child_handler_dict = {"torrents": MyChannelTorrentsEndpoint,
                              "playlists": MyChannelPlaylistsEndpoint,
                              "recheckfeeds": MyChannelRecheckFeedsEndpoint}
        for path, child_cls in child_handler_dict.iteritems():
            self.putChild(path, child_cls(self.session))

    def render_GET(self, request):
        """
        .. http:get:: /mychannel

        Return the name, description and identifier of your channel.
        This endpoint returns a 404 HTTP response if you have not created a channel (yet).

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/mychannel

            **Example response**:

            .. sourcecode:: javascript

                {
                    "overview": {
                        "name": "My Tribler channel",
                        "description": "A great collection of open-source movies",
                        "identifier": "4a9cfc7ca9d15617765f4151dd9fae94c8f3ba11"
                    }
                }

            :statuscode 404: if your channel has not been created (yet).
        """
        my_channel_id = self.channel_db_handler.getMyChannelId()
        if my_channel_id is None:
            return MyChannelBaseEndpoint.return_404(request)

        my_channel = self.channel_db_handler.getChannel(my_channel_id)
        return json.dumps({'overview': {'identifier': my_channel[1].encode('hex'), 'name': my_channel[2],
                                        'description': my_channel[3]}})


class MyChannelTorrentsEndpoint(MyChannelBaseEndpoint):
    """
    This end is responsible for handling requests regarding torrents in your channel.
    """

    def getChild(self, path, request):
        return MyChannelModifyTorrentsEndpoint(self.session, path)

    def render_GET(self, request):
        """
        .. http:get:: /mychannel/torrents

        Return the torrents in your channel. For each torrent item, the infohash, name and timestamp added is included.
        This endpoint returns a 404 HTTP response if you have not created a channel (yet).

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/mychannel/torrents

            **Example response**:

            .. sourcecode:: javascript

                {
                    "torrents": [{
                        "name": "ubuntu-15.04.iso",
                        "added": 1461840601,
                        "infohash": "e940a7a57294e4c98f62514b32611e38181b6cae"
                    }, ...]
                }

            :statuscode 404: if your channel does not exist.
        """
        my_channel_id = self.channel_db_handler.getMyChannelId()
        if my_channel_id is None:
            return MyChannelBaseEndpoint.return_404(request)

        req_columns = ['ChannelTorrents.name', 'infohash', 'ChannelTorrents.inserted']
        torrents = self.channel_db_handler.getTorrentsFromChannelId(my_channel_id, True, req_columns)

        torrent_list = []
        for torrent in torrents:
            torrent_list.append({'name': torrent[0], 'infohash': torrent[1].encode('hex'), 'added': torrent[2]})
        return json.dumps({'torrents': torrent_list})

    def render_PUT(self, request):
        """
        .. http:put:: /mychannel/torrents

        Add a torrent file to your own channel. Returns error 500 if something is wrong with the torrent file
        and DuplicateTorrentFileError if already added to your channel. The torrent data is passed as base-64 encoded
        string. The description is optional.

            **Example request**:

            .. sourcecode:: none

                curl -X PUT http://localhost:8085/mychannel/torrents --data "torrent=...&description=funny video"

            **Example response**:

            .. sourcecode:: javascript

                {
                    "added": True
                }

            :statuscode 404: if your channel does not exist.
            :statuscode 500: if the passed torrent data is corrupt.
        """
        my_channel_id = self.channel_db_handler.getMyChannelId()
        if my_channel_id is None:
            return MyChannelBaseEndpoint.return_404(request)

        parameters = http.parse_qs(request.content.read(), 1)

        if 'torrent' not in parameters or len(parameters['torrent']) == 0:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "torrent parameter missing"})

        if 'description' not in parameters or len(parameters['description']) == 0:
            extra_info = {}
        else:
            extra_info = {'description': parameters['description'][0]}

        try:
            torrent = base64.b64decode(parameters['torrent'][0])
            torrent_def = TorrentDef.load_from_memory(torrent)
            self.session.add_torrent_def_to_channel(my_channel_id, torrent_def, extra_info, forward=True)

        except (DuplicateTorrentFileError, ValueError) as ex:
            return MyChannelBaseEndpoint.return_500(self, request, ex)

        return json.dumps({"added": True})


class MyChannelModifyTorrentsEndpoint(MyChannelBaseEndpoint):
    """
    This class is responsible for methods that modify the list of torrents (adding/removing torrents).
    """

    def __init__(self, session, torrent_url):
        MyChannelBaseEndpoint.__init__(self, session)
        self.torrent_url = torrent_url

    def render_PUT(self, request):
        """
        .. http:put:: /mychannel/torrents/http%3A%2F%2Ftest.com%2Ftest.torrent

        Add a torrent by magnet or url to your channel. Returns error 500 if something is wrong with the torrent file
        and DuplicateTorrentFileError if already added to your channel (except with magnet links).

            **Example request**:

            .. sourcecode:: none

                curl -X PUT http://localhost:8085/mychannel/torrents/http%3A%2F%2Ftest.com%2Ftest.torrent
                            --data "description=nice video"

            **Example response**:

            .. sourcecode:: javascript

                {
                    "added": "http://test.com/test.torrent"
                }

            :statuscode 404: if your channel does not exist.
            :statuscode 500: if the specified torrent is already in your channel.
        """
        my_channel_id = self.channel_db_handler.getMyChannelId()
        if my_channel_id is None:
            return MyChannelBaseEndpoint.return_404(request)

        parameters = http.parse_qs(request.content.read(), 1)

        if 'description' not in parameters or len(parameters['description']) == 0:
            extra_info = {}
        else:
            extra_info = {'description': parameters['description'][0]}

        try:
            if self.torrent_url.startswith("http:") or self.torrent_url.startswith("https:"):
                torrent_def = TorrentDef.load_from_url(self.torrent_url)
                self.session.add_torrent_def_to_channel(my_channel_id, torrent_def, extra_info, forward=True)
            if self.torrent_url.startswith("magnet:"):

                def on_receive_magnet_meta_info(meta_info):
                    torrent_def = TorrentDef.load_from_dict(meta_info)
                    self.session.add_torrent_def_to_channel(my_channel_id, torrent_def, extra_info, forward=True)

                infohash_or_magnet = self.torrent_url
                callback = on_receive_magnet_meta_info
                self.session.lm.ltmgr.get_metainfo(infohash_or_magnet, callback)

        except (DuplicateTorrentFileError, ValueError) as ex:
            return MyChannelBaseEndpoint.return_500(self, request, ex)

        return json.dumps({"added": self.torrent_url})


class MyChannelPlaylistsEndpoint(MyChannelBaseEndpoint):
    """
    This class is responsible for handling requests regarding playlists in your channel.
    """

    def render_GET(self, request):
        """
        .. http:get:: /mychannel/playlists

        Returns the playlists in your channel. Returns error 404 if you have not created a channel.

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/mychannel/playlists

            **Example response**:

            .. sourcecode:: javascript

                {
                    "playlists": [{
                        "id": 1,
                        "name": "My first playlist",
                        "description": "Funny movies",
                        "torrents": [{
                            "name": "movie_1",
                            "infohash": "e940a7a57294e4c98f62514b32611e38181b6cae"
                        }, ... ]
                    }, ...]
                }

            :statuscode 404: if you have not created a channel.
        """
        my_channel_id = self.channel_db_handler.getMyChannelId()
        if my_channel_id is None:
            return MyChannelBaseEndpoint.return_404(request)

        playlists = []
        req_columns = ['Playlists.id', 'Playlists.name', 'Playlists.description']
        req_columns_torrents = ['ChannelTorrents.name', 'Torrent.infohash']
        for playlist in self.channel_db_handler.getPlaylistsFromChannelId(my_channel_id, req_columns):
            # Fetch torrents in the playlist
            torrents = []
            for torrent in self.channel_db_handler.getTorrentsFromPlaylist(playlist[0], req_columns_torrents):
                torrents.append({"name": torrent[0], "infohash": str2bin(torrent[1]).encode('hex')})

            playlists.append({"id": playlist[0], "name": playlist[1], "description": playlist[2], "torrents": torrents})

        return json.dumps({"playlists": playlists})
