#-*- coding: utf-8 -*-

__author__ = "James P Burke"
__version__ = '0.2.4'
__license__ = 'LGPL v3.0'

### CUT HERE (see setup.py)

import inspect
import logging
from pydal import DAL, Field
from bottle import HTTPError

logger = logging.getLogger(__name__)

class DALPlugin(object):
    ''' This plugin passes an DAL database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made.'''

    name = 'pydal'
    api = 2

    def __init__(self,
                 uri='sqlite://storage.sqlite',
                 autocommit=False,
                 pool_size=0, folder=None,
                 db_codec='UTF-8', check_reserved=None,
                 migrate=False, fake_migrate=False,
                 migrate_enabled=False, fake_migrate_all=False,
                 decode_credentials=False, driver_args=None,
                 adapter_args=None, attempts=5, auto_import=False,
                 define_tables=None, bigint_id=False, debug=False,
                 lazy_tables=False, db_uid=None, do_connect=True,
                 after_connection=None, tables=None,
                 ignore_field_case=True, entity_quoting=False,
                 table_hash=None,
                 keyword='db'):

        self.uri = uri
        self.autocommit = autocommit
        self.pool_size = pool_size
        self.folder = folder
        self.db_codec = db_codec
        self.check_reserved = check_reserved
        self.migrate = migrate
        self.fake_migrate = fake_migrate
        self.migrate_enabled = migrate_enabled
        self.fake_migrate_all = fake_migrate_all
        self.decode_credentials = decode_credentials
        self.driver_args = driver_args
        self.adapter_args = adapter_args
        self.attempts = attempts
        self.auto_import = auto_import
        self.bigint_id = bigint_id
        self.debug = debug
        self.lazy_tables = lazy_tables
        self.db_uid = db_uid
        self.do_connect = do_connect
        self.after_connection = after_connection
        self.tables = tables
        self.ignore_field_case = ignore_field_case
        self.entity_quoting = entity_quoting
        self.table_hash = table_hash

        self.define_tables = define_tables
        self.keyword = keyword
        self.db = None

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, DALPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another DAL plugin with "\
                                  "conflicting settings (non-unique keyword).")

        # Connect to the database
        if self.pool_size:
            self._connect()
        

    def apply(self, callback, context):
        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        conf = context.config.get('db') or {}
        args = context.get_callback_args()

        if self.keyword not in args:
            return callback

        def wrapper(*args, **kwargs):

            # Connect to the database
            if not self.pool_size:
                self._connect()

            # Add the connection handle as a keyword argument.
            kwargs[self.keyword] = self.db

            try:
                rv = callback(*args, **kwargs)
                if self.autocommit: self.db.commit()
            except Exception as e:
                logger.error(e, exc_info=True)
                self.db.rollback()
                raise HTTPError(500, "Database Error", e)

            return rv

        # Replace the route callback with the wrapped one.
        return wrapper

    def _connect(self):
        self.db = DAL(self.uri,
             pool_size=self.pool_size,
             folder=self.folder,
             db_codec=self.db_codec,
             check_reserved=self.check_reserved,
             migrate=self.migrate,
             fake_migrate=self.fake_migrate,
             migrate_enabled=self.migrate_enabled,
             fake_migrate_all=self.fake_migrate_all,
             decode_credentials=self.decode_credentials,
             driver_args=self.driver_args,
             adapter_args=self.adapter_args,
             attempts=self.attempts,
             auto_import=self.auto_import,
             bigint_id=self.bigint_id,
             debug=self.debug,
             lazy_tables=self.lazy_tables,
             db_uid=self.db_uid,
             do_connect=self.do_connect,
             after_connection=self.after_connection,
             tables=self.tables,
             ignore_field_case=self.ignore_field_case,
             entity_quoting=self.entity_quoting,
             table_hash=self.table_hash
             )

        if self.define_tables:  # tables definitions
            self.define_tables(self.db)

Plugin = DALPlugin