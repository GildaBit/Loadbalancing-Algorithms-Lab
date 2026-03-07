DEFAULT_WEIGHT = 1


class Server:
    def __init__(self, id, weight=DEFAULT_WEIGHT):
        self.id = id
        self.weight = weight
        self.request_count = 0

    def handle_request(self):
        self.request_count += 1

    def __repr__(self):
        return f"Server({self.id}, weight={self.weight}, count={self.request_count})"
