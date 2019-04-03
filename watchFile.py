import time
import threading
import BaseHTTPServer, SimpleHTTPServer
# import websocket

index = 0
statsQueue = []
statsFilename = '/home/yzngo/Documents/mrtc_stats/mrtc_history_stats'

def getStats():
  global index

  while True:
    time.sleep(5)
    statsFile = open(statsFilename, 'r')
    statsFile.seek(index, 0)
    line = statsFile.readline()
    if line:
      index = statsFile.tell()
      statsQueue.append(line)
      print(line)
    statsFile.close()
  

class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(statsQueue.pop())


def runHTTPServer():
  httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8001), SimpleHTTPRequestHandler)
  httpd.serve_forever()


if __name__ == '__main__':
  t1 = threading.Thread(target=getStats, name='getStats')
  t2 = threading.Thread(target=runHTTPServer, name='runHTTPServer')
  t1.start()
  t2.start()
  
