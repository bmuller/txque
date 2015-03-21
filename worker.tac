from os import environ
import socket

from twisted.application import service, internet
from twisted.enterprise import adbapi
from twisted.web import server
from twisted.python.logfile import LogFile
from twisted.python.log import ILogObserver

from txque.work import Job, Worker
from txque.dispatchers.sql import MySQLDispatcher

import sys, os
sys.path.append(os.path.dirname(__file__))

# Application set up
application = service.Application("txque worker")

quename = environ.get('TXQUE_QUENAME', 'default')
priority = environ.get('TXQUE_PRIORITY', 0)

dispatcher = MySQLDispatcher(user="root", passwd="", db="txque")
service = Worker(dispatcher, queue=quename, priority=priority)
service.setServiceParent(application)
