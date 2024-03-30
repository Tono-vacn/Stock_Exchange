from db_model import *
import datetime

def add_account(id: str, balance: float):
  session = sqlalchemy.orm.Session()
  if balance < 0:
    session.close()
    raise ValueError("Balance is negative")
  exist_account = session.query(Account).filter(Account.id == id).all()
  if exist_account is not None:
    session.close()
    raise ValueError("Account id exists")
  try:
    session.add(Account(id = id, balance = balance))
    session.commit()
  except:
    session.close()
    raise ValueError("Accounts already exists")
  session.close()
  pass

def check_account(account_id: str):
  session = sqlalchemy.orm.Session()
  exist_account = session.query(Account).filter(Account.id == account_id).all()
  if exist_account is None:
    session.close()
    return True
  session.close()
  return False

def add_position(account_id: str ,symbol: str, number: int):
  session = sqlalchemy.orm.Session()
  check_account(account_id)
  if number < 0:
    session.close()
    raise ValueError("No short allowed")
  rows = session.query(Position).filter(Position.account_id == account_id, Position.symbol == symbol).with_for_update().all()
  if rows is not None:
    for row in rows:
      row.amount += number
  else:
    session.add(Position(account_id = account_id, symbol = symbol, amount = number))
    session.commit()
  session.close()
  pass

def add_transaction(account_id, symbol, amount, price):
  session = sqlalchemy.orm.Session()
  check_account(account_id)
  if amount > 0:
    rows = session.query(Account).filter(Account.id == account_id).with_for_update().all()
    if rows[0].balance < amount * price:
      session.close()
      raise ValueError("No sufficient balance")
    rows[0].balance -= amount * price
    session.commit()
  else:
    rows = session.query(Position).filter(Position.account_id == account_id, Position.symbol == symbol).with_for_update().all()
    if rows is not None:
      amount = abs(amount)
      if rows[0].amount < amount:
        session.close()
        raise ValueError("No sufficient shares")
      rows[0].amount -= amount
    else:
      session.close()
      raise ValueError("No such symbol exist")
  transaction = Transaction(account_id = account_id, symbol = symbol, amount = amount, limit = price)
  transaction_id = transaction.transaction_id
  session.add(transaction)
  session.commit()
  session.close()
  add_status(transaction_id, "open", amount, price)
  return transaction_id

def add_status(transaction_id: int, status_name: str, shares: int, price: float):
  session = sqlalchemy.orm.Session()
  rows = session.query(Status).filter(Status.transaction_id == transaction_id).all()
  if rows is not None:
    session.close()
    raise ValueError("Current transaction already has a status")
  time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  session.add(Status(transaction_id = transaction_id, status_name = status_name, shares = shares, price = price, time = time))
  session.commit()
  session.close()
  pass

def query_transaction(account_id, transaction_id):
  session = sqlalchemy.orm.Session()
  query = session.query(Status).join(Transaction).join(Account)
  query = query.filter(Account.id == account_id)
  query = query.filter(Transaction.transaction_id == transaction_id)
  query = query.order_by(Status.status_id.asc())
  order = query.all()
  session.close()
  return order

