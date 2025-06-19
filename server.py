from opcua import Server
from add_revvity import add_revvity
import time

server = Server()
server.set_endpoint("opc.tcp://localhost:4840/")

ns_idx = server.register_namespace("http://opcua.persist-ai.com/test-platform")

objects = server.get_objects_node()
#sn = add_stellar_net(ns_idx,objects, "UV")
#meca = add_meca(ns_idx,objects,"MecaRobot1")
# waveshare = add_waveshare(ns_idx, objects, "RelayModule")
# misumi = add_misumi(ns_idx, objects, "MisumiXY")
rev = add_revvity(ns_idx, objects, "RevvityHandler")


server.start()

try:
    while True:
        time.sleep(1)
finally:
    server.stop()
