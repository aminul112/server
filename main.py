import asyncio
import logging

from db_operations import AsyncPgPostgresManager
from encode_decode_executor import EncodeDecodeExecutor
from protobuf_encode_decoder import ProtobufEncoderDecoder

from dotenv import load_dotenv
import os

from server import Server

load_dotenv()

log = logging.getLogger()


def main():
    loop = asyncio.get_event_loop()
    db_host = os.getenv("DB_HOST", "0.0.0.0")
    db_user = os.getenv("POSTGRES_USER", "devuser")
    password = os.getenv("POSTGRES_PASSWORD", "devpwd")
    db_name = os.getenv("POSTGRES_DB", "devdb")
    db_port = int(os.getenv("DB_PORT", 5432))
    query_seconds_interval_lower = int(
        os.getenv("QUERY_CLIENTS_INTERVAL_SECONDS_LOWER", 10)
    )
    query_seconds_interval_upper = int(
        os.getenv("QUERY_CLIENTS_INTERVAL_SECONDS_UPPER", 30)
    )

    db_op_manager = AsyncPgPostgresManager(
        user=db_user,
        password=password,
        database_name=db_name,
        db_host=db_host,
        db_port=db_port,
    )
    server_ip = os.getenv("SERVER_IP", "0.0.0.0")
    server_port = int(os.getenv("SERVER_PORT", 4000))

    encoder_decoder = EncodeDecodeExecutor(ProtobufEncoderDecoder())
    server = Server(
        encoder_decoder=encoder_decoder,
        db_op_manager=db_op_manager,
        query_seconds_interval_lower=query_seconds_interval_lower,
        query_seconds_interval_upper=query_seconds_interval_upper,
        server_ip=server_ip,
        server_port=server_port,
    )

    log.info(f"server ip is {server_ip} port is {server_port}")

    # start Async server to handle client requests.
    f1 = server.start_server()
    f2 = asyncio.ensure_future(server.send_status_request_to_clients())

    loop.run_until_complete(db_op_manager.query_saved_clients_from_db())

    loop.run_until_complete(f1)
    loop.run_until_complete(f2)
    loop.run_forever()


if __name__ == "__main__":
    logging.basicConfig(
        filename="log/server.log", encoding="utf-8", level=logging.DEBUG
    )
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
