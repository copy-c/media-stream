#coding=utf-8

import sys
import time
import threading
import subprocess
import BaseHTTPServer, SimpleHTTPServer

defaultPort = 8005
'''
rootPath = '/data/mrtc_info/'
'''
rootPath = '/home/yzngo/Documents/mrtc_info/'
statsPath = ' '
interactionPath = ' '

statsFile = 
interactionFile

timeinterval = 5
statsMutex = threading.Lock()
interactionMutex = threading.Lock()

stats = ['[null]']
interaction = ['[null]']

def getDate():
  localtime = time.localtime(time.time())
  return str(localtime[0]) + '-' + str(localtime[1]) + '-' + str(localtime[2])

def processFile():
  date = getTime()
  while (True):
    time.sleep(timeinterval)
    if date != getTime():
      date = getTime()

      statsMutex.acquire()
      statsPath = rootPath + 'mrtc_info.stats.' + date
      popen = subprocess.Popen('touch ' + statsPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      result = popen.stdout.readline()



      statsMutex.release()
      interactionMutex.acquire()
      interactionPath = rootPath + 'mrtc_info.interaction.' + date
      popen = subprocess.Popen('touch ' + interactionPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      result = popen.stdout.readline()
      interactionMutex.release()
      subprocess.Popen('touch ' + statsPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      
    

def getStats():
  statsFile = open(statsPath, 'r')
  statsFile.seek(0, 2)
  index = statsFile.tell()
  statsFile.close()
  while True:
    time.sleep(timeinterval)
    statsMutex.acquire()
    statsFile = open(statsPath, 'r')
    statsFile.seek(index, 0)
    line = statsFile.readline()
    stats.pop()
    if line:
      index = statsFile.tell()
      stats.append(line)
    else:
      stats.append('[null]')
    statsFile.close()
    statsMutex.release()

def getInteraction():
  while True:
    time.sleep(timeinterval)
    interactionMutex.acquire()
    popen = subprocess.Popen('tail -n 1 ' + interactionPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    line = popen.stdout.readline().strip()
    interaction.pop()
    if line:
      interaction.append(line)
    else:
      interaction.append('[null]')
    interactionMutex.release()

def runHttpServer():
  httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', defaultPort), RequestHandler)
  httpd.serve_forever()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/stats':
      self.send_response(200)
      self.end_headers()
      statsMutex.acquire()
      message = '{"status":' + stats[0] + '}'
      self.wfile.write(message)
      statsMutex.release()
    elif self.path == '/download_stats':
      self.send_response(200)
      self.end_headers()
      statsMutex.acquire()
      statsFile = open(statsPath, 'r')
      self.wfile.write(statsFile.read())
      statsFile.close()
      statsMutex.release()

      
    elif self.path == '/interaction':
      self.send_response(200)
      self.end_headers()
      interactionMutex.acquire()
      message = '{"interaction":' + interaction[0] + '}'
      self.wfile.write(message)
      interactionMutex.release()
    elif self.path == '/download_interaction':
      self.send_response(200)
      self.end_headers()
      interactionMutex.acquire()
      interactionFile = open(interactionPath, 'r')
      self.wfile.write(interactionFile.read())
      interactionFile.close()
      interactionMutex.release()


if __name__ == '__main__':
  statsPath = rootPath + 'mrtc_info.stats.' + getTime()
  interactionPath = rootPath + 'mrtc_info.interaction.' + getTime()

  popen = subprocess.Popen('mkdir -p ' + rootPath + ' && touch ' + statsPath + ' && touch ' + interactionPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  result = popen.stdout.readline()

  getStatsTread = threading.Thread(target = getStats, name = 'getStats')
  getStatsTread.start()

  getInteractionThread = threading.Thread(target = getInteraction, name = 'getInteraction')
  getInteractionThread.start()

  runStatsHttpThread = threading.Thread(target = runHttpServer, name = 'runStatsHttpServer')
  runStatsHttpThread.start()

  processFileHttpThread = threading.Thread(target = processFile, name = 'processFile')
  processFileHttpThread.start()



  
