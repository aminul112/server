

class EncodeDecodeExecutor:
    def __init__(self, executor):
        self.executor = executor

    def encode_heartbeat(self, msg_dict):
        return self.executor.encode_heartbeat(msg_dict)

    def encode_status(self, msg_dict):
        return self.executor.encode_status(msg_dict)

    def decode_heartbeat(self, binary_data):
        return self.executor.decode_heartbeat(binary_data)

    def decode_status(self, binary_data):
        return self.executor.decode_status(binary_data)

