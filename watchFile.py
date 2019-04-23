#coding=utf-8
import time
import threading
import subprocess as cmd
import BaseHTTPServer, SimpleHTTPServer

kDefaultPort = 8007
kTimeinterval = 5
kRootPath = '/data/log/stream_switch/'
kStatsPath = 'mrtc_info.stats.'
kInteractionPath = 'mrtc_info.interaction.'

statsMutex = threading.Lock()
interactionMutex = threading.Lock()

index = None
statsPath = ''
interactionPath = ''

date = ''
stats = ['[null]']
interaction = ['[null]']

def getTime():
  localtime = time.localtime(time.time())
  return '{:0>4d}'.format(localtime[0]) + '-' + '{:0>2d}'.format(localtime[1]) + '-' + '{:0>2d}'.format(localtime[2])

def processFile():
  global date, index, statsPath, interactionPath
  while (True):
    time.sleep(kTimeinterval)
    dateTemp = getTime()
    if date != dateTemp:
      # 更新stats句柄
      popen = cmd.Popen('touch ' + kRootPath + kStatsPath + dateTemp, stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
      res = popen.stdout.readline()
      statsMutex.acquire()
      statsPath = kRootPath + kStatsPath + dateTemp
      statsFile = open(statsPath, 'r')
      statsFile.seek(0, 2)
      index = statsFile.tell() # 一定要重新更新index
      statsFile.close()
      statsMutex.release()
      # 更新interaction文件名
      popen = cmd.Popen('touch ' + kRootPath + kInteractionPath + dateTemp, stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
      res = popen.stdout.readline()
      interactionMutex.acquire()
      interactionPath = kRootPath + kInteractionPath + dateTemp
      interactionMutex.release()
      # 更新date
      date = dateTemp
      # 只保留3天的内容
      popen = cmd.Popen('find ' + kRootPath + ' -name "mrtc_info.*" -mtime +2 | xargs rm -rf', stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
      res = popen.stdout.readline()

def getStats():
  global index
  statsFile = open(statsPath, 'r')
  statsFile.seek(0, 2)
  index = statsFile.tell()
  statsFile.close()
  while True:
    time.sleep(kTimeinterval)
    statsMutex.acquire()
    statsFile = open(statsPath, 'r')
    statsFile.seek(index, 0)
    line = statsFile.readline()
    stats.pop()
    if line:
      index = statsFile.tell()
      find = line.find(' ', 11) # 截去时间戳 2019-04-23 从下标=11开始寻找
      stats.append(line[find+1:])
    else:
      stats.append('[null]')
    statsFile.close()
    statsMutex.release()

def getInteraction():
  while True:
    time.sleep(kTimeinterval)
    interactionMutex.acquire()
    popen = cmd.Popen('tail -n 1 ' + interactionPath, stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
    line = popen.stdout.readline().strip()
    interaction.pop()
    if line:
      find = line.find(' ', 11) # 截去时间戳
      interaction.append(line[find+1:])
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
      # 发送最近3天的内容
      popen = cmd.Popen('find ' + kRootPath + ' -name "mrtc_info.stats*" -mtime -3 | xargs ls -lt', stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
      for line in popen.stdout.readlines():
        fileName = line.split(' ')
        historyFile = open(fileName[-1][:-1], 'r')
        self.wfile.write(historyFile.read())
        historyFile.close()
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
      popen = cmd.Popen('find ' + kRootPath + ' -name "mrtc_info.interaction*" -mtime -3 | xargs ls -lt', stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
      for line in popen.stdout.readlines():
        fileName = line.split(' ')
        historyFile = open(fileName[-1][:-1], 'r')
        self.wfile.write(historyFile.read())
        historyFile.close()

if __name__ == '__main__':
  # 根据当前时间创建文件
  date = getTime()
  statsPath = kRootPath + kStatsPath + date
  interactionPath = kRootPath + kInteractionPath + date
  popen = cmd.Popen('mkdir -p ' + kRootPath + ' && touch ' + statsPath + ' ' + interactionPath, stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
  res = popen.stdout.readline()

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
