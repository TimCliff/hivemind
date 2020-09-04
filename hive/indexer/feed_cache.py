"""Maintains feed cache (blogs + reblogs)"""

import logging
import time
from hive.db.adapter import Db
from hive.db.db_state import DbState

log = logging.getLogger(__name__)

DB = Db.instance()

class FeedCache:
    """Maintains `hive_feed_cache`, which merges posts and reports.

    The feed cache allows for efficient querying of posts + reblogs,
    savings us from expensive queries. Effectively a materialized view.
    """

    @classmethod
    def insert(cls, post_id, account_id, created_at, block_num):
        """Inserts a [re-]post by an account into feed."""
        assert not DbState.is_initial_sync(), 'writing to feed cache in sync'
        sql = """INSERT INTO hive_feed_cache (account_id, post_id, created_at, block_num)
                      VALUES (:account_id, :id, :created_at, :block_num)
                 ON CONFLICT ON CONSTRAINT hive_feed_cache_ux1 DO NOTHING"""
        DB.query(sql, account_id=account_id, id=post_id, created_at=created_at, block_num=block_num)

    @classmethod
    def delete(cls, post_id, account_id=None):
        """Remove a post from feed cache.

        If `account_id` is specified, we remove a single entry (e.g. a
        singular un-reblog). Otherwise, we remove all instances of the
        post (e.g. a post was deleted; its entry and all reblogs need
        to be removed.
        """
        assert not DbState.is_initial_sync(), 'writing to feed cache in sync'
        sql = "DELETE FROM hive_feed_cache WHERE post_id = :id"
        if account_id:
            sql = sql + " AND account_id = :account_id"
        DB.query(sql, account_id=account_id, id=post_id)

    @classmethod
    def rebuild(cls, truncate=True):
        """Rebuilds the feed cache upon completion of initial sync."""

        log.info("[HIVE] Rebuilding feed cache, this will take a few minutes.")
        DB.query("START TRANSACTION")
        if truncate:
            DB.query("TRUNCATE TABLE hive_feed_cache")

        lap_0 = time.perf_counter()
        # why join with accounts and taking id if author_id exists?
        DB.query("""
            INSERT INTO hive_feed_cache (account_id, post_id, created_at, block_num)
                 SELECT hive_posts.author_id, hive_posts.id, hive_posts.created_at, hive_posts.block_num
                   FROM hive_posts
                  WHERE depth = 0 AND counter_deleted = 0
            ON CONFLICT DO NOTHING
        """)
        lap_1 = time.perf_counter()
        DB.query("""
            INSERT INTO hive_feed_cache (account_id, post_id, created_at, block_num)
                 SELECT hive_accounts.id, post_id, hive_reblogs.created_at, hive_reblogs.block_num
                   FROM hive_reblogs
                   JOIN hive_accounts ON hive_reblogs.account = hive_accounts.name
            ON CONFLICT DO NOTHING
        """)
        lap_2 = time.perf_counter()
        DB.query("COMMIT")

        log.info("[HIVE] Rebuilt hive feed cache in %ds (%d+%d)",
                 (lap_2 - lap_0), (lap_1 - lap_0), (lap_2 - lap_1))
