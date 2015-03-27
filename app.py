import os, sys, signal
from fabric.api import settings, local
from secrets import BASE_DIR

MONITOR_DIR = os.path.join(BASE_DIR, ".monitor")

def startDaemon(log_file, pid_file):
	print "DAEMONIZING PROCESS>>> (STDIN %d)" % sys.stdin.fileno()
	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError, e:
		print e.errno
		sys.exit(1)
		
	os.chdir("/")
	os.setsid()
	os.umask(0)
	
	try:
		pid = os.fork()
		if pid > 0:
			f = open(pid_file, 'w')
			f.write(str(pid))
			f.close()
			
			sys.exit(0)
	except OSError, e:
		print e.errno
		sys.exit(1)
	
	si = file('/dev/null', 'r')
	so = file(log_file, 'a+')
	se = file(log_file, 'a+', 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())

	print ">>> PROCESS DAEMONIZED"

def stopDaemon(pid_file, extra_pids_port=None):
	pid = False
	try:
		f = open(pid_file, 'r')
		try:
			pid = int(f.read().strip())
		except ValueError as e:
			print "NO PID AT %s" % pid_file
	except IOError as e:
		print "NO PID AT %s" % pid_file
	
	if pid:
		print "STOPPING DAEMON on pid %d" % pid
		try:
			os.kill(pid, signal.SIGTERM)
			
			if extra_pids_port is not None:
				pids = Popen(['lsof', '-t', '-i:%d' % extra_pids_port], stdout=PIPE)
				pid = pids.stdout.read().strip()
				pids.stdout.close()
				
				for p in pid.split("\n"):
					cmd = ['kill', str(p)]
					Popen(cmd)
			
			return True
		except OSError as e:
			print "could not kill process at PID %d" % pid

	return False

class POEException(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class ProofOfExistenceApp():
	def __init__(self):
		print "new notary instance"
		self.in_service = False

	def start_app(self):
		from paste import httpserver		

		startDaemon(os.path.join(MONITOR_DIR, "app.log"), os.path.join(MONITOR_DIR, "app.pid"))
		try:
			httpserver.serve(self.api, host="localhost", port=os.environ.get('API_PORT', 8700))

		except AttributeError as e:
			print e, type(e)

	def start(self):
		print "starting app"

		try:
			from main import app
		except Exception as e:
			print e, type(e)
			return False

		from multiprocessing import Process
		from fabric.api import settings, local
		
		try:
			# START API
			self.api = app
			p = Process(target=self.start_app)
			p.start()
			p.join()

			# START CRON
			'''
			with settings(warn_only=True):
				local("crontab %s" % os.path.join(BASE_DIR, "cron.tab"))
			'''

			return True

		except Exception as e:
			print e, type(e)

		return False

	def stop(self):
		print "stopping app"
		
		'''
		with settings(warn_only=True):
			local("kill -6 $(pgrep -U $(whoami) cron)")
		'''

		return stopDaemon(os.path.join(MONITOR_DIR, "app.pid"), extra_pids_port=os.environ.get('API_PORT', None))

if __name__ == "__main__":
	usage_prompt = "usage: app.py [start|stop|restart] --base-dir=/path/to/configs/dir"

	if len(sys.argv) < 2:
		print usage_prompt
		sys.exit(-1)

	res = False
	app = ProofOfExistenceApp()

	if sys.argv[1] in ["restart", "stop"]:
		res = app.stop()

	if sys.argv[1] in ["restart", "start"]:
		res = app.start()

	sys.exit(0 if res else -1)
