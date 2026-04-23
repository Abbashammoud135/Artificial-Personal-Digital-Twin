from abc import ABC, abstractmethod

class BaseExtractorTool(ABC):

    @abstractmethod
    def extract(self, input_data):
        pass