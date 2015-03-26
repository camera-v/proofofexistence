import json, os

SECRETS = {}
BASE_DIR = os.path.abspath(os.dirname(__file__))

print BASE_DIR

def get_secret(keys):
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

	return secrets

try:
	BASE_DIR = os.environ['POE_BASE_DIR']
except Exception as e:
	print e, type(e)

try:
	with open(os.path.join(BASE_DIR, "poe.config.json"), 'rb') as s:
		SECRETS = json.loads(s.read())
except Exception as e:
	print e, type(e)

for s in ["ADMIN_EMAIL", "SECRET_ADMIN_PATH", "BLOCKCHAIN_WALLET_GUID", \
	"BLOCKCHAIN_PASSWORD_1", "BLOCKCHAIN_PASSWORD_2", "CALLBACK_SECRET", \
	"BLOCKCHAIN_ENCRYPTED_WALLET", "PAYMENT_PRIVATE_KEY", "PAYMENT_ADDRESS"]:
	locals[s] = get_secret(s)
