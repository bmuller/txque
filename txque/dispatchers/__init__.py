from zope.interface import Interface


class IDispatcher(Interface):
    def getJobs(worker, count):
        """
        Get available jobs, if any.  Returns a deferred that will
        call back with a list of jobs (could be empty if none)
        """

    def queue(job, queue='default', priority=10):
        """
        Enqueue a job to run.
        """

    def jobFinished(worker, job):
        """
        Remove a job from storage because it finished.
        """

    def jobErrored(worker, job):
        """
        Update a job status to indicate it errored out.
        """
