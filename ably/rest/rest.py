from __future__ import absolute_import

import logging
import types

import requests

from ably.http.http import Http
from ably.rest.auth import Auth
from ably.rest.channel import Channels
from ably.util.exceptions import AblyException, catch_all

log = logging.getLogger(__name__)


class AblyRest(object):
    """Ably Rest Client"""
    def __init__(self, options):
        """Create an AblyRest instance.

        :Parameters:
          **Credentials**
          - `key`: a valid key string

          **Or**
          - `key_id`: Your Ably key id
          - `key_value`: Your Ably key value

          **Optional Parameters**
          - `client_id`: Undocumented
          - `host`: The host to connect to. Defaults to rest.ably.io
          - `port`: The port to connect to. Defaults to 80
          - `tls_port`: The tls_port to connect to. Defaults to 443
          - `tls`: Specifies whether the client should use TLS. Defaults
            to True
          - `auth_token`: Undocumented
          - `auth_callback`: Undocumented
          - `auth_url`: Undocumented
          - `keep_alive`: use persistent connections. Defaults to True
        """

        if options is None:
            msg = "no options provided"
            raise AblyException(msg, 400, 40000)

        self.__client_id = options.client_id

        #if self.__keep_alive:
        #    self.__session = requests.Session()
        #else:
        #    self.__session = None

        self.__http = Http(self, options)
        self.__auth = Auth(self, options)
        self.__http.auth = self.__auth

        self.__channels = Channels(self)

    @classmethod
    def with_key(cls, key):
        return cls(Options.with_key(key))

    def _format_time_param(self, t):
        try:
            return '%d' % (calendar.timegm(t.utctimetuple()) * 1000)
        except:
            return '%s' % t


    @catch_all
    def stats(self, direction=None, start=None, end=None, params=None,
              limit=None, paginated=None, timeout=None):
        """Returns the stats for this application"""
        params = params or {}

        if direction:
            params["direction"] = direction
        if start:
            params["start"] = self._format_time_param(start)
        if end:
            params["end"] = self._format_time_param(end)
        if limit:
            params["limit"] = "%d" % limit

        url = '/stats'
        if params:
            url += '?' + urllib.urlencode(params)

        return PaginatedResult.paginated_query(self.http, url, None, stats_processor)

    @catch_all
    def time(self, timeout=None):
        """Returns the current server time in ms since the unix epoch"""
        r = self.http.get('/time', skip_auth=True, timeout=timeout)
        AblyException.raise_for_response(r)
        return r.json()[0]

    @property
    def client_id(self):
        return self.options.client_id

    @property
    def channels(self):
        """Returns the channels container object"""
        return self.__channels

    @property
    def auth(self):
        return self.__auth

    @property
    def http(self):
        return self.__http
