# txque: Python Async Background Jobs

This project allows you to run background jobs asynchronously much like Ruby's [Sidekiq](http://sidekiq.org/).  It uses [Python Twisted](http://twistedmatrix.com) to handle thread pooling and all of the magic behind the scenes.

It can currently use the DBAPI modules MySQLdb, psycopg2, and sqlite3 - though new storage methods are easy to add via the dispatcher interface.

## Installation

```bash
pip install txque
```

You'll need to set up a table in your DB for txque to store jobs.  There are files in the db folder to initialize the table needed by txque.  Make sure you run that SQL for your DB first before continuing.


## Usage
Usage is pretty straightforward.  To create a job definition, simply extend the Job class and define a "run" method.

```python
from txque.work import Job

class MyBackgroundJob(Job):
    def run(self, anArgument, akeyword=avalue):
        # Now do some work.  This work can be synchronous, or it can return a deferred.
        someExpensiveFunction(anArgument, akeyword)
```

Then, you can queue a job anywhere you need to:

```python
import sys
from twisted.internet import reactor
from txque.dispatchers.sql import MySQLDispatcher

# create a dispatcher
dispatcher = MySQLDispatcher(user="username", passwd="password", db="txque")

# queue the job, then stop the reactor once queued
d = dispatcher.queue(MyBackgroundJob('hi there'), queue='default', priority=10)
d.addCallback(lambda _: reactor.stop())

# start the reactor to start everything
reactor.run()
```

Then, you can run as many workers as you'd like.  A sample worker application has been included:

```bash
twistd -noy worker.tac
```

You can specify the queue and priority as well:
```bash
TXQUE_QUENAME=myque TXQUE_PRIORITY=5 twistd -noy worker.tac
```

## Errors / Bugs / Contact
See [github](http://github.com/bmuller/txque).
