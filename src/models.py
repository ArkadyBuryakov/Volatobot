# Create classes stored in database
# with sqlalchemy meta
from sqlalchemy import (
    Column, String, Numeric, Boolean, ForeignKey, Integer, DateTime, Text,
)
from sqlalchemy.orm import relationship

from orm import Base, new_session


class Strategy(Base):
    # Table
    __tablename__ = "t_strategies"

    # Columns
    id = Column(String, primary_key=True)
    name = Column(String)
    pair_name = Column(String)
    coin = Column(String)
    stable = Column(String)
    step = Column(Numeric)
    bid = Column(Numeric)
    bottom = Column(Numeric)
    ceiling = Column(Numeric)
    active = Column(Boolean)

    # Related objects
    robot = relationship('Robot', uselist=False, back_populates='strategy')

    @staticmethod
    def get_all(session):
        return session.query(Strategy).all()

    @staticmethod
    def find(session, strategy_id):
        return session.query(Strategy).filter(Strategy.id == strategy_id).first()


class Order(Base):
    # Table
    __tablename__ = 't_orders'

    # Columns
    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey('t_strategies.id'))
    type = Column(String)
    amount = Column(Numeric)
    price = Column(Numeric)
    open_position = Column(Numeric)
    closed_position = Column(Numeric)
    status = Column(String)

    # Related objects
    strategy = relationship('Strategy')

    @staticmethod
    def get_all(session):
        return session.query(Order).all()

    @staticmethod
    def get_by_status(session, status):
        return session.query(Order).filter(Order.status == status).all()

    @staticmethod
    def find(session, order_id: str):
        return session.query(Order).filter(Order.id == order_id).first()

    def push(self, session):
        session.add(self)


class Robot(Base):
    # Table
    __tablename__ = 't_robots'

    # Columns
    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey('t_strategies.id'))
    current_step_price = Column(Numeric)
    sell_order_id = Column(String, ForeignKey('t_orders.id'))
    buy_order_id = Column(String, ForeignKey('t_orders.id'))
    status = Column(String, default='stopped')

    # Related objects
    strategy = relationship('Strategy', back_populates='robot')
    sell_order = relationship('Order', foreign_keys=[sell_order_id])
    buy_order = relationship('Order', foreign_keys=[buy_order_id])

    @staticmethod
    def get_all(session):
        return session.query(Robot).all()

    @staticmethod
    def find(session, robot_id: str):
        return session.query(Robot).filter(Robot.id == robot_id).first()

    def push(self, session):
        session.add(self)

    def delete(self, session):
        session.delete(self)


class Error(Base):
    # Table
    __tablename__ = 't_error_log'

    # Columns
    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    message = Column(Text)

    @staticmethod
    def post(message):
        session = new_session()
        error = Error(message=message)
        session.add(error)
        session.commit()
        session.close()
