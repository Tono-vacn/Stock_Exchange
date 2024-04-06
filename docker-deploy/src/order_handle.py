from db_model import *
from commons_func import *
from db_operation import *

def calculate_position(cur_order, cur_acc, cur_transc, cur_pos, cur_match_acc, cur_match_transc, cur_match_pos, order_status):
  
  order_shares = min(abs(cur_order.shares), abs(order_status.shares))
  if cur_order.shares > 0:
    cur_acc.balance -= (order_status.price - cur_transc.limit)*order_shares
    cur_match_acc.balance += (order_status.price)*order_shares
    if not cur_pos:
      add_position(cur_acc.id, cur_transc.symbol, order_shares)
    else:
      cur_pos.amount +=order_shares
  else:
    cur_acc.balance += order_status.price*order_shares
    if not cur_match_pos:
      add_position(cur_match_acc.id, cur_match_transc.symbol, order_shares)
    else:
      cur_match_pos.amount += order_shares


def get_match_order_list(cur_tran_lst, cur_order_to_match):
  if cur_tran_lst[0].amount == 0:
    return None
  if cur_tran_lst[0].amount>0:
    cur_match = cur_order_to_match.filter(Transaction.symbol == cur_tran_lst[0].symbol, 
                                          Transaction.amount <0 , 
                                          Status.status_name == 'open',
                                          Transaction.limit<=cur_tran_lst[0].limit).with_for_update().order_by(
      Transaction.limit, 
      Status.time
      ).all()
    pass
  else:
    cur_match = cur_order_to_match.filter(Transaction.symbol == cur_tran_lst[0].symbol, Transaction.amount >0 , Status.status_name == 'open',Transaction.limit>=cur_tran_lst[0].limit).with_for_update().order_by(
      Transaction.limit.desc(), 
      Status.time
      ).all()
    pass
  
  return cur_match
  
  
def execute_order_status(order_s):
  order_s.time = get_now_time()
  order_s.status_name = 'excecuted'

def get_order_transc_acc_pos(order_s,session):
  cur_match_transc = session.query(Transaction).filter(Transaction.transaction_id == order_s.transaction_id).with_for_update().first()
  cur_match_acc = session.query(Account).filter(Account.id == cur_match_transc.account_id).with_for_update().first()
  cur_match_pos = session.query(Position).filter(Position.account_id == cur_match_acc.id, Position.symbol == cur_match_transc.symbol).with_for_update().first()
  return cur_match_transc, cur_match_acc, cur_match_pos

def get_cur_order_acc_pos(cur_transc_s, session):
  cur_order = session.query(Status).filter(Status.transaction_id == cur_transc_s.transaction_id, 
                                           Status.status_name == 'open' # can be deleted
                                           ).with_for_update().first()
  # cur_transc = cur_tran_lst[0]
  cur_acc = session.query(Account).filter(Account.id == cur_transc_s.account_id).with_for_update().first()
  cur_pos = session.query(Position).filter(Position.account_id == cur_acc.id, Position.symbol == cur_transc_s.symbol).with_for_update().first()
  return cur_order, cur_acc, cur_pos
    

def match_given_order(tran_id):
  session = Session()
  cur_order_to_match = session.query(Status).join(Transaction).filter(Transaction.transaction_id == Status.transaction_id)
  cur_tran_lst = session.query(Transaction).filter(Transaction.transaction_id == tran_id).all()
  
  cur_match = get_match_order_list(cur_tran_lst, cur_order_to_match)
  
  if not cur_match:
    session.close()
    return None
  
  cur_transc = cur_tran_lst[0]
  
  cur_order, cur_acc, cur_pos = get_cur_order_acc_pos(cur_transc, session)
  
  for order in cur_match:
    cur_match_transc, cur_match_acc, cur_match_pos = get_order_transc_acc_pos(order, session)
    if abs(order.shares) == abs(cur_order.shares):
      
      order_status = session.query(Status).filter(Status.status_id == order.status_id).with_for_update().first()
      
      execute_order_status(order_status)
      
      execute_order_status(cur_order)
      
      cur_order.price = order_status.price
      
      calculate_position(cur_order, cur_acc, cur_transc, cur_pos, cur_match_acc, cur_match_transc, cur_match_pos, order_status)
      session.commit()
      break
    elif abs(order.shares) > abs(cur_order.shares):
      
      order_status = session.query(Status).filter(Status.status_id == order.status_id).with_for_update().first()
      
      order_status.shares += cur_order.shares
      session.add(Status(transaction_id = order_status.transaction_id, 
                                     status_name = 'excecuted', 
                                     shares = -cur_order.shares, 
                                     price = order_status.price, 
                                     time = get_now_time()))
      
      execute_order_status(cur_order)
      cur_order.price = order_status.price        
      calculate_position(cur_order, cur_acc, cur_transc, cur_pos, cur_match_acc, cur_match_transc, cur_match_pos, order_status)
      session.commit()
      break
    else:
      
      order_status = session.query(Status).filter(Status.status_id == order.status_id).with_for_update().first()
      execute_order_status(order_status)
      cur_order.shares += order_status.shares
      session.add(Status(transaction_id = cur_order.transaction_id, 
                                  status_name = 'excecuted', 
                                  shares = -order_status.shares, 
                                  price = order_status.price, 
                                  time = get_now_time()))

      calculate_position(cur_order, cur_acc, cur_transc, cur_pos, cur_match_acc, cur_match_transc, cur_match_pos, order_status)
      session.commit()
  session.close()
  pass

def check_existance(tran_id):
  session = Session()
  cur_tran = session.query(Transaction).filter(Transaction.transaction_id == tran_id).all()
  cur_or = session.query(Status).filter(Status.transaction_id == tran_id, Status.status_name == 'open').all() 
  if cur_or == [] or cur_tran == []: 
    raise ValueError("Invalid search for transaction or status")
  if cur_or[0].status_name != 'open':
    raise ValueError("Non-open transaction")
  session.close()
  pass

def process_order(tran_id):
  check_existance(tran_id)
  match_given_order(tran_id)