import logging

from base_enc_dec import BaseEncoderDecoder
import messages_pb2 as messages
log = logging.getLogger(__name__)

class ProtobufEncoderDecoder(BaseEncoderDecoder):
    def encode_hello(self, msg_dict):
        proto_message = messages.HelloMessage()
        proto_message.type = msg_dict.get("type")
        proto_message.msg = msg_dict.get("msg")
        proto_message.client_host = msg_dict.get("client_host")
        proto_message.identifier = int(msg_dict.get("identifier"))
        proto_message.client_port = int(msg_dict.get("client_port"))
        return proto_message.SerializeToString()  # serialize

    def decode_hello(self, binary_data):
        proto_message = messages.HelloMessage()
        deserialized = proto_message.FromString(binary_data)  # deserialize, input will be bytes
        log.info(f"Desrialized = {deserialized}")
        return {
            "type": deserialized.type,
            "msg": deserialized.msg,
            "client_host": deserialized.client_host,
            "identifier": deserialized.identifier,
            "client_port": deserialized.client_port,
        }

    def encode_status(self, msg_dict):
        proto_message = messages.StatusMessage()
        proto_message.type = msg_dict.get("type")
        proto_message.identifier = int(msg_dict.get("identifier"))
        proto_message.message_count = int(msg_dict.get("message_count"))
        return proto_message.SerializeToString()  # serialize

    def decode_status(self, binary_data):
        proto_message = messages.StatusMessage()
        deserialized = proto_message.FromString(binary_data)  # deserialize, input will be bytes
        log.info(f"Desrialized = {deserialized}")
        return {
            "type": deserialized.type,
            "message_count": deserialized.message_count,
            "identifier": deserialized.identifier,
        }


