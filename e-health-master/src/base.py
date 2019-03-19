from abc import abstractmethod, ABC
from src.data_handler import *


class BaseManager(ABC):

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def save_data(self):
        pass


class BaseObject(ABC):

    def get_type(self):
        return self.__class__.__name__

    def data(self):
        result = dict(self.__dict__)
        result['type'] = self.get_type()
        return result

    def __str__(self):
        return str(self.__dict__)