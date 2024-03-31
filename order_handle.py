from db_model import *
from commons_func import *
from db_operation import *

def match_given_order(tran_id):
  session = sqlalchemy.orm.Session()
  cur_order_to_match = session.query(Status).join(Transaction).filter(Transaction.transaction_id == Status.status_id)
  cur_tran_lst = session.query(Transaction).filter(Transaction.transaction_id == tran_id).all()
  
  if cur_tran_lst[0].amount == 0:
    return None
  
  if cur_tran_lst[0].amount>0:
    cur_match = cur_order_to_match.filter(Transaction.symbol == cur_tran_lst[0].symbol, Transaction.amount <0 , Status.status_name == 'open',Transaction.limit<=cur_tran_lst[0].limit).with_for_update().order_by(
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
  #   raise ValueError("Invalid amount")
  
  cur_order = session.query(Status).filter(Status.transaction_id == tran_id, Status.status_name == 'open').with_for_update().first()
  cur_transc = cur_tran_lst[0]
  cur_acc = session.query(Account).filter(Account.id == cur_transc.account_id).with_for_update().first()
  cur_pos = session.query(Position).filter(Position.account_id == cur_acc.id, Position.symbol == cur_transc.symbol).with_for_update().first()
  
  for order in cur_match:
    cur_match_transc = session.query(Transaction).filter(Transaction.transaction_id == order.transaction_id).with_for_update().first()
    cur_match_acc = session.query(Account).filter(Account.id == cur_match_transc.account_id).with_for_update().first()
    cur_match_pos = session.query(Position).filter(Position.account_id == cur_match_acc.id, Position.symbol == cur_match_transc.symbol).with_for_update().first()
    
    if abs(order.shares) == abs(cur_order.shares):
      order_status = session.query(Status).filter(Status.status_id == order.status_id).with_for_update().first()
      
      order_status.time = get_now_time()
      order_status.status_name = 'excecuted'
      
      cur_order.time = get_now_time()
      cur_order.status_name = 'excecuted'
      
      cur_order.price = order_status.price
      
      if cur_order.shares > 0:
        cur_acc.balance -= (order_status.price - cur_transc.limit)*abs(cur_order.shares)
        
        if not cur_pos:
          add_position(cur_acc.id, cur_transc.symbol, abs(cur_order.shares))
        else:
          cur_pos.amount += abs(cur_order.shares)
      else:
        cur_acc.balance += order_status.price*abs(cur_order.shares)
        
        if not cur_match_pos:
          add_position(cur_match_acc.id, cur_match_transc.symbol, abs(cur_order.shares))
          
        else:
          cur_match_pos.amount += abs(cur_order.shares) 
      session.commit()
      break
    elif abs(order.shares) > abs(cur_order.shares):
      order_status = session.query(Status).filter(Status.status_id == order.status_id).with_for_update().first()
      
      order_status.shares += cur_order.shares
      
      ###constructer?###
      order_status_executed = Status(transaction_id = order_status.transaction_id, 
                                     status_name = 'excecuted', 
                                     shares = -cur_order.shares, 
                                     price = order_status.price, 
                                     time = get_now_time())
      session.add(order_status_executed)
      
      cur_order.status_name = 'excecuted'
      cur_order.price = order_status.price
      cur_order.time = get_now_time()
      
      if cur_order.shares > 0:
        cur_acc.balance -= (order_status.price - cur_transc.limit)*abs(cur_order.shares)
        
        if not cur_pos:
          add_position(cur_acc.id, cur_transc.symbol, abs(cur_order.shares))
        else:
          cur_pos.amount += abs(cur_order.shares)
      else:
        cur_acc.balance += order_status.price*abs(cur_order.shares)
        
        if not cur_match_pos:
          add_position(cur_match_acc.id, cur_match_transc.symbol, abs(cur_order.shares))
        else:
          cur_match_pos.amount += abs(cur_order.shares)
      session.commit()
      break
    else:
      order_status = session.query(Status).filter(Status.status_id == order.status_id).with_for_update().first()
      
      order_status.time = get_now_time()
      cur_order.shares += order_status.shares
      cur_order_executed = Status(transaction_id = cur_order.transaction_id, 
                                  status_name = 'excecuted', 
                                  shares = -order_status.shares, 
                                  price = order_status.price, 
                                  time = get_now_time())
      session.add(cur_order_executed)
      order_status.status_name = 'excecuted'
      
      if cur_order.shares > 0:
        cur_acc.balance -= (order_status.price - cur_transc.limit)*abs(order_status.shares)
        
        if not cur_pos:
          add_position(cur_acc.id, cur_transc.symbol, abs(order_status.shares))
        else:
          cur_pos.amount += abs(order_status.shares)
      else:
        cur_acc.balance += order_status.price*abs(order_status.shares)
        
        if not cur_match_pos:
          add_position(cur_match_acc.id, cur_match_transc.symbol, abs(order_status.shares))
        else:
          cur_match_pos.amount += abs(order_status.shares)
        session.commit()
  session.close()
  pass

def check_existance(tran_id):
  session = sqlalchemy.orm.Session()
  cur_tran = session.query(Transaction).filter(Transaction.transaction_id == tran_id).all()
  cur_or = session.query(Status).filter(Status.transaction_id == tran_id, Status.status_name == 'open').all() 
  if not cur_or or not cur_tran: 
  # or cur_or[0].status_name != 'open':
  #   return False
  # return True
    raise ValueError("Invalid search for transaction or status")
  if cur_or[0].status_name != 'open':
    raise ValueError("Non-open transaction")
  pass

def process_order(tran_id):
  check_existance(tran_id)
  match_given_order(tran_id)