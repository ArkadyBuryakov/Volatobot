from kraken_manager import get_open_orders
from kraken_manager import get_current_price
from kraken_manager import post_order
from kraken_manager import cancel_order
from kraken_manager import KrakenApiError
from orm import Order
from orm import Robot
from orm import Strategy
from orm import session
from uuid import uuid4


class KrakenBotError(Exception):
    pass


class Bot:

    def __init__(self, strategy: Strategy, current_price: float):
        self.strategy = strategy
        self.current_price = current_price

    def place_orders(self):
        robot = self.strategy.robot
        multiplicator = (1 + self.strategy.step / 100)
        orders = []

        try:
            # Get all valuable parameters
            strategy_id = self.strategy.id
            pair = self.strategy.pair_name
            sell_price = round(robot.current_step_price * multiplicator, 1)
            sell_volume = self.strategy.bid
            buy_price = round(robot.current_step_price / multiplicator, 1)
            buy_volume = self.strategy.bid*multiplicator

            # Post sell order
            sell_order_result = post_order(pair=pair,
                                           type='sell',
                                           price=sell_price,
                                           volume=sell_volume)
            sell_order = Order(id=sell_order_result['id'],
                               strategy_id=strategy_id,
                               type='sell',
                               amount=sell_volume,
                               price=sell_price,
                               open_position=sell_volume,
                               closed_position=0,
                               status='open')
            orders.append(sell_order)

            # Post buy order
            buy_order_result = post_order(pair=pair,
                                          type='buy',
                                          price=buy_price,
                                          volume=buy_volume)
            buy_order = Order(id=buy_order_result['id'],
                              strategy_id=strategy_id,
                              type='buy',
                              amount=buy_volume,
                              price=buy_price,
                              open_position=buy_volume,
                              closed_position=0,
                              status='open')
            orders.append(buy_order)

            # Save orders and link them to robot
            sell_order.push()
            buy_order.push()

            robot.sell_order = sell_order
            robot.buy_order = buy_order
            session.commit()

        except Exception as e:
            # In case of errors, cancel orders
            print(e)

            # Cancel all changes in session
            session.rollback()

            # Cancel orders
            for order in orders:
                cancel_order(order.id)
                order.status = 'cancel'
                session.commit()

            raise KrakenBotError(e)

    def start_robot(self):
        # Check if current price is in strategy boundaries
        if self.strategy.bottom <= self.current_price <= self.strategy.ceiling:
            # Create empty robot
            robot = Robot(id=str(uuid4()), strategy=self.strategy, current_step_price=self.current_price)
            robot.push()
            orders = {}

            try:
                orders = self.place_orders()
            except KrakenBotError as e:
                # In case of error delete the robot
                robot.delete()
                print('error during orders posting')


    def stop_robot(self):
        pass

    def step_up(self):
        pass

    def step_down(self):
        pass

    def current_price_step(self):
        pass

    def run_robot(self):
        pass


def kraken_bot():
    pass


