import os
from sys import argv, exit, stdin, stdout, stderr
from secrets import get_secret

def startDaemon(log_file, pid_file):
	print "DAEMONIZING PROCESS>>>"
	try:
		pid = os.fork()
		if pid > 0:
			exit(0)
	except OSError, e:
		print e.errno
		exit(1)
		
	os.chdir("/")
	os.setsid()
	os.umask(0)
	
	try:
		pid = os.fork()
		if pid > 0:
			f = open(pid_file, 'w')
			f.write(str(pid))
			f.close()
			
			exit(0)
	except OSError, e:
		print e.errno
		exit(1)
	
	si = file('/dev/null', 'r')
	so = file(log_file, 'a+')
	se = file(log_file, 'a+', 0)
	os.dup2(si.fileno(), stdin.fileno())
	os.dup2(so.fileno(), stdout.fileno())
	os.dup2(se.fileno(), stderr.fileno())

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

class ProofOfExistenceApp():
	def __init__(self):
		print "new notary instance"

	def start_app(self):
		print "starting app"

		from lib.proofofexistence.main import app as poe_app
		

		MONITOR_DIR = os.path.join(get_secret('BASE_DIR'), ".monitor")
		self.api = app

		startDaemon(os.path.join(MONITOR_DIR, "app.log"), os.path.join(MONITOR_DIR, "app.pid"))

	def start(self):
		# START APP
		from multiprocessing import Process

		p = Process(target=self.start_app)
		p.join()


		# START CRON
		return False

	def stop(self):
		print "stopping app"

		MONITOR_DIR = os.path.join(get_secret('BASE_DIR'), ".monitor")
		return stopDaemon(os.path.join(MONITOR_DIR), extra_pids_port=os.environ.get('API_PORT', None))

if __name__ == "__main__":
	usage_prompt = "usage: app.py [start|stop|restart] --base-dir=/path/to/configs/dir"

	if len(argv) < 2:
		print usage_prompt
		exit(-1)

	res = False
	app = ProofOfExistenceApp()

	if argv[1] in ["restart", "stop"]:
		res = app.stop()

	if argv[1] in ["restart", "start"]:
		res = app.start()

	if len(argv) > 2:
		print argv[2:]

	exit(0 if res else -1)
