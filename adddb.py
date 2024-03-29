from db_model import *

session = sqlalchemy.orm.Session()
def addAccount(ID, BALANCE):
    # Make sure ID is larger and equal than 1
    if ID < 1:
        raise ValueError(
            "Account ID shouldn't be less than 1")

    if BALANCE < 0:
        session.close()
        raise ValueError(
            "Account Balance shouldn't be negative")
    account = session.query(Account).filter(Account.id == ID).all()
    if account is not None:
        session.close()
        raise ValueError("Account ID exists")
    try:
        account = Account(id=ID, balance=BALANCE)
        session.add(account)
        session.commit()
    except:
        session.flush()
        raise ValueError("Accounts exists")


session.close()