import os
import cherrypy

cherrypy.config.update({'server.socket_port': 8081, "server.socket_host": "0.0.0.0"})
cherrypy.engine.restart()

class BlockIps:
    # http://localhost:8081/blockIp?ip=1824.124.123.1
    @cherrypy.expose
    def blockIp(self, ip=None):
        if ip:
            block_command = f"iptables -A INPUT -s {ip} -j DROP"
            print(block_command)
            status = os.system(block_command)
            return "success" if status == 0 else "error"
        else:
            return 'No Ip was passed' if ip is None else 'No Ip was passed'

    # http://localhost:8081/allowIp?ip=1824.124.123.1
    @cherrypy.expose
    def allowIp(self, ip=None):
        if ip:
            allow_command = f"iptables -D INPUT -s {ip} -j DROP"
            print(allow_command)
            status = os.system(allow_command)
            return "success" if status == 0 else "error"
        else:
            return 'No Ip was passed' if ip is None else 'No Ip was passed'



if __name__ == '__main__':
    cherrypy.quickstart(BlockIps())