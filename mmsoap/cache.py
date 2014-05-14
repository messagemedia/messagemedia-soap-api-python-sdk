# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )
#
# Modified by: Jordan Trudgett ( jordan.trudgett@messagemedia.com.au )

"""
Modifies the SUDS FileCache class to allow it to work on Windows.
"""

import os
from tempfile import gettempdir as tmp
from datetime import datetime as dt
from datetime import timedelta

import suds

try:
    import cPickle as pickle
except:
    import pickle


class ExtendedFileCache(suds.cache.Cache):
    """
    A file-based URL cache.
    @cvar fnprefix: The file name prefix.
    @type fnsuffix: str
    @ivar duration: The cached file duration which defines how
        long the file will be cached.
    @type duration: (unit, value)
    @ivar location: The directory for the cached files.
    @type location: str
    """
    fnprefix = 'suds'
    units = ('months', 'weeks', 'days', 'hours', 'minutes', 'seconds')

    def __init__(self, location=None, **duration):
        """
        @param location: The directory for the cached files.
        @type location: str
        @param duration: The cached file duration which defines how
            long the file will be cached.  A duration=0 means forever.
            The duration may be: (months|weeks|days|hours|minutes|seconds).
        @type duration: {unit:value}
        """
        if location is None:
            location = os.path.join(tmp(), 'suds')
        self.location = location
        self.duration = (None, 0)
        self.setduration(**duration)
        self.checkversion()

    def fnsuffix(self):
        """
        Get the file name suffix
        @return: The suffix
        @rtype: str
        """
        return 'gcf'

    def setduration(self, **duration):
        """
        Set the caching duration which defines how long the
        file will be cached.
        @param duration: The cached file duration which defines how
            long the file will be cached.  A duration=0 means forever.
            The duration may be: (months|weeks|days|hours|minutes|seconds).
        @type duration: {unit:value}
        """
        if len(duration) == 1:
            arg = duration.items()[0]
            if not arg[0] in self.units:
                raise Exception('must be: %s' % str(self.units))
            self.duration = arg
        return self

    def setlocation(self, location):
        """
        Set the location (directory) for the cached files.
        @param location: The directory for the cached files.
        @type location: str
        """
        self.location = location

    def mktmp(self):
        """
        Make the I{location} directory if it doesn't already exits.
        """
        try:
            if not os.path.isdir(self.location):
                os.makedirs(self.location)
        except:
            log.debug(self.location, exc_info=1)
        return self

    def put(self, id, bfr):
        try:
            fn = self.__fn(id)
            f = self.open(fn, 'wb')
            f.write(bfr)
            f.close()
            return bfr
        except:
            log.debug(id, exc_info=1)
            return bfr

    def putf(self, id, fp):
        try:
            fn = self.__fn(id)
            f = self.open(fn, 'w')
            f.write(fp.read())
            fp.close()
            f.close()
            return open(fn)
        except:
            log.debug(id, exc_info=1)
            return fp

    def get(self, id):
        try:
            f = self.getf(id)
            bfr = f.read()
            f.close()
            return bfr
        except:
            pass

    def getf(self, id):
        try:
            fn = self.__fn(id)
            self.validate(fn)
            return self.open(fn, 'rb')
        except:
            pass

    def validate(self, fn):
        """
        Validate that the file has not expired based on the I{duration}.
        @param fn: The file name.
        @type fn: str
        """
        if self.duration[1] < 1:
            return
        created = dt.fromtimestamp(os.path.getctime(fn))
        d = {self.duration[0]: self.duration[1]}
        expired = created + timedelta(**d)
        if expired < dt.now():
            log.debug('%s expired, deleted', fn)
            os.remove(fn)

    def clear(self):
        for fn in os.listdir(self.location):
            if os.path.isdir(fn):
                continue
            if fn.startswith(self.fnprefix):
                log.debug('deleted: %s', fn)
                os.remove(os.path.join(self.location, fn))

    def purge(self, id):
        fn = self.__fn(id)
        try:
            os.remove(fn)
        except:
            pass

    def open(self, fn, *args):
        """
        Open the cache file making sure the directory is created.
        """
        self.mktmp()
        return open(fn, *args)

    def checkversion(self):
        path = os.path.join(self.location, 'version')
        try:
            f = self.open(path)
            version = f.read()
            f.close()
            if version != suds.__version__:
                raise Exception()
        except:
            self.clear()
            f = self.open(path, 'w')
            f.write(suds.__version__)
            f.close()

    def __fn(self, id):
        name = id
        suffix = self.fnsuffix()
        fn = '%s-%s.%s' % (self.fnprefix, name, suffix)
        return os.path.join(self.location, fn)


class ExtendedObjectCache(ExtendedFileCache):
    """
    Provides pickled object caching.
    @cvar protocol: The pickling protocol.
    @type protocol: int
    """
    protocol = 2

    def fnsuffix(self):
        return 'px'

    def get(self, id):
        try:
            fp = ExtendedFileCache.getf(self, id)
            if fp is None:
                return None
            else:
                return pickle.load(fp)
        except:
            ExtendedFileCache.purge(self, id)

    def put(self, id, object):
        bfr = pickle.dumps(object, self.protocol)
        ExtendedFileCache.put(self, id, bfr)
        return object
