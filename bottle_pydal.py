#-*- coding: utf-8 -*-

'''
Bottle-DAL is a plugin that integrates Web2py DAL Database Abstraction Layer
with your Bottle application. It automatically connects to a database at the
beginning of a request, passes the database handle to the route callback and
closes the connection afterwards.

To automatically detect routes that need a database connection, the plugin
searches for route callbacks that require a `db` keyword argument
(configurable) and skips routes that do not. This removes any overhead for
routes that don't need a database connection.

Usage Example::

from bottle import route, view, run, debug, install
from bottle_dal import DALPlugin, Field

def define_tables(db):
    """My tables definitions here"""
    db.define_table('person',Field('name','string'))

install(DALPlugin('sqlite://storage.sqlite',
                  define_tables = lambda db: define_tables(db)))

@route('/')
def index(db):
    """ Index Example """

    if db(db.person.id>0).count()==0:
        db.person.insert(name='James')
        db.person.insert(name='Michael')
        db.person.insert(name='Steve')
        db.person.insert(name='Robert')
        db.commit()

    persons = db(db.person.id>0).select()

    return dict(persons=persons.json())

if __name__ == '__main__':
    debug(True)
    run(host='localhost', port=8080)
'''

__author__ = "Martin Mulone"
__version__ = '0.2.0'
__license__ = 'LGPL v3.0'

### CUT HERE (see setup.py)

from pydal import DAL, Field
from validators import *
from html import *
import inspect
from bottle import HTTPError


class DALPlugin(object):
    ''' This plugin passes an DAL database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made. You can override the database
    settings on a per-route basis. See DAL on www.web2py.com'''

    name = 'dal'

    def __init__(self,
                 daluri='sqlite://storage.sqlite',
                 autocommit=False,
                 pool_size=0, folder=None,
                 db_codec='UTF-8', check_reserved=None,
                 migrate=True, fake_migrate=False,
                 migrate_enabled=True, fake_migrate_all=False,
                 decode_credentials=False, driver_args=None,
                 adapter_args=None, attempts=5, auto_import=False,
                 define_tables=None, bigint_id=False, debug=False,
                 lazy_tables=False, db_uid=None, do_connect=True,
                 after_connection=None, tables=None,
                 ignore_field_case=True, entity_quoting=False,
                 table_hash=None
                 keyword='db'):

        self.daluri = daluri
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

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, DALPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another DAL plugin with "\
                                  "conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        # Override global configuration with route-specific values.
        conf = context['config'].get('dal') or {}
        daluri = conf.get('daluri', self.daluri)
        autocommit = conf.get('autocommit', self.autocommit)
        pool_size = conf.get('pool_size', self.pool_size)
        folder = conf.get('folder', self.folder)
        db_codec = conf.get('db_codec', self.db_codec)
        check_reserved = conf.get('check_reserved', self.check_reserved)
        migrate = conf.get('migrate', self.migrate)
        fake_migrate = conf.get('fake_migrate', self.fake_migrate)
        migrate_enabled = conf.get('migrate_enabled', self.migrate_enabled)
        fake_migrate_all = conf.get('fake_migrate_all', self.fake_migrate_all)
        decode_credentials = conf.get('decode_credentials',
                                                    self.decode_credentials)
        driver_args = conf.get('driver_args', self.driver_args)
        adapter_args = conf.get('adapter_args', self.adapter_args)
        attempts = conf.get('attempts', self.attempts)
        auto_import = conf.get('auto_import', self.auto_import)
        bigint_id = conf.get('bigint_id', self.bigint_id)
        debug = conf.get('debug', self.debug)
        lazy_tables = conf.get('lazy_tables', self.lazy_tables)
        db_uid = conf.get('db_uid', self.db_uid)
        do_connect = conf.get('do_connect', self.do_connect)
        after_connection = conf.get('after_connection', self.after_connection)
        tables = conf.get('tables', self.tables)
        ignore_field_case = conf.get('ignore_field_case', self.ignore_field_case)
        entity_quoting = conf.get('entity_quoting', self.entity_quoting)
        table_hash = conf.get('table_hash', self.table_hash)

        define_tables = conf.get('define_tables', self.define_tables)
        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        args = inspect.getargspec(context['callback'])[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):

            # Connect to the database
            db = DAL(daluri,
                 pool_size=pool_size,
                 folder=folder,
                 db_codec=db_codec,
                 check_reserved=check_reserved,
                 migrate=migrate,
                 fake_migrate=fake_migrate,
                 migrate_enabled=migrate_enabled,
                 fake_migrate_all=fake_migrate_all,
                 decode_credentials=decode_credentials,
                 driver_args=driver_args,
                 adapter_args=adapter_args,
                 attempts=attempts,
                 auto_import=auto_import)

            if define_tables:  # tables definitions
                define_tables(db)

            # Add the connection handle as a keyword argument.
            kwargs[keyword] = db

            try:
                rv = callback(*args, **kwargs)
                if autocommit: db.commit()
            except Exception, e:
                db.rollback()
                raise HTTPError(500, "Database Error", e)

            return rv

        # Replace the route callback with the wrapped one.
        return wrapper


Plugin = DALPlugin