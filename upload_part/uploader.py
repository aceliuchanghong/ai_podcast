import abc
import os


class Upload(abc.ABC):
    def __init__(self):
        self.tail = os.getenv("tail")

    @abc.abstractmethod
    def upload_video(self, *args, **kwargs):
        pass
