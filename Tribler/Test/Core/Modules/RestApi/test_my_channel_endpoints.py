import os
import json

from Tribler.Core.Modules.channel.channel import ChannelObject
from Tribler.Core.Modules.channel.channel_manager import ChannelManager
from Tribler.Core.Utilities.twisted_thread import deferred
from Tribler.Core.simpledefs import NTFY_CHANNELCAST
from Tribler.Core.exceptions import DuplicateChannelNameError
from Tribler.Test.Core.Modules.RestApi.base_api_test import AbstractApiTest
from Tribler.Test.test_as_server import TESTS_DATA_DIR


class ChannelCommunityMock(object):

    def __init__(self, channel_id, name, description, mode):
        self.cid = 'a' * 20
        self._channel_id = channel_id
        self._channel_name = name
        self._channel_description = description
        self._channel_mode = mode

    def get_channel_id(self):
        return self._channel_id

    def get_channel_name(self):
        return self._channel_name

    def get_channel_description(self):
        return self._channel_description

    def get_channel_mode(self):
        return self._channel_mode


class AbstractTestMyChannelEndpoints(AbstractApiTest):

    def setUp(self, autoload_discovery=True):
        super(AbstractTestMyChannelEndpoints, self).setUp(autoload_discovery)
        self.channel_db_handler = self.session.open_dbhandler(NTFY_CHANNELCAST)

    def create_my_channel(self, name, description):
        """
        Utility method to create your channel
        """
        self.channel_db_handler._get_my_dispersy_cid = lambda: "myfakedispersyid"
        self.channel_db_handler.on_channel_from_dispersy('fakedispersyid', None, name, description)
        return self.channel_db_handler.getMyChannelId()

    def create_fake_channel(self, name, description, mode=u'closed'):
        # Use a fake ChannelCommunity object (we don't actually want to create a Dispersy community)
        my_channel_id = self.create_my_channel(name, description)
        self.session.lm.channel_manager = ChannelManager(self.session)

        channel_obj = ChannelObject(self.session, ChannelCommunityMock(my_channel_id, name, description, mode))
        self.session.lm.channel_manager._channel_list.append(channel_obj)
        return my_channel_id

    def create_fake_channel_with_existing_name(self, name, description, mode=u'closed'):
        raise DuplicateChannelNameError(u"Channel name already exists: %s" % name)

    def insert_torrents_into_my_channel(self, torrent_list):
        self.channel_db_handler.on_torrents_from_dispersy(torrent_list)


class TestMyChannelEndpoints(AbstractTestMyChannelEndpoints):

    @deferred(timeout=10)
    def test_my_channel_unknown_endpoint(self):
        """
        Testing whether the API returns an error if an unknown endpoint is queried
        """
        self.should_check_equality = False
        return self.do_request('mychannel/thisendpointdoesnotexist123', expected_code=404)

    @deferred(timeout=10)
    def test_my_channel_endpoint_create(self):
        """
        Testing whether the API returns the right JSON data if a channel is created
        """

        def verify_channel_created(body):
            channel_obj = self.session.lm.channel_manager._channel_list[0]
            self.assertEqual(channel_obj.name, post_data["name"])
            self.assertEqual(channel_obj.description, post_data["description"])
            self.assertEqual(channel_obj.mode, post_data["mode"])
            self.assertDictEqual(json.loads(body), {"added": channel_obj.channel_id})

        post_data = {
            "name": "John Smit's channel",
            "description": "Video's of my cat",
            "mode": "semi-open"
        }
        self.session.create_channel = self.create_fake_channel
        self.should_check_equality = False
        return self.do_request('mychannel', expected_code=200, expected_json=None,
                               request_type='PUT', post_data=post_data).addCallback(verify_channel_created)

    @deferred(timeout=10)
    def test_my_channel_endpoint_create_default_mode(self):
        """
        Testing whether the API returns the right JSON data if a channel is created
         """

        def verify_channel_created(body):
            channel_obj = self.session.lm.channel_manager._channel_list[0]
            self.assertEqual(channel_obj.name, post_data["name"])
            self.assertEqual(channel_obj.description, post_data["description"])
            self.assertEqual(channel_obj.mode, u'closed')
            self.assertDictEqual(json.loads(body), {"added": channel_obj.channel_id})

        post_data = {
            "name": "John Smit's channel",
            "description": "Video's of my cat"
        }
        self.session.create_channel = self.create_fake_channel
        self.should_check_equality = False
        return self.do_request('mychannel', expected_code=200, expected_json=None,
                               request_type='PUT', post_data=post_data).addCallback(verify_channel_created)

    @deferred(timeout=10)
    def test_my_channel_endpoint_create_duplicate_name_error(self):
        """
        Testing whether the API returns a formatted 500 error if DuplicateChannelNameError is raised
        """

        def verify_error_message(body):
            error_response = json.loads(body)
            expected_response = {
                u"error": {
                    u"handled": True,
                    u"code": u"DuplicateChannelNameError",
                    u"message": u"Channel name already exists: %s" % post_data["name"]
                }
            }
            self.assertDictContainsSubset(expected_response[u"error"], error_response[u"error"])

        post_data = {
            "name": "John Smit's channel",
            "description": "Video's of my cat",
            "mode": "semi-open"
        }
        self.session.create_channel = self.create_fake_channel_with_existing_name
        self.should_check_equality = False
        return self.do_request('mychannel', expected_code=500, expected_json=None, request_type='PUT',
                               post_data=post_data).addCallback(verify_error_message)

    @deferred(timeout=10)
    def test_my_channel_endpoint_create_no_name_param(self):
        """
        Testing whether the API returns a 400 and error if the name parameter is not passed
        """
        post_data = {
            "description": "Video's of my cat",
            "mode": "semi-open"
        }
        expected_json = {"error": "name parameter missing"}
        return self.do_request('mychannel', expected_code=400, expected_json=expected_json, request_type='PUT',
                               post_data=post_data)

    @deferred(timeout=10)
    def test_my_channel_endpoint_create_no_description_param(self):
        """
        Testing whether the API returns a 400 and error if the name parameter is not passed
        """
        post_data = {
            "name": "John Smit's channel",
            "mode": "semi-open"
        }
        expected_json = {"error": "description parameter missing"}
        return self.do_request('mychannel', expected_code=400, expected_json=expected_json, request_type='PUT',
                               post_data=post_data)

    @deferred(timeout=10)
    def test_my_channel_overview_endpoint_no_my_channel(self):
        """
        Testing whether the API returns response code 404 if no channel has been created
        """
        return self.do_request('mychannel', expected_code=404)

    @deferred(timeout=10)
    def test_my_channel_overview_endpoint_with_channel(self):
        """
        Testing whether the API returns the right JSON data if a channel overview is requested
        """
        channel_json = {u'overview': {u'name': u'testname', u'description': u'testdescription',
                                      u'identifier': 'fakedispersyid'.encode('hex')}}
        self.create_my_channel(channel_json[u'overview'][u'name'], channel_json[u'overview'][u'description'])

        return self.do_request('mychannel', expected_code=200, expected_json=channel_json)

    @deferred(timeout=10)
    def test_my_channel_torrents_endpoint_no_my_channel(self):
        """
        Testing whether the API returns response code 404 if no channel has been created when fetching torrents
        """
        return self.do_request('mychannel/torrents', expected_code=404)

    @deferred(timeout=10)
    def test_torrents_endpoint_with_channel(self):
        """
        Testing whether the API returns the right JSON data if a torrents from a channel are fetched
        """

        def verify_torrents_json(body):
            torrents_dict = json.loads(body)
            self.assertTrue(torrents_dict["torrents"])
            self.assertEqual(len(torrents_dict["torrents"]), 1)

        self.should_check_equality = False
        my_channel_id = self.create_my_channel("my channel", "this is a short description")
        torrent_list = [[my_channel_id, 1, 1, ('a' * 40).decode('hex'), 1460000000, "ubuntu-torrent.iso", [], []]]
        self.insert_torrents_into_my_channel(torrent_list)

        return self.do_request('mychannel/torrents', expected_code=200).addCallback(verify_torrents_json)

    @deferred(timeout=10)
    def test_rss_feeds_endpoint_no_my_channel(self):
        """
        Testing whether the API returns the right JSON data if no channel has been created when fetching rss feeds
        """
        self.session.lm.channel_manager = ChannelManager(self.session)
        return self.do_request('mychannel/rssfeeds', expected_code=404)


class TestMyChannelTorrentsEndpoint(AbstractTestMyChannelEndpoints):

    torrent_name = u"ubuntu-15.04-desktop-amd64.iso.torrent"
    torrent_path = os.path.join(TESTS_DATA_DIR, torrent_name)
    post_data = {
        "torrentfile": torrent_path,
        "description": torrent_name.replace("-", " ").replace(".iso.torrent", " iso")
    }

    @deferred(timeout=10)
    def test_add_torrent_to_my_channel(self):
        self.create_fake_channel("channel", "")

        def mock_session_function(my_channel_id, torrent_def, extra_info):
            pass

        self.session.add_torrent_def_to_channel = mock_session_function
        expected_json = {"added": True}
        return self.do_request('mychannel/torrents', 200, expected_json, 'PUT', self.post_data)

    @deferred(timeout=10)
    def test_add_torrent_to_my_channel_404(self):
        return self.do_request('mychannel/torrents', 404, None, 'PUT', self.post_data)

    @deferred(timeout=10)
    def test_add_torrent_to_my_channel_missing_parameter(self):
        self.create_fake_channel("channel", "")
        post_data = {"description": "foo"}
        expected_json = {"error": "torrentfile parameter missing"}
        return self.do_request('mychannel/torrents', 400, expected_json, 'PUT', post_data)

    @deferred(timeout=10)
    def test_add_torrent_to_my_channel_no_description(self):
        def mock_session_function(my_channel_id, torrent_def, extra_info):
            pass

        self.session.add_torrent_def_to_channel = mock_session_function
        self.create_fake_channel("channel", "")
        post_data = {"torrentfile": self.torrent_path}
        expected_json = {"added": True}
        return self.do_request('mychannel/torrents', 200, expected_json, 'PUT', post_data)

    @deferred(timeout=10)
    def test_add_torrent_to_my_channel_missing_torrentfile(self):
        self.create_fake_channel("channel", "")

        def verify_error_message(body):
            error_response = json.loads(body)
            expected_response = {
                u"error": {
                    u"handled": True,
                    u"code": u"IOError",
                    u"message": u"No such file or directory"
                }
            }
            self.assertDictContainsSubset(expected_response[u"error"], error_response[u"error"])

        post_data = {
            "torrentfile": "fake.torrent"
        }
        self.should_check_equality = False
        return self.do_request('mychannel/torrents', 500, None, 'PUT', post_data).addCallback(verify_error_message)

    @deferred(timeout=10)
    def test_add_torrent_to_my_channel_duplicate_torrent(self):
        self.create_fake_channel("channel", "")

        def mock_has_torrent(my_channel_id, infohash):
            return True

        self.channel_db_handler.hasTorrent = mock_has_torrent

        def verify_error_message(body):
            error_response = json.loads(body)
            expected_response = {
                u"error": {
                    u"handled": True,
                    u"code": u"DuplicateTorrentFileError",
                    u"message": u"Torrent file already added: %s" % self.post_data["torrentfile"]
                }
            }
            self.assertDictContainsSubset(expected_response[u"error"], error_response[u"error"])

        self.should_check_equality = False
        return self.do_request('mychannel/torrents', 500, None, 'PUT', self.post_data).addCallback(verify_error_message)


class TestMyChannelRssEndpoints(AbstractTestMyChannelEndpoints):

    @deferred(timeout=10)
    def test_rss_feeds_endpoint_with_channel(self):
        """
        Testing whether the API returns the right JSON data if a rss feeds from a channel are fetched
        """
        expected_json = {u'rssfeeds': [{u'url': u'http://test1.com/feed.xml'}, {u'url': u'http://test2.com/feed.xml'}]}
        channel_name = "my channel"
        self.create_fake_channel(channel_name, "this is a short description")
        channel_obj = self.session.lm.channel_manager.get_channel(channel_name)
        for rss_item in expected_json[u'rssfeeds']:
            channel_obj.create_rss_feed(rss_item[u'url'])

        return self.do_request('mychannel/rssfeeds', expected_code=200, expected_json=expected_json)

    @deferred(timeout=10)
    def test_add_rss_feed_no_my_channel(self):
        """
        Testing whether the API returns a 404 if no channel has been created when adding a rss feed
        """
        self.session.lm.channel_manager = ChannelManager(self.session)
        return self.do_request('mychannel/rssfeeds/http%3A%2F%2Frssfeed.com%2Frss.xml',
                               expected_code=404, request_type='PUT')

    @deferred(timeout=10)
    def test_add_rss_feed_conflict(self):
        """
        Testing whether the API returns error 409 if a channel the rss feed already exists
        """
        expected_json = {"error": "this rss feed already exists"}
        my_channel_id = self.create_fake_channel("my channel", "this is a short description")
        channel_obj = self.session.lm.channel_manager.get_my_channel(my_channel_id)
        channel_obj.create_rss_feed("http://rssfeed.com/rss.xml")

        return self.do_request('mychannel/rssfeeds/http%3A%2F%2Frssfeed.com%2Frss.xml', expected_code=409,
                               expected_json=expected_json, request_type='PUT')

    @deferred(timeout=10)
    def test_add_rss_feed_with_channel(self):
        """
        Testing whether the API returns a 200 if a channel has been created and when adding a rss feed
        """

        def verify_rss_added(_):
            channel_obj = self.session.lm.channel_manager.get_my_channel(my_channel_id)
            self.assertEqual(channel_obj.get_rss_feed_url_list(), ["http://rssfeed.com/rss.xml"])

        expected_json = {"added": True}
        my_channel_id = self.create_fake_channel("my channel", "this is a short description")
        return self.do_request('mychannel/rssfeeds/http%3A%2F%2Frssfeed.com%2Frss.xml', expected_code=200,
                               expected_json=expected_json, request_type='PUT')\
            .addCallback(verify_rss_added)

    @deferred(timeout=10)
    def test_remove_rss_feed_no_channel(self):
        """
        Testing whether the API returns a 404 if no channel has been created when adding a rss feed
        """
        self.session.lm.channel_manager = ChannelManager(self.session)
        return self.do_request('mychannel/rssfeeds/http%3A%2F%2Frssfeed.com%2Frss.xml',
                               expected_code=404, request_type='DELETE')

    @deferred(timeout=10)
    def test_remove_rss_feed_invalid_url(self):
        """
        Testing whether the API returns a 404 and error if the url parameter does not exist in the existing feeds
        """
        expected_json = {"error": "this url is not added to your RSS feeds"}
        self.create_fake_channel("my channel", "this is a short description")
        return self.do_request('mychannel/rssfeeds/http%3A%2F%2Frssfeed.com%2Frss.xml', expected_code=404,
                               expected_json=expected_json, request_type='DELETE')

    @deferred(timeout=10)
    def test_remove_rss_feed_with_channel(self):
        """
        Testing whether the API returns a 200 if a channel has been created and when removing a rss feed
        """
        def verify_rss_removed(_):
            channel_obj = self.session.lm.channel_manager.get_my_channel(my_channel_id)
            self.assertEqual(channel_obj.get_rss_feed_url_list(), [])

        expected_json = {"removed": True}
        my_channel_id = self.create_fake_channel("my channel", "this is a short description")
        channel_obj = self.session.lm.channel_manager.get_my_channel(my_channel_id)
        channel_obj.create_rss_feed("http://rssfeed.com/rss.xml")

        return self.do_request('mychannel/rssfeeds/http%3A%2F%2Frssfeed.com%2Frss.xml', expected_code=200,
                               expected_json=expected_json, request_type='DELETE').addCallback(verify_rss_removed)

    @deferred(timeout=10)
    def test_recheck_rss_feeds_no_channel(self):
        """
        Testing whether the API returns a 404 if no channel has been created when rechecking rss feeds
        """
        self.session.lm.channel_manager = ChannelManager(self.session)
        return self.do_request('mychannel/recheckfeeds', expected_code=404, request_type='POST')

    @deferred(timeout=10)
    def test_recheck_rss_feeds(self):
        """
        Testing whether the API returns a 200 if the rss feeds are rechecked in your channel
        """
        expected_json = {"rechecked": True}
        my_channel_id = self.create_fake_channel("my channel", "this is a short description")
        channel_obj = self.session.lm.channel_manager.get_my_channel(my_channel_id)
        channel_obj._is_created = True
        channel_obj.create_rss_feed("http://rssfeed.com/rss.xml")

        return self.do_request('mychannel/recheckfeeds', expected_code=200,
                               expected_json=expected_json, request_type='POST')


class TestMyChannelPlaylistEndpoints(AbstractTestMyChannelEndpoints):

    def create_playlist(self, channel_id, dispersy_id, peer_id, name, description):
        self.channel_db_handler.on_playlist_from_dispersy(channel_id, dispersy_id, peer_id, name, description)

    def insert_torrent_into_playlist(self, playlist_disp_id, infohash):
        self.channel_db_handler.on_playlist_torrent(42, playlist_disp_id, 42, infohash)

    @deferred(timeout=10)
    def test_get_playlists_endpoint_without_channel(self):
        """
        Testing whether the API returns error 404 if no channel has been created when fetching playlists
        """
        self.should_check_equality = False
        return self.do_request('mychannel/playlists', expected_code=404)

    @deferred(timeout=10)
    def test_playlists_endpoint_no_playlists(self):
        """
        Testing whether the API returns the right JSON data if no playlists have been added to your channel
        """
        self.create_my_channel("my channel", "this is a short description")
        return self.do_request('mychannel/playlists', expected_code=200, expected_json={"playlists": []})

    @deferred(timeout=10)
    def test_playlists_endpoint(self):
        """
        Testing whether the API returns the right JSON data if playlists are fetched
        """
        my_channel_id = self.create_my_channel("my channel", "this is a short description")
        self.create_playlist(my_channel_id, 1234, 42, "test playlist", "test description")
        torrent_list = [[my_channel_id, 1, 1, 'a' * 20, 1460000000, "ubuntu-torrent.iso", [], []]]
        self.insert_torrents_into_my_channel(torrent_list)
        self.insert_torrent_into_playlist(1234, 'a' * 20)

        expected_json = {u"playlists": [{u"id": 1, u"name": u"test playlist", u"description": u"test description",
                                         u"torrents": [{u"infohash": bytes(('a' * 20).encode('hex')),
                                                        u"name": u"ubuntu-torrent.iso"}]}]}
        return self.do_request('mychannel/playlists', expected_code=200, expected_json=expected_json)
