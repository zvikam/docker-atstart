import sys
import docker

def start ( cli, event ):
    """ handle 'start' events"""
    dest = '/tmp/monitoring'
    source = 'monitor.tar'
    command = dest+'/register.sh'
    # read tar file into memory
    f = open(source, 'rb')
    filedata = f.read()
    # execute (1) : "mkdir -p /tmp/monitoring"
    exe = cli.exec_create( container=event['id'], 
                           cmd='mkdir -p '+dest )
    cli.exec_start( exec_id=exe )
    # copy and extract tar file into container
    cli.put_archive( container=event['id'], 
                     path=dest, 
                     data=filedata )
    # execute (2) : "/tmp/monitoring/register.sh"
    exe = cli.exec_create( container=event['id'], 
                           cmd=command, 
                           stdout=False, stderr=False )
    cli.exec_start( exec_id=exe, detach=True )

thismodule = sys.modules[__name__]
# create a docker client object that talks to the local docker daemon 
cli = docker.Client(base_url='unix://var/run/docker.sock')
# start listening for new events
events = cli.events(decode=True)
# possible events are: 
#  attach, commit, copy, create, destroy, die, exec_create, exec_start, export, 
#  kill, oom, pause, rename, resize, restart, start, stop, top, unpause, update
for event in events:
    # if a handler for this event is defined, call it
    if (hasattr( thismodule , event['Action'])):
        getattr( thismodule , event['Action'])( cli, event )