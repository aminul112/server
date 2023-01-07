import asyncio
import logging
import random

from db_operations import AsyncPgPostgresManager
from encode_decode_executor import EncodeDecodeExecutor


log = logging.getLogger('__main__.' + __name__)

clients = {}
active_clients = {}


class Server:
    def __init__(
        self,
        encoder_decoder: EncodeDecodeExecutor,
        db_op_manager: AsyncPgPostgresManager,
    ):
        self.encoder_decoder = encoder_decoder
        self.db_op_manager = db_op_manager

    def accept_client(
        self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter
    ):
        task = asyncio.Task(self.handle_client(client_reader, client_writer))
        clients[task] = (client_reader, client_writer)

        def client_disconnected(task_del):
            del clients[task_del]
            client_writer.close()
            log.info("client disconnected")

        log.info("client connected")
        task.add_done_callback(client_disconnected)

    async def send_a_message_to_client(self, host: str, port: int, msg: dict):
        try:
            log.info(f"send_a_message_to_client host{host} port{port} ")

            client_reader, client_writer = await asyncio.open_connection(host, port)
            log.info("Client connected sending first data %s", msg)

            serialized_bnr = self.encoder_decoder.encode_status(msg_dict=msg)

            client_writer.write(serialized_bnr)
            await client_writer.drain()

            data = await client_reader.read(1024)

            if data is None:
                log.error("Expected status msg, received None")
                return False, 0
            log.info(f"received data is is {data}")

            deserialized_dict = self.encoder_decoder.decode_status(binary_data=data)

            log.info(f"deserialized_dict STATUS COUNT is  from {deserialized_dict}")


            # send ACK to client
            msg = {
                "type": "heartbeat",
                "msg": "ACK",
                "client_host": host,
                "client_port": port,
                "identifier": deserialized_dict.get("identifier"),
            }
            serialized_bnr = self.encoder_decoder.encode_heartbeat(msg_dict=msg)
            client_writer.write(serialized_bnr)
            await client_writer.drain()

            client_writer.close()
            return True, deserialized_dict.get("message_count", 0)
        except (ConnectionError, OSError) as e:
            log.error(f"Connection error while sending status request to client{e}")
            return False, 0

    async def send_status_request_to_clients(self):
        """Run func every interval seconds."""
        while True:
            log.info(f"send_status_request_to_clients.........{active_clients}")
            clients_from_db = await self.db_op_manager.query_saved_clients_from_db()
            log.info(f"clients_from_db =  {clients_from_db}")
            updated_clients_mapping = {}

            # send message to all saved clients in the cache
            for client_id in active_clients:
                host = active_clients[client_id].get("client_host")
                port = active_clients[client_id].get("client_port")

                msg = {"type": "status", "message_count": 0, "identifier": client_id}

                client_status, count = await self.send_a_message_to_client(
                    host, port, msg
                )
                if client_status:
                    updated_clients_mapping[client_id] = {
                        "client_identifier": client_id,
                        "is_connected": True,
                        "client_host": host,
                        "client_port": port,
                        "status_count": count,
                    }
                log.info(
                    f"Client status for {host}, {port} is {client_status} after status check, map is "
                    f"{updated_clients_mapping}"
                )

            # send message to all saved clients from the database
            for client in clients_from_db:
                log.info(client)
                host = client.get("client_host").strip()
                port = client.get("client_port")
                client_id = client.get("client_identifier")
                log.info(f"from db: {host}{port}{client_id}")
                msg = {"type": "status", "message_count": client.get("status_count", 0), "identifier": client_id}
                client_status, count = await self.send_a_message_to_client(
                    host, port, msg
                )
                if client_status:
                    updated_clients_mapping[client_id] = {
                        "client_identifier": client_id,
                        "is_connected": True,
                        "client_host": host,
                        "client_port": port,
                        "status_count": count,
                    }
                    if count != client.get("status_count"):
                        log.warning(
                            f"Status count for client id {client_id} is different from database and actual from client"
                        )
            log.info(f"updated_clients_mapping is {updated_clients_mapping}")
            await self.db_op_manager.update_client_list_to_db(updated_clients_mapping)
            await asyncio.sleep(random.randint(30, 35))

    async def handle_client(
        self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter
    ):
        data = await client_reader.read(1024)
        if not data:
            raise Exception("socket closed")

        log.info(f"handle_client:")

        deserialized_dict = self.encoder_decoder.decode_heartbeat(binary_data=data)

        log.info(f"Received deserialized data is {deserialized_dict}")

        if deserialized_dict.get("type") == "heartbeat":
            client_identifier = deserialized_dict.get("identifier")
            client_host = deserialized_dict.get("client_host")
            client_port = deserialized_dict.get("client_port")
            log.info(
                f"Client info: ip {client_host} port {client_port} identifier {client_identifier} "
            )
            active_clients[client_identifier] = {
                "client_host": client_host,
                "client_port": client_port,
            }
            log.info(f"active_clients is {active_clients}")
        else:
            # do nothing as we are only expecting heartbeat message
            pass
        deserialized_dict["type"] = "heartbeat"
        deserialized_dict["msg"] = "ACK"
        binary_data = self.encoder_decoder.encode_heartbeat(deserialized_dict)
        client_writer.write(binary_data)
        await client_writer.drain()
