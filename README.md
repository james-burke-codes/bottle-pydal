Bottle pyDAL
---------------------------------------------------------------------------

Derived from Martin Mulone's initial version:
https://pypi.python.org/pypi/bottle-web2pydal/

# Install


`pip install bottle_pydal`


# About

Bottle-DAL is a plugin that integrates Web2py DAL Database Abstraction Layer
with your Bottle application. It automatically connects to a database at the
beginning of a request, passes the database handle to the route callback and
closes the connection afterwards.

Note: setting `pool_size=1` or greater will give you significant performance
      gains for DBMSs that support connection pooling.

More information about web2py's pyDAL can be found here:
http://www.web2py.com/books/default/chapter/29/06/the-database-abstraction-layer

And the pyDAL repository is here:
https://github.com/web2py/pydal


# Example

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