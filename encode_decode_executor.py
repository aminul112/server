

class EncodeDecodeExecutor:
    def __init__(self, executor):
        self.executor = executor

    def encode_hello(self, msg_dict):
        return self.executor.encode_hello(msg_dict)

    def encode_status(self, msg_dict):
        return self.executor.encode_status(msg_dict)

    def decode_hello(self, binary_data):
        return self.executor.decode_hello(binary_data)

    def decode_status(self, binary_data):
        return self.executor.decode_status(binary_data)

