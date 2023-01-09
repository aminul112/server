import logging

from base_enc_dec import BaseEncoderDecoder
import messages_pb2 as messages

log = logging.getLogger("__main__." + __name__)


class ProtobufEncoderDecoder(BaseEncoderDecoder):
    def encode_heartbeat(self, msg_dict: dict) -> bytes:
        """
        Serialize a heartbeat message.
        :param msg_dict: the data to serialize
        :return: binary string format data.
        """
        try:
            proto_message = messages.HeartBeatMessage()
            proto_message.type = msg_dict.get("type")
            proto_message.msg = msg_dict.get("msg")
            proto_message.client_host = msg_dict.get("client_host")
            proto_message.identifier = int(msg_dict.get("identifier"))
            proto_message.client_port = int(msg_dict.get("client_port"))
            return proto_message.SerializeToString()  # serialize
        except TypeError as e:
            log.error(f"encode_heartbeat exception happened")
            proto_message = messages.ErrorMessage()
            proto_message.type = messages.MessageType.MESSAGE_TYPE_ERROR
            proto_message.error = str(e)
            return proto_message.SerializeToString()  # serialize

    def decode_heartbeat(self, binary_data):
        """
        Deserialize binary data for a heartbeat message.
        :param binary_data: the data to deserialize.
        :return: a decoded dict format message.
        """
        proto_message = messages.HeartBeatMessage()
        deserialized = proto_message.FromString(
            binary_data
        )  # deserialize, input will be bytes
        if deserialized.type == messages.MessageType.MESSAGE_TYPE_HEARTBEAT:
            return {
                "type": deserialized.type,
                "msg": deserialized.msg,
                "client_host": deserialized.client_host,
                "identifier": deserialized.identifier,
                "client_port": deserialized.client_port,
            }
        else:
            log.error(f"decode_heartbeat exception happened")
            return {
                "type": messages.MessageType.MESSAGE_TYPE_ERROR,
                "msg": "incorrect decoder",
            }

    def encode_status(self, msg_dict: dict) -> bytes:
        """
        Serialize a status message.
        :param msg_dict: the data to serialize
        :return: binary string format data.
        """
        try:
            proto_message = messages.StatusMessage()
            proto_message.type = msg_dict.get("type")
            proto_message.identifier = int(msg_dict.get("identifier"))
            proto_message.message_count = int(msg_dict.get("message_count"))
            return proto_message.SerializeToString()  # serialize
        except TypeError as e:
            log.error(f"encode_status exception happened")
            proto_message = messages.ErrorMessage()
            proto_message.type = messages.MessageType.MESSAGE_TYPE_ERROR
            proto_message.error = str(e)
            return proto_message.SerializeToString()  # serialize

    def decode_status(self, binary_data: bytes) -> dict:
        """
        Deserialize binary data for a status message.
        :param binary_data: the data to deserialize.
        :return: a decoded dict format message.
        """
        proto_message = messages.StatusMessage()
        deserialized = proto_message.FromString(
            binary_data
        )  # deserialize, input will be bytes
        if deserialized.type == messages.MessageType.MESSAGE_TYPE_STATUS:
            return {
                "type": deserialized.type,
                "message_count": deserialized.message_count,
                "identifier": deserialized.identifier,
            }
        else:
            log.error(f"decode_status exception happened")
            return {
                "type": messages.MessageType.MESSAGE_TYPE_ERROR,
                "msg": "incorrect decoder",
            }
