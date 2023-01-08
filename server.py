import asyncio
import logging
import random

from db_operations import AsyncPgPostgresManager
from encode_decode_executor import EncodeDecodeExecutor

log = logging.getLogger('__main__.' + __name__)


class Server:
    def __init__(
            self,
            encoder_decoder: EncodeDecodeExecutor,
            db_op_manager: AsyncPgPostgresManager,
            query_seconds_interval_lower: int,
            query_seconds_interval_upper: int,
    ):
        self.encoder_decoder = encoder_decoder
        self.db_op_manager = db_op_manager
        self.query_seconds_interval_lower = query_seconds_interval_lower
        self.query_seconds_interval_upper = query_seconds_interval_upper
        self.clients = {}  # to handle multiple clients
        self.active_clients_in_cache = {}  # save all client information

    def accept_client(
            self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter
    ) -> None:
        """
        This is callback function for start_server() function of asyncio.
        :param client_reader: StreamReader object to read data from client.
        :param client_writer: StreamWriter object to write data to client.
        """
        task = asyncio.Task(self.handle_client(client_reader, client_writer))
        self.clients[task] = (client_reader, client_writer)

        def client_disconnected(task_del):
            del self.clients[task_del]
            client_writer.close()
            log.info("client disconnected")

        log.info("client connected")
        task.add_done_callback(client_disconnected)

    async def send_a_message_to_client(self, host: str, port: int, msg: dict) -> (bool, int):
        """
        This method sends a message to a given client and try to get message count from the client.

        :param host: client's host address.
        :param port: client's port number
        :param msg: message to send
        :return: status of client as True or False and heartbeat message count from this client.
        """
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

            deserialized_dict = self.encoder_decoder.decode_status(binary_data=data)

            log.info(f"deserialized_dict STATUS COUNT is  from {deserialized_dict}")

            # send 'ack' to client
            msg = {
                "type": "heartbeat",
                "msg": "ack",
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

    async def send_status_request_to_clients(self) -> None:
        """
        This method runs an infinite loop and send status message
        to all active clients in the cache and saved in the database.
        The interval is determined randomly between 2 configured values saved in self.query_seconds_interval_lower and
        self.query_seconds_interval_upper
        Then it updates the database with the latest information from the clients.
        """
        while True:
            log.info(f"send_status_request_to_clients.........{self.active_clients_in_cache}")
            clients_from_db = await self.db_op_manager.query_saved_clients_from_db()
            log.info(f"clients_from_db =  {clients_from_db}")
            updated_clients_mapping = {}

            # send message to all saved clients in the cache
            for client_id in self.active_clients_in_cache:
                host = self.active_clients_in_cache[client_id].get("client_host")
                port = self.active_clients_in_cache[client_id].get("client_port")

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
                existing_status_count = client.get("status_count", 0)
                log.info(f"from db: {host}{port}{client_id}")
                # avoid sending duplicate message to client_id existing in cache and database
                if client_id not in updated_clients_mapping:
                    msg = {"type": "status", "message_count": existing_status_count, "identifier": client_id}
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
                        if count != existing_status_count:
                            log.error(
                                f"Status count for client id {client_id} is different from database and actual from "
                                f"client "
                            )
                else:
                    # this client is already communicated from active_clients_in_cache cache info
                    if existing_status_count != updated_clients_mapping[client_id].get("status_count"):
                        log.error(
                            f"Status count for client id {client_id} is different from database and actual from client"
                        )

                log.info(f"updated_clients_mapping is {updated_clients_mapping}")
            await self.db_op_manager.update_client_list_to_db(updated_clients_mapping)
            await asyncio.sleep(random.randint(self.query_seconds_interval_lower, self.query_seconds_interval_upper))

    async def handle_client(
            self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter
    ) -> None:
        """
        To serve connectivity request from a client.
        :param client_reader: StreamReader object to read data from client.
        :param client_writer: StreamWriter object to write data to client.
        """
        data = await client_reader.read(1024)
        if not data:
            raise Exception("socket closed")

        log.info(f"handle_client: got a new connection request")

        deserialized_dict = self.encoder_decoder.decode_heartbeat(binary_data=data)

        log.info(f"Received deserialized data is {deserialized_dict}")

        if deserialized_dict.get("type") == "heartbeat":
            client_identifier = deserialized_dict.get("identifier")
            client_host = deserialized_dict.get("client_host")
            client_port = deserialized_dict.get("client_port")
            log.info(
                f"Client info: ip {client_host} port {client_port} identifier {client_identifier} "
            )
            self.active_clients_in_cache[client_identifier] = {
                "client_host": client_host,
                "client_port": client_port,
                "identifier": client_identifier,
            }
            log.info(f"active_clients_in_cache is {self.active_clients_in_cache}")
        else:
            # do nothing as we are only expecting heartbeat message. So far we do not expect any other
            # message here. In the future, we might support other message types
            pass
        deserialized_dict["type"] = "heartbeat"
        deserialized_dict["msg"] = "ack"
        binary_data = self.encoder_decoder.encode_heartbeat(deserialized_dict)
        client_writer.write(binary_data)
        await client_writer.drain()
