from db_model import *
from datetime import *

def drop_all():
  Base.metadata.drop_all(engine)

def drop_all_and_init():
  Base.metadata.drop_all(engine)
  Base.metadata.create_all(engine)

def add_account(id: str, balance: float):
  session = Session()
  if balance < 0:
    session.close()
    raise ValueError("Balance is negative")
  # if 'account' in metadata.tables:
  exist_account = session.query(Account).filter(Account.id == id).all()
  if exist_account != []:
    session.close()
    raise ValueError("Account id exists")
  try:
    session.add(Account(id = id, balance = balance))
    session.commit()
    session.close()
  except:
    session.rollback()
    session.close()
    raise ValueError("Accounts already exists")
  session.close()
  pass

def check_account(account_id: str):
  session = Session()
  exist_account = session.query(Account).filter(Account.id == account_id).all()
  
  # print("query done")
  if exist_account != []:
    session.close()
    return True
  session.close()
  return False

def add_position(account_id: str ,symbol: str, number: int):
  session = Session()
  if not check_account(account_id):
    session.close()
    raise ValueError("No such account")

  if number < 0:
    session.close()
    raise ValueError("No short allowed")
  
  # if 'position' in metadata.tables:
  try:
    rows = session.query(Position).filter(Position.account_id == account_id, Position.symbol == symbol).with_for_update().all()
    if rows != []:
      for row in rows:
        row.amount += number
    else:
      session.add(Position(account_id = account_id, symbol = symbol, amount = number))
    session.commit()
    session.close()
  except:
    session.rollback()
    session.close()
    raise ValueError("Position already exists")
  # else:
  #   session.add(Position(account_id = account_id, symbol = symbol, amount = number))
  session.close()
  pass

def add_transaction(account_id, symbol, amount, price):
  session = Session()
  if not check_account(account_id):
    session.close()
    raise ValueError("No such account")
  
  if amount > 0:
    rows = session.query(Account).filter(Account.id == account_id).with_for_update().all()
    if rows[0].balance < amount * price:
      session.close()
      raise ValueError("No sufficient balance")
    rows[0].balance -= amount * price
    session.commit()
  else:
    rows = session.query(Position).filter(Position.account_id == account_id, Position.symbol == symbol).with_for_update().all()
    if rows != []:
      if rows[0].amount < abs(amount):
        session.close()
        raise ValueError("No sufficient shares")
      rows[0].amount += amount
    else:
      session.close()
      raise ValueError("No such symbol exist")
  transaction = Transaction(account_id = account_id, symbol = symbol, amount = amount, limit = price)
  session.add(transaction)
  session.commit()
  transaction_id = transaction.transaction_id
  session.close()
  add_status(transaction_id, "open", amount, price)
  return transaction_id

def add_status(transaction_id: int, status_name: str, shares: int, price: float):
  session = Session()
  time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  session.add(Status(transaction_id = transaction_id, status_name = status_name, shares = shares, price = price, time = time))
  session.commit()
  session.close()
  pass

def query_transaction(account_id, transaction_id, session):
  # session = Session()
  query = session.query(Status).join(Transaction).join(Account)
  query = query.filter(Account.id == account_id)
  query = query.filter(Transaction.transaction_id == transaction_id)
  query = query.order_by(Status.status_id.asc())
  order = query.all()
  # result = list(order)
  # session.commit()
  # session.close()
  return order

def cancel_transaction(account_id, transaction_id,session):
  # session = Session()
  query = session.query(Status).join(Transaction).join(Account)
  query = query.filter(Account.id == account_id)
  status = query.filter(Transaction.transaction_id == transaction_id)
  if status.count() == 0:
    session.close()
    raise ValueError("No such transaction exist")
  status_rows = status.filter(Status.status_name == "open").with_for_update().all()
  if status_rows == []:
    session.close()
    raise ValueError("A non-open transaction can't be canceled")
  is_buy = status_rows[0].shares > 0
  status_rows[0].status_name = 'canceled'
  time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  status_rows[0].time = time
  session.commit()
  account_rows = session.query(Account).filter(Account.id == account_id).with_for_update().all()
  symbol_rows = session.query(Transaction).filter(Transaction.transaction_id == transaction_id).all()
  if is_buy:
    account_rows[0].balance += status_rows[0].shares * status_rows[0].price
    session.commit()
  else:
    shares = status_rows[0].shares
    account_id = account_rows[0].id
    symbol = symbol_rows[0].symbol
    position_rows = session.query(Position).filter(Position.account_id == account_id, Position.symbol == symbol).with_for_update().all()
    position_rows[0].amount -= shares
    session.commit()
  # session.close()
  order = query_transaction(account_id, transaction_id, session)
  return order