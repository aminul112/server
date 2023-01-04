
import asyncpg


class AsyncPgPostgresManager:
    def __init__(self, log):
        self.log = log

    async def query_saved_clients_from_db(self):
        conn = None        
        try:
            self.log.info("query_saved_clients_from_db()")
            conn = await asyncpg.connect(user='devuser', password='devpwd',
                                         database='devdb', host='0.0.0.0', port=5432)

            # Execute a statement to create a new table if necessary
            await conn.execute('''
               CREATE TABLE IF NOT EXISTS client_record (
                 client_identifier INTEGER NOT NULL,
                 status_count INTEGER,
                 is_connected BOOLEAN NOT NULL,
                 PRIMARY KEY (client_identifier , is_connected),             
                 client_host  CHAR(200) NOT NULL,             
                 client_port INTEGER NOT NULL,
                 connection_time  TIMESTAMP NOT NULL DEFAULT NOW()
                 )
           ''')

            # get all active clients
            rows = await conn.fetch(
                'SELECT * FROM client_record WHERE is_connected = $1', True)

            active_clients = [dict(row) for row in rows]

            # Close the connection
            await conn.close()
            return active_clients
        except Exception as e:
            if conn:
                await conn.close()
            self.log.error(f"Database exception happened {e}")
            return []

    async def update_client_list_to_db(self, updated_clients_mapping):
        conn = None
        
        try:
            self.log.info("update_client_list_to_db")
            conn = await asyncpg.connect(user='devuser', password='devpwd',
                                         database='devdb', host='0.0.0.0', port=5432)

            async with conn.transaction():

                await conn.execute('''
                               TRUNCATE client_record
                           ''')

                for client_id in updated_clients_mapping:
                    host = updated_clients_mapping[client_id].get("client_host")
                    port = updated_clients_mapping[client_id].get("client_port")
                    status_count = updated_clients_mapping[client_id].get("status_count")
                    await conn.execute('''
                       INSERT INTO client_record(client_identifier, is_connected, client_host, client_port, status_count) VALUES($1, $2, $3, $4, $5)
                   ''', client_id, True, host, port, status_count)

            await conn.close()
        except Exception as e:
            if conn:
                await conn.close()
            self.log.error(f"Database exception happened {e}")
            return []
