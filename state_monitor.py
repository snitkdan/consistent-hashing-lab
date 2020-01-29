class StateMonitor:
    def __init__(self, servers):
        self.num_monitors = len(servers)
        self.servers = set()
        for server in servers:
            self.servers.add(server)
        self.content = {}
        for i in range(num_monitors):
            self.content[self.servers[i]] = {}

    def servers():
        return self.servers

    def add_server(server_name):
        self.num_monitors += 1
        self.servers.append(server_name)
        self.content[server_name] = {}

    def remove_server(server_name):
        if 