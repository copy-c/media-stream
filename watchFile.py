#coding=utf-8

import sys
import time
import threading
import subprocess
import BaseHTTPServer, SimpleHTTPServer

kDefaultPort = 8005
kTimeinterval = 5
kRootPath = '/Users/copy/'
kStatsPath = 'mrtc_info.stats.'
kInteractionPath = 'mrtc_info.interaction.'

statsFile = None
statsFilePtr = None
interactionFile = None

statsMutex = threading.Lock()
interactionMutex = threading.Lock()

date = 0
stats = ['[null]']
interaction = ['[null]']

def getTime():
  localtime = time.localtime(time.time())
  return str(localtime[0]) + '-' + str(localtime[1]) + '-' + str(localtime[2])

def processFile():
  global date, statsFile, statsFilePtr, interactionFile
  while (True):
    time.sleep(kTimeinterval)
    dateTemp = getTime()
    print(dateTemp)
    if date != dateTemp:
      date = dateTemp
      popen = subprocess.Popen('touch ' + kRootPath + kStatsPath + date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      result = popen.stdout.readline()
      statsMutex.acquire()
      statsFile.close()
      statsFile = open(kRootPath + kStatsPath + date, 'r')
      statsFile.seek(0, 2)
      statsFilePtr = statsFile.tell()
      statsMutex.release()
      popen = subprocess.Popen('touch ' + kRootPath + kInteractionPath + date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      result = popen.stdout.readline()
      interactionMutex.acquire()
      interactionFile.close()
      interactionFile = open(kRootPath + kInteractionPath + date, 'r')
      interactionMutex.release()

def getStats():
  global statsFilePtr
  while True:
    time.sleep(kTimeinterval)
    statsMutex.acquire()
    statsFile.seek(statsFilePtr, 0)
    line = statsFile.readline()
    stats.pop()
    if line:
      statsFilePtr = statsFile.tell()
      stats.append(line)
    else:
      stats.append('[null]')
    statsMutex.release()

def getInteraction():
  while True:
    time.sleep(kTimeinterval)
    interactionMutex.acquire()
    popen = subprocess.Popen('tail -n 1 ' + kInteractionPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    line = popen.stdout.readline().strip()
    interaction.pop()
    if line:
      interaction.append(line)
    else:
      interaction.append('[null]')
    interactionMutex.release()

def runHttpServer():
  httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', kDefaultPort), RequestHandler)
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
      self.wfile.write(statsFile.read())
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
      self.wfile.write(interactionFile.read())
      interactionMutex.release()


if __name__ == '__main__':
  # 根据当前时间创建文件
  date = getTime()
  popen = subprocess.Popen('mkdir -p ' + kRootPath + ' && touch ' + kRootPath + kStatsPath + date + ' && touch ' + kRootPath + kInteractionPath + date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  result = popen.stdout.readline()

  # 打开stats文件，更新文件指针，使其指向文件最后
  statsFile = open(kRootPath + kStatsPath + date, 'r')
  statsFile.seek(0, 2) 
  statsFilePtr = statsFile.tell()

  # 打开interaction文件
  interactionFile = open(kRootPath + kInteractionPath + date, 'r')

  # 注册线程
  getStatsTread = threading.Thread(target = getStats, name = 'getStats')
  getInteractionThread = threading.Thread(target = getInteraction, name = 'getInteraction')
  runStatsHttpThread = threading.Thread(target = runHttpServer, name = 'runStatsHttpServer')
  processFileHttpThread = threading.Thread(target = processFile, name = 'processFile')

  # 开启线程
  getStatsTread.start()
  getInteractionThread.start()
  runStatsHttpThread.start()
  processFileHttpThread.start()
  
  getStatsTread.join()
  getInteractionThread.join()
  runStatsHttpThread.join()
  processFileHttpThread.join()
