import logging

from base_enc_dec import BaseEncoderDecoder

log = logging.getLogger(__name__)


class JsonEncoderDecoder(BaseEncoderDecoder):
    def encode_hello(self, msg_dict):
        raise NotImplementedError("JSON encode_hello will be implemented in future")

    def decode_hello(self, binary_data):
        raise NotImplementedError("JSON decode_hello will be implemented in future")

    def encode_status(self, msg_dict):
        raise NotImplementedError("JSON encode_status will be implemented in future")

    def decode_status(self, binary_data):
        raise NotImplementedError("JSON decode_status will be implemented in future")
