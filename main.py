import asyncio
import logging

from db_operations import AsyncPgPostgresManager
from encode_decode_executor import EncodeDecodeExecutor
from protobuf_encode_decoder import ProtobufEncoderDecoder

from dotenv import load_dotenv
import os

from server import Server

load_dotenv()

log = logging.getLogger("server_log")


def main():
    loop = asyncio.get_event_loop()
    db_host = os.getenv("DB_HOST","0.0.0.0")
    db_user = os.getenv("POSTGRES_USER","devuser")
    password = os.getenv("POSTGRES_PASSWORD","devpwd")
    db_name = os.getenv("POSTGRES_DB","devdb")
    db_port = os.getenv("DB_PORT", 5432)


    db_op_manager = AsyncPgPostgresManager(user=db_user, password=password, database_name=db_name, db_host=db_host, db_port=db_port)

    encoder_decoder = EncodeDecodeExecutor(ProtobufEncoderDecoder())
    server = Server(encoder_decoder=encoder_decoder, db_op_manager=db_op_manager)

    server_ip = os.getenv("SERVER_IP")
    server_port = os.getenv("SERVER_PORT")

    if not (server_ip and server_port):
        log.error(".env file must have valid SERVER_IP and SERVER_PORT defined")
        return

    log.info(f"server ip is {server_ip} port is {server_port}")

    f1 = asyncio.start_server(server.accept_client, server_ip, server_port)
    f2 = asyncio.ensure_future(server.send_status_request_to_clients())

    loop.run_until_complete(db_op_manager.query_saved_clients_from_db())

    loop.run_until_complete(f1)
    loop.run_until_complete(f2)
    loop.run_forever()


if __name__ == "__main__":
    logging.basicConfig(filename='log/server.log', encoding='utf-8', level=logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s " + "[%(module)s:%(lineno)d] %(message)s"
    )

    # setup console logging
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)
    main()
