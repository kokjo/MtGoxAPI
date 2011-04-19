import MtGoxAPI
import time

client = MtGoxAPI.Client()

while(True):
    t = client.get_ticker()
    print "sell: %G buy: %G last: %G ---- market volume: %d ---- high: %G low: %G" % (t["sell"], t["buy"], t["last"], t["vol"], t["high"], t["low"])
    time.sleep(10)
