from datetime import datetime
from zope.interface import implements

from twisted.enterprise import adbapi
from twisted.python import reflect
from twisted.internet import defer

from twistar.registry import Registry
from twistar.dbobject import DBObject

from txque.functools import returner, impartial
from txque.dispatchers import IDispatcher


class TxqueJob(DBObject):
    pass


class SQLDispatcher(object):
    implements(IDispatcher)

    def __init__(self, driver, **kwargs):
        conf = { 'cp_reconnect': True, 'charset': 'utf8' }
        conf.update(kwargs)
        Registry.DBPOOL = adbapi.ConnectionPool(driver, **conf)
        self.dbconfig = Registry.getConfig()

    def queue(self, job, queue='default', priority=10):
        dbjob = TxqueJob()
        dbjob.classname = job.fullClassName
        dbjob.args = job.serialize()
        dbjob.queue = queue
        dbjob.priority = priority
        return dbjob.save()

    def _queueMore(self, worker, need):
        params = { 'running_worker': worker.id }
        query = "running_worker is null and queue = ? and priority >= ?"
        where = [ query, worker.queueName, worker.priority]
        return self.dbconfig.update("txque_jobs", params, where=where, limit=need)

    def _preprocessJobs(self, dbjobs, worker):
        # convert TxqueJob's to Job's
        jobs = []
        ids = []
        for dbjob in dbjobs:
            klass = reflect.namedAny(dbjob.classname)
            job = klass.deserialize(dbjob.args)
            job.dbid = dbjob.id
            ids.append(str(dbjob.id))
            jobs.append(job)

        if jobs:
            where = ['id in (%s)' % ",".join(ids)]
            d = self.dbconfig.update("txque_jobs", {'worker_started': datetime.now()}, where=where)
            return d.addCallback(returner(jobs))
        return defer.succeed([])

    def getJobs(self, worker):
        def testMore(jobs):
            need = worker.maxJobs - len(jobs)
            if need > 0:
                d = self._queueMore(worker, need)
                d.addCallback(impartial(self._getJobs, worker))
                return d.addCallback(self._preprocessJobs, worker)
            return self._preprocessJobs(jobs, worker)
        return self._getJobs(worker).addCallback(testMore)

    def _getJobs(self, worker):
        where = ['running_worker = ? AND worker_started is NULL AND error is NULL', worker.id]
        return TxqueJob.find(where=where, limit=worker.maxJobs)

    def jobFinished(self, worker, job):
        return TxqueJob.deleteAll(where=['id = ?', job.dbid])

    def jobErrored(self, worker, job, error):
        def setError(dbjob):
            dbjob.error = "Issue running %s: %s" % (job, error)
            return dbjob.save()
        return TxqueJob.find(job.dbid).addCallback(setError)


class MySQLDispatcher(SQLDispatcher):
    def __init__(self, **kwargs):
        super(MySQLDispatcher, self).__init__('MySQLdb', **kwargs)
