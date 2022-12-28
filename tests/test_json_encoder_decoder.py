from unittest import TestCase

from encode_decode_executor import EncodeDecodeExecutor
import pytest

from json_encoder_decoder import JsonEncoderDecoder


class JsonBufEncodeDecodeTestCase(TestCase):
    def setUp(self) -> None:
        self.json_buffer_enc_dec = JsonEncoderDecoder()

    def test_encode_hello_with_json(self):
        encoder_decoder = EncodeDecodeExecutor(self.json_buffer_enc_dec)
        msg_dict = {"type": "status",
                    "message_count": 100,
                    "identifier": 1234
                    }
        # JSON encode/decode functions are not implemented yet and expect NotImplementedError raise
        with pytest.raises(NotImplementedError):
            encoder_decoder.encode_hello(msg_dict)

    def test_encode_status_message(self):
        encoder_decoder = EncodeDecodeExecutor(self.json_buffer_enc_dec)
        msg_dict = {"type": "status",
                    "message_count": 100,
                    "identifier": 1234
                    }
        # JSON encode/decode functions are not implemented yet and expect NotImplementedError raise
        with pytest.raises(NotImplementedError):
            encoder_decoder.encode_status(msg_dict)
