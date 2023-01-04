from abc import ABC, abstractmethod


class BaseEncoderDecoder(ABC):
    @abstractmethod
    def encode_heartbeat(self, msg_dict):
        pass

    @abstractmethod
    def decode_heartbeat(self, binary_data):
        pass

    @abstractmethod
    def encode_status(self, msg_dict):
        pass

    @abstractmethod
    def decode_status(self, binary_data):
        pass
