from settings import db_settings
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Set a database connection
engine = create_engine(db_settings)
session = sessionmaker(bind=engine)()
Base = declarative_base()


# Create a class for settings stored in database
class Strategy(Base):
    __tablename__ = "t_strategies"

    id = Column(String, primary_key=True)
    name = Column(String)
    pair_name = Column(String)
    coin = Column(String)
    stable = Column(String)
    step = Column(String)
    bid = Column(Numeric)
    bottom = Column(Numeric)
    ceiling = Column(Numeric)
    active = Column(Boolean)

    # Related objects
    robot = relationship('Robot', uselist=False, back_populates='strategy')

    @staticmethod
    def get_all():
        return session.query(Strategy).all()

    @staticmethod
    def find(strategy_id):
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
    def get_all():
        return session.query(Order).all()

    @staticmethod
    def get_by_status(status):
        return session.query(Order).filter(Order.status == status).all()

    @staticmethod
    def find(order_id: str):
        return session.query(Order).filter(Order.id == order_id).first()

    def push(self):
        session.add(self)
        session.commit()


class Robot(Base):
    # Table
    __tablename__ = 't_robots'

    # Columns
    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey('t_strategies.id'))
    current_step_price = Column(Numeric)
    sell_order_id = Column(String, ForeignKey('t_orders.id'))
    buy_order_id = Column(String, ForeignKey('t_orders.id'))

    # Related objects
    strategy = relationship('Strategy', back_populates='robot')
    sell_order = relationship('Order', foreign_keys=[sell_order_id])
    buy_order = relationship('Order', foreign_keys=[buy_order_id])

    @staticmethod
    def get_all():
        return session.query(Robot).all()

    @staticmethod
    def find(robot_id: str):
        return session.query(Robot).filter(Robot.id == robot_id).first()

    def push(self):
        session.add(self)
        session.commit()

    @staticmethod
    def commit():
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()
