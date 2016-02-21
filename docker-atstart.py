# The MIT License (MIT)
# Copyright (c) 2016 Zvika Meiseles
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import docker
import signal
import argparse
import sys
import fnmatch
import tarfile
import os.path
import tempfile
import mmap

def signal_handler(signal, frame):
    print()
    sys.exit(0)

class eventHandler:
    def __init__ ( self , args ):
        self._cli = docker.Client(base_url='unix://var/run/docker.sock')
        self._args = args;
        self._filedata = None

    def __enter__( self ):
        if ( tarfile.is_tarfile( self._args.source ) ):
            self._f = open(self._args.source, 'rb')
        else:
            fd, self._tar_file = tempfile.mkstemp()
            with tarfile.open( self._tar_file, 'w' ) as out:
                out.add( self._args.source )
            self._f = os.fdopen( fd, 'rb' )
        self._filedata = mmap.mmap( self._f.fileno(), 0, access=mmap.ACCESS_READ )
        if ( not self._filedata ):
            raise ValueError( 'nothing to inject' )
        return self

    def __exit__( self ,type, value, traceback ):
        if ( self._filedata ):
            self._filedata.close()
        if ( self._f ):
            self._f.close()
        if ( self._tar_file ):
            os.remove( self._tar_file )
    
    def run ( self ):
        events = self._cli.events(decode=True)
        for event in events:
            if (hasattr( self , event['Action'])):
                getattr( self , event['Action'])( event )

    def start( self, event ):
        if ( self._args.container ):
            if fnmatch.fnmatch( event['from'], self._args.container ):
                exe = self._cli.exec_create( container=event['id'], cmd='mkdir -p '+self._args.dest )
                self._cli.exec_start( exec_id=exe )
                self._cli.put_archive( container=event['id'], path=self._args.dest, data=self._filedata )
                if ( self._args.command ):
                    exe = self._cli.exec_create( container=event['id'], cmd=self._args.command, stdout=False, stderr=False )
                    self._cli.exec_start( exec_id=exe, detach=True )
                        

signal.signal(signal.SIGINT, signal_handler)

parser = argparse.ArgumentParser()
parser.add_argument("--container", default='*', help="container(s) to inject (wildcards accepted)")
parser.add_argument("--source", help="file/directory to inject")
parser.add_argument("--dest", help="path inside container where the injected files will be placed")
parser.add_argument("command", nargs=argparse.REMAINDER, help="command to run after injection")
args = parser.parse_args()
if ( not args.dest or not args.source ):
    parser.print_help()
    sys.exit(0)
if ( not os.path.exists( args.source ) ):
    print( "source does not exist" )
    sys.exit(0)
with eventHandler( args ) as handler:
    handler.run()
