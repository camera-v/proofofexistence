from sys import argv, exit

class ProofOfExistenceApp():
	def __init__(self):
		print "new notary instance"

	def start(self):
		print "starting app"

		'''
		import redis
		from rom import util

		from lib.proofofexistence.main import app as poe_app

		self.poe_app = poe_app
		util.set_connection_settings(host="localhost", 
			port=os.environ.get('REDIS_PORT', 6379), db=0)
		'''
		return False

	def stop(self):
		print "stopping app"
		return False

if __name__ == "__main__":
	usage_prompt = "usage: app.py [start|stop|restart] --config=/path/to/config"

	if len(argv) < 2:
		print usage_prompt
		exit(-1)

	res = False
	app = ProofOfExistenceApp()

	if argv[1] in ["restart", "stop"]:
		res = app.stop()

	if argv[1] in ["restart", "start"]:
		res = app.start()

	argv = [argv[0]] + argv[2:]

	if len(argv) > 1:
		print argv[1:]

		
	exit(0 if res else -1)
