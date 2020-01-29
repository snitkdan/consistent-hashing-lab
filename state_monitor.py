from server import Server 

class StateMonitor:
    def __init__(self, servers):
        self.num_monitors = len(servers)
        self.servers = {}
        for name in servers:
            self.servers[name] = Server(name)

    def servers():
        return self.servers

    def add_server(server_name):
        self.num_monitors += 1
        self.servers[server_name] = Server(server_name)

    def remove_server(server_name):
        s = self.servers.pop(server_name, None)
        if s:
            return (s.kvstore, s.access_tracking)
        return None

    