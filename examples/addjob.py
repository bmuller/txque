import sys
from twisted.internet import reactor
from twisted.python import log
log.startLogging(sys.stdout)

from txque.dispatchers.sql import MySQLDispatcher
from txque.work import Job

class SleepyJob(Job):
    def run(self, msg):
        # do something with our arg
        print msg

def done(r):
    print r
    reactor.stop()

dispatcher = MySQLDispatcher(user="root", passwd="", db="txque")
d = dispatcher.queue(SleepyJob('hi there'), queue='default', priority=10)
d.addCallbacks(done, done)
reactor.run()
