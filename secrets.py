import json, os
from sys import argv

SECRETS = {}
BASE_DIR = os.path.abspath(os.path.join(os.path.join(__file__, os.pardir), os.pardir))

print BASE_DIR

def get_secret(keys, info=False):
	if type(keys) in [str, unicode]:
		keys = [keys]
	if type(keys) != list:
		return None

	secrets = []
	for k in keys:
		if k in SECRETS.keys():
			secrets.append(SECRETS[k])

	if len(secrets) == 1:
		return secrets[0]
	elif len(secrets) == 0:
		return None

	if not info:
		return secrets

	return (secrets, keys)

try:
	if len(argv) == 2 and os.path.exists(argv[1]):
		argv.pop()
		BASE_DIR = argv[1]
		print 
except Exception as e:
	print e, type(e)

try:
	with open(os.path.join(BASE_DIR, "config.json"), 'rb') as s:
		SECRETS = json.loads(s.read())
except Exception as e:
	print e, type(e)

keys = ["ADMIN_EMAIL", "SECRET_ADMIN_PATH", "BLOCKCHAIN_WALLET_GUID", \
	"BLOCKCHAIN_PASSWORD_1", "BLOCKCHAIN_PASSWORD_2", "CALLBACK_SECRET", \
	"BLOCKCHAIN_ENCRYPTED_WALLET", "PAYMENT_PRIVATE_KEY", "PAYMENT_ADDRESS"]

for s in s_keys:
	locals[s] = get_secret(s)
