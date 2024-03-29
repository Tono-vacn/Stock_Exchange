import sqlalchemy
import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base

class Account(Base):
  __tablename__ = 'account'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True)
  balance = sqlalchemy.Column(sqlalchemy.Float)

class Position(Base):
  __tablename__ = 'position'
  user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('account.id'), primary_key=True)
  symbol = sqlalchemy.Column(sqlalchemy.TEXT, primary_key=True)
  amount = sqlalchemy.Column(sqlalchemy.Integer)


class Transaction(Base):
  __tablename__ = 'transaction'
  transaction_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
  user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('account.id'))
  symbol = sqlalchemy.Column(sqlalchemy.TEXT)
  amount = sqlalchemy.Column(sqlalchemy.Integer)
  limit = sqlalchemy.Column(sqlalchemy.Float)


class Status(Base):
  __tablename__ = 'status'
  status_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
  transaction_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('transaction.transaction_id'))
  name = sqlalchemy.Column(sqlalchemy.String)
  shares = sqlalchemy.Column(sqlalchemy.Integer)
  price = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
  time = sqlalchemy.Column(sqlalchemy.TIMESTAMP, nullable=True)