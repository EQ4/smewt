#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <rikrd@smewt.com>
# Copyright (c) 2008 Nicolas Wack <wackou@smewt.com>
#
# Smewt is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Smewt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import with_statement
from Queue import PriorityQueue
from threading import Thread, Lock, current_thread
import time
import logging

log = logging.getLogger(__name__)

class Task(object):
    def __init__(self, priority = 5):
        self.priority = priority

    def perform(self):
        """All tasks should implement this function, which should perform the actual task.

        No data is passed to this method. All the necessary task data should be given in the constructor.

        This method shouldn't return anything on success, and raise an exception in case of failure.
        It can have side effects though, such as updating the global collection for instance. In this case,
        the collection needs to be passed as argument to the constructor."""
        raise NotImplementedError

class FuncTask(Task):
    def __init__(self, desc, func, *args, **kwargs):
        super(FuncTask, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.description = desc


    def perform(self):
        self.func(*self.args, **self.kwargs)


def worker(taskManager):
    log.debug('Worker thread is: 0x%x' % current_thread().ident)
    while True:
        if taskManager.shouldFinish:
            log.info('Worker thread stopped working because TaskManager should finish now')
            return

        try:
            taskId = taskManager.taskId
            (_, _), task = taskManager.queue.get()
            taskManager.taskId + 1

            # TODO: need to have timeout on the tasks, eg: 5 seconds
            # TODO: need to be able to stop task immediately
            taskManager.taskDesc = task.description
            task.perform()

        except Exception:
            import sys, traceback
            log.warning('TaskManager: task failed with error: %s' % ''.join(traceback.format_exception(*sys.exc_info())))

        finally:
            taskManager.taskDone(taskId)


class TaskManager(object):
    """The TaskManager is a stable priority queue of tasks. It takes them one by one, the
    one with the highest priority first, and call its perform() method, then repeat until no tasks are left.

    If two or more tasks have the same priority, it will take the one that was added first to the queue.

    The TaskManager can be controlled asynchronously, as it runs the tasks in a separate thread."""

    def __init__(self):
        super(TaskManager, self).__init__()

        # our main task queue
        self.queue = PriorityQueue()

        self.taskId = 0    # ID for the next task that will be generated
        self.total = 0     # used to keep track of the total jobs that have been submitted (queue size decreases as we process tasks)
        self.finished = [] # list of task IDs which have finished
        self.taskDesc = '' # description of the task started last

        self.lock = Lock()

        log.debug('Main GUI thread is: 0x%x' % current_thread().ident)

        self.shouldFinish = False

        # ideally a pool of threads or sth like TBB or ThreadWeaver
        self.workerThread = Thread(target = worker, args = (self,))
        self.workerThread.daemon = True
        self.workerThread.start()


    def add(self, task):
        log.info('TaskManager add task: %s' % task.description)
        with self.lock:
            # -task.priority because it always gets the lowest one first
            # we need to put the time as well, because Queue uses heap sort which is not stable, so we
            # had to find a way to make it look stable ;-)
            self.queue.put(( (-task.priority, time.time()), task ))
            self.total += 1


    def taskDone(self, taskId):
        with self.lock:
            self.finished.append(taskId)

            log.info('Task %d/%d completed!' % (len(self.finished), self.total))

            # if we finished all the tasks, reset the current total
            if self.queue.empty():
                self.finished = []
                self.total = 0

            self.queue.task_done()

    def finishNow(self):
        log.info('TaskManager should finish ASAP, waiting for currently running tasks to finish')
        self.shouldFinish = True
        with self.lock:
            if self.total == 0:
                # worker thread is already waiting on an empty queue, we can't wait for him
                log.info('No currently running jobs')
                return

        # FIXME: need to stop worker, we can't always wait for it
        self.workerThread.join()

        log.info('TaskManager: last running task finished')
