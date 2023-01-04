import logging

from base_enc_dec import BaseEncoderDecoder

log = logging.getLogger(__name__)


class JsonEncoderDecoder(BaseEncoderDecoder):
    def encode_heartbeat(self, msg_dict):
        raise NotImplementedError("JSON encode_heartbeat will be implemented in future")

    def decode_heartbeat(self, binary_data):
        raise NotImplementedError("JSON decode_heartbeat will be implemented in future")

    def encode_status(self, msg_dict):
        raise NotImplementedError("JSON encode_status will be implemented in future")

    def decode_status(self, binary_data):
        raise NotImplementedError("JSON decode_status will be implemented in future")
