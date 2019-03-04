import abc

class Database(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def initialise(self, settings):
        raise NotImplementedError("must define initialise() to use this base class")

    @abc.abstractmethod
    def all(self):
        raise NotImplementedError("must define all() to use this base class")

    @abc.abstractmethod
    def exists(self, record):
        raise NotImplementedError("must define exists() to use this base class")

    @abc.abstractmethod
    def save(self, record):
        raise NotImplementedError("must define save() to use this base class")

    @abc.abstractmethod
    def top(self, num_items):
        raise NotImplementedError("must define get_top_records() to use this base class")

    @abc.abstractmethod
    def remove(self, record):
        raise NotImplementedError("must define remove() to use this base class")
