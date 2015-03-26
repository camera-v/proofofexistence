import os, yaml
from sys import argv, exit

def setup():
	# validate/set configs
	# write cron script according to cron.yaml
	return False

if __name__ == "__main__":
	base_dir = None

	if len(argv) == 2 and os.path.exists(argv[1]):
		base_dir = os.path.abspath(argv[1])
		os.environ['POE_BASE_DIR'] = base_dir

	if setup():
		exit(0)

	exit(-1)