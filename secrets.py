import json, os
from sys import argv

SECRETS = {}
BASE_DIR = os.path.abspath(os.path.join(os.path.join(__file__, os.pardir), os.pardir))

def get_secret(keys, info=False):	
	if type(keys) in [str, unicode]:
		keys = [keys]
	if type(keys) != list:
		return None

	secrets = []
	for k in keys:
		if k in SECRETS.keys():
			secrets.append(SECRETS[k])

	print "SECRET %s: %s" % (keys, secrets)

	if len(secrets) == 1:
		return secrets[0]
	elif len(secrets) == 0:
		return None

	if not info:
		return secrets

	return (secrets, keys)

try:
	if len(argv) >= 3:
		for a in argv[2:]:
			a = a.split("=")
			if a[0] == "--base-dir":
				b = os.path.abspath(a[1])
				if(os.path.exists(os.path.join(b, "poe.config.json"))):
					BASE_DIR = b
					break

except Exception as e:
	print e, type(e)

try:
	with open(os.path.join(BASE_DIR, "poe.config.json"), 'rb') as s:
		SECRETS = json.loads(s.read())
except Exception as e:
	print e, type(e)

keys = ["ADMIN_EMAIL", "DEFAULT_SENDER_EMAIL", "SECRET_ADMIN_PATH", "BLOCKCHAIN_WALLET_GUID", \
	"BLOCKCHAIN_PASSWORD_1", "BLOCKCHAIN_PASSWORD_2", "CALLBACK_SECRET", \
	"BLOCKCHAIN_ENCRYPTED_WALLET", "PAYMENT_PRIVATE_KEY", "PAYMENT_ADDRESS"]

lcl = locals()
for k in keys:
	lcl[k] = get_secret(k)

