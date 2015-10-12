# coding: utf-8

from collections import defaultdict
from Queue import Queue, Empty
from threading import Thread

# Definition of the type of events
EVENT_MD_LOGIN = 'md_login'
EVNET_MD_RSPERROR = 'md_error'
EVENT_MD_DATA = 'md_data'

EVENT_TD_LOGIN = 'td_login'
EVENT_TD_SETTLEINFO = 'td_settleinfo'
EVENT_TD_SETTLECONFIRM = 'td_settleconfirm'

class Event(object):
    """
    Definition of a event.
    A event has a type field, a data field, a error field and a state filed.
    """

    def __init__(self, type=None, data=None, error=None, state=None):
        self.type = type
        self.data = data
        self.error = error
        self.state = state

class EventDispatcher(object):
    """
    EventDispatcher handle different kind of event, listener functions can be registered on it
    """

    def __init__(self):
        self.__events = Queue()
        self.__listeners = defaultdict(list)
        self.__active = False
        self.__thread = Thread(target=self.__run)

    def __run(self):
        while self.isActive():
            try:
                event = self.__events.get(block=True)
                self.__process(event)
            except Empty:
                pass

    def __process(self, event):
        if event.type in self.__listeners.keys():
            for listener in self.__listeners[event.type]:
                listener(event)

    def start(self):
        if self.__active == False:
            self.__active = True
            self.__thread.start()

    def stop(self):
        self.__active = False
        self.__thread.join()

    def registerListener(self, event_type, listener):
        self.__listeners[event_type].append(listener)

    def unregisterListener(self, event_type, listener):
        if listener in self.__listeners[event_type]:
            self.__listeners[event_type] = self.__listeners[event_type].remove(listener)

    def put(self, event):
        self.__events.put(event)

    def isActive(self):
        return self.__active



