from google.appengine.ext import db
from pycoin.encoding import hash160_sec_to_bitcoin_address
from blockchain import new_address, publish_data, archive_address, address_balance
import datetime
from time import sleep
from config import MIN_SATOSHIS_PAYMENT

class LatestBlockchainDocuments(db.Model):
  """Helper table for latest confirmed documents retrieval"""
  digests = db.StringListProperty()
  
  def add_document(self, digest):
    self.digests = [digest] + self.digests[:-1]
    self.put()
  
  @classmethod
  def get_inst(cls):
    inst = cls.all().get()
    if not inst:
      inst = cls()
      inst.put()
    return inst

class Document(db.Model):
  """Models a proof of document existence at a certain time"""
  digest = db.StringProperty()
  pending = db.BooleanProperty()
  tx = db.StringProperty()
  payment_address = db.StringProperty()

  timestamp = db.DateTimeProperty(auto_now_add=True)
  txstamp = db.DateTimeProperty()
  blockstamp = db.DateTimeProperty()
  
  legacy = db.BooleanProperty()
  archived= db.DateTimeProperty()

  def received_payment(self):
    self.pending = False
    self.put()

  def payment_received(self):
    return not self.pending

  def is_actionable(self):
    return self.payment_received() and self.tx == ''

  def to_dict(self):
    if not self.payment_address:
      self.payment_address = new_address(self.digest)
      self.put()
    d = db.to_dict(self)
    return d

  def has_balance(self):
    balance = address_balance(self.payment_address)
    return True if balance >= MIN_SATOSHIS_PAYMENT else False

  @classmethod
  def get_doc(cls, digest):
    return cls.all().filter("digest = ", digest).get()

  @classmethod
  def get_by_address(cls, address):
    return cls.all().filter('payment_address = ', address).get()

  @classmethod
  def new(cls, digest):
    d = cls(digest=digest)
    d.pending = True
    d.legacy = False
    d.tx = ''
    d.payment_address = None

    d.put()
    return d

  LATEST_N = 5
  @classmethod
  def get_latest(cls, confirmed=False):
    if confirmed:
      bag = LatestBlockchainDocuments.get_inst()
      return [cls.get_doc(digest) for digest in bag.digests]
    else:
      return cls.all().order("-timestamp").run(limit=cls.LATEST_N)

  @classmethod
  def get_actionable(cls):
    return cls.all().filter("pending == ", False).filter("tx == ", '').run()

  @classmethod
  def get_paid(cls, offset=0):
    limit = datetime.datetime.now() - datetime.timedelta(days=10)
    #.filter("timestamp < ", limit) \
    pending = cls.all() \
      .filter("pending == ", True) \
      .filter("tx == ", '') \
      .run(offset=offset, limit=50)
    for d in pending:
      if d.has_balance():
        yield d
      sleep(0.2)

  @classmethod
  def update_schema(cls):
    ds = cls.all()
    n = 0
    for d in ds:
      n += 1
    return n

  @classmethod
  def get_archiveable(cls):
    limit = datetime.datetime.now() - datetime.timedelta(days=5)
    return cls.all() \
      .filter("timestamp < ", limit) \
      .filter("tx == ", '') \
      .filter("archived == ", None) \
      .run(limit=100)

  def archive(self):
    result = archive_address(self.payment_address)
    if result.get('archived'):
      self.archived = datetime.datetime.now()
      self.put()
    return result

  def blockchain_certify(self):
    if self.tx:
      return {"success" : False, "error": "already certified"}
    txid, message = publish_data(self.digest.decode('hex'))
    if txid:
      self.tx = txid
      self.txstamp = datetime.datetime.now()
      LatestBlockchainDocuments.get_inst().add_document(self.digest)
      self.put()
    return {"success" : txid is not None, "tx" : txid, "message" : message}

