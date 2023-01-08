import logging

import asyncpg

log = logging.getLogger("__main__." + __name__)


class AsyncPgPostgresManager:
    def __init__(self, user, password, database_name, db_host, db_port):
        self.user = user
        self.password = password
        self.database = database_name
        self.host = db_host
        self.port = db_port

    async def query_saved_clients_from_db(self) -> list[dict]:
        """
        This function retrieves all active clients from the database.
        :return: a list of all active clients
        """
        conn = None
        try:
            log.info("query_saved_clients_from_db()")
            conn = await asyncpg.connect(
                user=self.user,
                password=self.password,
                database=self.database,
                host=self.host,
                port=self.port,
            )

            # Execute a statement to create a new table if necessary
            await conn.execute(
                """
               CREATE TABLE IF NOT EXISTS client_record (
                 client_identifier INTEGER NOT NULL,
                 status_count INTEGER,
                 is_connected BOOLEAN NOT NULL,
                 PRIMARY KEY (client_identifier , is_connected),             
                 client_host  CHAR(200) NOT NULL,             
                 client_port INTEGER NOT NULL,
                 connection_time  TIMESTAMP NOT NULL DEFAULT NOW()
                 )
           """
            )

            # get all active clients
            rows = await conn.fetch(
                "SELECT * FROM client_record WHERE is_connected = $1", True
            )

            active_clients = [dict(row) for row in rows]

            # Close the connection
            await conn.close()
            return active_clients
        except Exception as e:
            if conn:
                await conn.close()
            log.error(f"Database exception happened {e}")
            return []

    async def update_client_list_to_db(self, updated_clients_mapping: dict) -> None:
        """
        This method updates clients information to the database.

        :param updated_clients_mapping: a dictionary of all active clients information.
        :return:
        """
        conn = None

        try:
            log.info("update_client_list_to_db")
            conn = await asyncpg.connect(
                user=self.user,
                password=self.password,
                database=self.database,
                host=self.host,
                port=self.port,
            )

            # better to use a transaction since we are removing everything and saving fresh clients information
            async with conn.transaction():

                await conn.execute(
                    """
                               TRUNCATE client_record
                           """
                )

                for client_id in updated_clients_mapping:
                    host = updated_clients_mapping[client_id].get("client_host")
                    port = updated_clients_mapping[client_id].get("client_port")
                    status_count = updated_clients_mapping[client_id].get(
                        "status_count"
                    )
                    await conn.execute(
                        """
                       INSERT INTO client_record(client_identifier, is_connected, client_host, client_port, 
                       status_count) VALUES($1, $2, $3, $4, $5)
                   """,
                        client_id,
                        True,
                        host,
                        port,
                        status_count,
                    )

            await conn.close()
        except Exception as e:
            if conn:
                await conn.close()
            log.error(f"Database exception happened {e}")
