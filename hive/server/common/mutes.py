"""List of muted accounts for server process."""

import logging
from time import perf_counter as perf
from urllib.request import urlopen, Request
import ujson as json
from hive.server.common.helpers import valid_account
from hive.db.adapter import Db

log = logging.getLogger(__name__)

GET_BLACKLISTED_ACCOUNTS_SQL = """
WITH blacklisted_users AS (
    SELECT following, 'my_blacklist' AS source FROM hive_follows WHERE follower =
        (SELECT id FROM hive_accounts WHERE name = :observer )
    AND blacklisted
    UNION ALL
    SELECT following, 'my_followed_blacklists' AS source FROM hive_follows WHERE follower IN
    (SELECT following FROM hive_follows WHERE follower =
        (SELECT id FROM hive_accounts WHERE name = :observer )
    AND follow_blacklists) AND blacklisted
    UNION ALL
    SELECT following, 'my_muted' AS source FROM hive_follows WHERE follower =
        (SELECT id FROM hive_accounts WHERE name = :observer )
    AND state = 2
    UNION ALL
    SELECT following, 'my_followed_mutes' AS source FROM hive_follows WHERE follower IN
    (SELECT following FROM hive_follows WHERE follower =
        (SELECT id FROM hive_accounts WHERE name = :observer )
    AND follow_muted) AND state = 2
)
SELECT following, source FROM blacklisted_users
"""

def _read_url(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urlopen(req).read()

class Mutes:
    """Singleton tracking muted accounts."""

    _instance = None
    url = None
    accounts = set() # list/irredeemables
    blist = set() # list/any-blacklist
    blist_map = dict() # cached account-list map
    fetched = None
    all_accounts = dict()

    @classmethod
    def instance(cls):
        """Get the shared instance."""
        assert cls._instance, 'set_shared_instance was never called'
        return cls._instance

    @classmethod
    def set_shared_instance(cls, instance):
        """Set the global/shared instance."""
        cls._instance = instance

    def __init__(self, url, blacklist_api_url):
        """Initialize a muted account list by loading from URL"""
        self.url = url
        self.blacklist_api_url = blacklist_api_url
        if url:
            self.load()

    def load(self):
        """Reload all accounts from irredeemables endpoint and global lists."""
        return
        self.accounts = set(_read_url(self.url).decode('utf8').split())
        jsn = _read_url(self.blacklist_api_url + "/blacklists")
        self.blist = set(json.loads(jsn))
        log.warning("%d muted, %d blacklisted", len(self.accounts), len(self.blist))

        self.all_accounts.clear()
        sql = "select id, name from hive_accounts"
        db = Db.instance()
        sql_result = db.query_all(sql)
        for row in sql_result:
            self.all_accounts[row['id']] = row['name']
        self.fetched = perf()

    @classmethod
    def all(cls):
        """Return the set of all muted accounts from singleton instance."""
        return cls.instance().accounts

    @classmethod
    async def get_blacklists_for_observer(cls, observer=None, context=None):
        """ fetch the list of users that the observer has blacklisted """
        if not observer or not context:
            return {}

        if cls.instance().fetched and (perf() - cls.instance().fetched) > 3600:
            cls.instance().load()

        blacklisted_users = {}

        db = context['db']
        sql = GET_BLACKLISTED_ACCOUNTS_SQL
        sql_result = await db.query_all(sql, observer=observer)
        for row in sql_result:
            account_name = cls.all_accounts[row['following']]
            if account_name not in blacklisted_users:
                blacklisted_users[account_name] = []
            blacklisted_users[account_name].append(row['source'])
        return blacklisted_users

    @classmethod
    def lists(cls, name, rep):
        """Return blacklists the account belongs to."""
        return[]
        assert name
        inst = cls.instance()

        # update hourly
        if perf() - inst.fetched > 3600:
            inst.load()

        if name not in inst.blist and name not in inst.accounts:
            if name in inst.blist_map: #this user was blacklisted, but has been removed from the blacklists since the last check
                inst.blist_map.pop(name)    #so just pop them from the cache
            return []
        else:   # user is on at least 1 list
            blacklists_for_user = []
            if name not in inst.blist_map:  #user has been added to a blacklist since the last check so figure out what lists they belong to
                if name in inst.blist: #blacklisted accounts
                    url = "%s/user/%s" % (inst.blacklist_api_url, name)
                    lists = json.loads(_read_url(url))
                    blacklists_for_user.extend(lists['blacklisted'])

                if name in inst.accounts:   #muted accounts
                    if 'irredeemables' not in blacklists_for_user:
                        blacklists_for_user.append('irredeemables')

            if int(rep) < 1:
                blacklists_for_user.append('reputation-0')  #bad reputation
            if int(rep) == 1:
                blacklists_for_user.append('reputation-1') #bad reputation

            inst.blist_map[name] = blacklists_for_user
            return inst.blist_map[name]
