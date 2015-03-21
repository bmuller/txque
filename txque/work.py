import os
import uuid
import json
from inspect import getmodule

from twisted.internet import reactor, defer
from twisted.python import log
from twisted.python.reflect import getClass
from twisted.application import service


class Worker(service.Service):
    _callID = None
    delay = 0.1
    maxDelay = 5
    maxJobs = 20


    def __init__(self, dispatcher, queue='default', priority=0):
        self.priority = priority
        self.queueName = queue
        self.dispatcher = dispatcher
        self.id = "%i:%i" % (uuid.getnode(), os.getpid())
        self.running = False

    def startService(self):
        log.msg("Starting worker %s" % self.id)
        self.running = True
        self.run()

    def stopService(self):
        self.running = False
        if self._callID and not self._callID.called:
            self._callID.cancel()
            self._callID = None

    def run(self):
        log.msg("Requesting jobs.")
        d = self.dispatcher.getJobs(self)
        d.addCallbacks(self._runJobs)

    def _runJobs(self, jobs):
        if not jobs:
            log.msg("No job found.")
            self._schedule(False)

        for job in jobs:
            log.msg("Running job %s." % job)
            d = job.call()
            d.addCallback(self._finishJob, job)
            d.addErrback(self._jobError, job)

    def _jobError(self, error, job):
        log.msg("Job %s had an exception: %s" % (job, error))
        self.dispatcher.jobErrored(self, job, error)
        self._schedule(True)

    def _finishJob(self, result, job):
        log.msg("Job %s finished" % job)
        self.dispatcher.jobFinished(self, job)
        self._schedule(True)

    def _schedule(self, runnow):
        if self._callID and not self._callID.called:
            self._callID.cancel()
            self._callID = None

        if runnow and self.running:
            self.delay = 0.1
            self.run()
        elif self.running:
            self.delay = min(self.delay * 2.7, self.maxDelay)
            self._callID = reactor.callLater(self.delay, self.run)


class Job(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.fullClassName = getmodule(self).__name__ + '.' + getClass(self).__name__
        # used to map this back to storage
        self.dbid = None

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def serialize(self):
        return json.dumps((self.args, self.kwargs))

    @classmethod
    def deserialize(klass, value):
        args, kwargs = json.loads(value)
        return klass(*args, **kwargs)

    def call(self):
        # this will throw an exception if it's the wrong signature
        return defer.maybeDeferred(self.run, *self.args, **self.kwargs)

    def __str__(self):
        args = ", ".join(map(str, self.args))
        kwargs = ", ".join([ "%s=%s" % (k, v) for k, v in self.kwargs.items() ])
        return "%s(%s, %s)" % (getClass(self).__name__, args, kwargs)
