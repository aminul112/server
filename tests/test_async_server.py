import os
import socket
from unittest import TestCase

from db_operations import AsyncPgPostgresManager
from encode_decode_executor import EncodeDecodeExecutor
from loop_runner import LoopRunner
from protobuf_encode_decoder import ProtobufEncoderDecoder
from server import Server

TESTING_PORT = 8888

import uvloop


class TestServer(TestCase):
    def setUp(self):
        db_host = "0.0.0.0"
        db_user = "devuser"
        password = "devpwd"
        db_name = "devdb"
        db_port = 5432
        self.query_seconds_interval_lower = 10
        self.query_seconds_interval_upper = 20

        self.db_op_manager = AsyncPgPostgresManager(
            user=db_user,
            password=password,
            database_name=db_name,
            db_host=db_host,
            db_port=db_port,
        )

        self.encoder_decoder = EncodeDecodeExecutor(ProtobufEncoderDecoder())

        self.loop = uvloop.new_event_loop()
        self.runner = LoopRunner(self.loop)
        self.runner.start()

    def tearDown(self):
        self.runner.stop()
        self.runner.join()

    def test_async_start_server(self):
        server = Server(
            encoder_decoder=self.encoder_decoder,
            db_op_manager=self.db_op_manager,
            query_seconds_interval_lower=self.query_seconds_interval_lower,
            query_seconds_interval_upper=self.query_seconds_interval_upper,
            server_ip="localhost",
            loop=self.loop,
            server_port=TESTING_PORT,
        )

        self.runner.run_coroutine(server.start_server())

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ("localhost", TESTING_PORT)
        sock.connect(server_address)

        msg = {
            "type": "heartbeat",
            "msg": "First Message",
            "client_host": "localhost",
            "client_port": 1000,
            "identifier": 4567,
        }
        protobuf_binary_data = self.encoder_decoder.encode_heartbeat(msg_dict=msg)
        sock.send(protobuf_binary_data)

        data = sock.recv(1000)
        decoded_data = self.encoder_decoder.decode_heartbeat(binary_data=data)

        self.assertEqual(
            decoded_data,
            {
                "client_host": "localhost",
                "client_port": 1000,
                "identifier": 4567,
                "msg": "ack",
                "type": "heartbeat",
            },
        )

        sock.close()
