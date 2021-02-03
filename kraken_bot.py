from kraken_manager import get_open_orders
from kraken_manager import query_orders
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

    def __init__(self, strategy, current_price):
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

    @staticmethod
    def cancel_order(order):
        if order is not None:
            if order.status == 'open':
                try:
                    cancel_order(order.id)
                    order.status = 'cancel'
                    session.commit()
                except Exception as e:
                    print(e)
                    session.rollback()
                    raise KrakenBotError(e)

    def cancel_orders(self):
        # Check robot
        robot = self.strategy.robot
        if robot is None:
            raise KrakenBotError('Cancel_orders: There is no robot in strategy')

        # try to cancel orders
        try:
            self.cancel_order(robot.sell_order)
            self.cancel_order(robot.buy_order)
        except Exception as e:
            raise KrakenBotError(e)

    def start_robot(self):
        # Check if current price is in strategy boundaries
        if self.strategy.bottom <= self.current_price <= self.strategy.ceiling:
            # Create empty robot
            robot = Robot(id=str(uuid4()), strategy=self.strategy, current_step_price=self.current_price)
            robot.push()

            try:
                self.place_orders()
            except KrakenBotError as e:
                # In case of error delete the robot
                robot.delete()
                print('error during orders posting')

    def stop_robot(self):
        # Check if robot exists
        if self.strategy.robot is not None:
            self.cancel_orders()
            self.strategy.robot.delete()

    def step_up(self):
        robot = self.strategy.robot
        multiplicator = 1 + self.strategy.step/100
        if robot is not None:
            if robot.current_step_price is None:
                robot.current_step_price = self.current_price
            self.cancel_orders()
            robot.current_step_price = robot.current_step_price * multiplicator
            session.commit()
            self.place_orders()

    def step_down(self):
        robot = self.strategy.robot
        multiplicator = 1 + self.strategy.step/100
        if robot is not None:
            if robot.current_step_price is None:
                robot.current_step_price = self.current_price
            self.cancel_orders()
            robot.current_step_price = robot.current_step_price / multiplicator
            session.commit()
            self.place_orders()

    def current_price_step(self):
        robot = self.strategy.robot
        if robot is not None:
            if robot.current_step_price is None:
                robot.current_step_price = self.current_price
            elif self.current_price > robot.current_step_price:
                self.step_up()
            else:
                self.step_down()

    def run_robot(self):
        if self.strategy:
            if self.strategy.robot is not None:
                robot = self.strategy.robot

                # Arguments to make step decision
                buy_order_is_open = False
                sell_order_is_open = False

                if robot.buy_order is not None:
                    if robot.buy_order.status == 'open':
                        buy_order_is_open = True

                if robot.sell_order is not None:
                    if robot.sell_order.status == 'open':
                        sell_order_is_open = True

                # Make decision
                if buy_order_is_open and sell_order_is_open:
                    return
                elif buy_order_is_open:
                    self.step_up()
                elif sell_order_is_open:
                    self.step_down()
                else:
                    self.current_price_step()

            else:
                self.start_robot()
        else:
            self.stop_robot()


def kraken_bot():
    # noinspection PyBroadException
    try:
        # Get all strategies
        strategies = Strategy.get_all()

        # Get current prices
        pairs = []
        for strategy in strategies:
            if strategy.pair_name not in pairs:
                pairs.append(strategy.pair_name)

        current_prices = get_current_price(pairs)

        # Update all open orders
        orm_orders = Order.get_by_status('open')
        orders_id_list = []
        for orm_order in orm_orders:
            orders_id_list.append(orm_order.id)
        kraken_orders = query_orders(orders_id_list)

        for orm_order in orm_orders:
            if orm_order.id in kraken_orders.keys():
                kraken_order = kraken_orders[orm_order.id]
                orm_order.status = kraken_order['status']
                orm_order.open_position = kraken_order['open_position']
                orm_order.closed_position = kraken_order['closed_position']
                session.commit()

        # Call strategies
        for strategy in strategies:
            bot = Bot(strategy, current_prices[strategy.pair_name])
            bot.run_robot()
    except Exception as e:
        print(e)

