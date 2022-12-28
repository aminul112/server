from abc import ABC, abstractmethod


class BaseEncoderDecoder(ABC):
    @abstractmethod
    def encode_hello(self, msg_dict):
        pass

    @abstractmethod
    def decode_hello(self, binary_data):
        pass

    @abstractmethod
    def encode_status(self, msg_dict):
        pass

    @abstractmethod
    def decode_status(self, binary_data):
        pass
