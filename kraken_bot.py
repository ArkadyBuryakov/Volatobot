from kraken_manager import query_orders
from kraken_manager import get_current_price
from kraken_manager import post_order
from kraken_manager import cancel_order
from orm import new_session
from orm import Error
from orm import Order
from orm import Robot
from orm import Strategy
from telegram_manager import send_telegram_message
from uuid import uuid4


class KrakenBotError(Exception):
    pass


class Bot:

    def __init__(self, strategy_id, current_price):
        self.session = new_session()
        self.strategy = Strategy.find(self.session, strategy_id)
        self.current_price = current_price

    def place_orders(self):
        session = self.session
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
            if self.strategy.bottom <= sell_price <= self.strategy.ceiling:
                # Publish order
                sell_order_result = post_order(pair=pair,
                                               type='sell',
                                               price=sell_price,
                                               volume=sell_volume)

                # Add to database
                sell_order = Order(id=sell_order_result['id'],
                                   strategy_id=strategy_id,
                                   type='sell',
                                   amount=sell_volume,
                                   price=sell_price,
                                   open_position=sell_volume,
                                   closed_position=0,
                                   status='open')
                sell_order.push(session)
                robot.sell_order = sell_order

                # Add to orders list for error handling
                orders.append(sell_order)

            # Post buy order
            if self.strategy.bottom <= buy_price <= self.strategy.ceiling:
                # Publish order
                buy_order_result = post_order(pair=pair,
                                              type='buy',
                                              price=buy_price,
                                              volume=buy_volume)

                # Add to database
                buy_order = Order(id=buy_order_result['id'],
                                  strategy_id=strategy_id,
                                  type='buy',
                                  amount=buy_volume,
                                  price=buy_price,
                                  open_position=buy_volume,
                                  closed_position=0,
                                  status='open')
                buy_order.push(session)
                robot.buy_order = buy_order

                # Add to orders list for error handling
                orders.append(buy_order)

            # Commit on success
            session.commit()

        except Exception as e:
            # Cancel all changes in session
            session.rollback()

            # Cancel orders
            for order in orders:
                cancel_order(order.id)
                order.status = 'cancel'
                session.commit()

            raise KrakenBotError('place_orders: ' + str(e))

    def cancel_order(self, order):
        session = self.session
        if order is not None:
            if order.status == 'open':
                try:
                    cancel_order(order.id)
                    order.status = 'cancel'
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise KrakenBotError('cancel_order: ' + str(e))

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
            raise KrakenBotError('cancel_orders: ' + str(e))

    def start_robot(self):
        # Check if current price is in strategy boundaries
        if self.strategy.bottom <= self.current_price <= self.strategy.ceiling:
            session = self.session
            try:
                # Create empty robot
                robot = Robot(id=str(uuid4()), strategy=self.strategy, current_step_price=self.current_price)
                robot.push(session)
                session.commit()
            except Exception as e:
                session.rollback()
                raise KrakenBotError('start_robot: ' + str(e))

            try:
                self.place_orders()
            except KrakenBotError as e:
                # In case of error delete the robot
                robot.delete(session)
                session.commit()
                raise KrakenBotError('start_robot: ' + str(e))

    def stop_robot(self):
        session = self.session
        try:
            # Check if robot exists
            if self.strategy.robot is not None:
                self.cancel_orders()
                self.strategy.robot.delete(session)
                session.commit()
        except Exception as e:
            session.rollback()
            raise KrakenBotError('stop_robot: ' + str(e))

    def step_up(self):
        session = self.session
        try:
            # Get robot
            robot = self.strategy.robot

            # Check if robot exists
            if robot is None:
                raise KrakenBotError('robot does not exist')

            # Calculate new price
            if robot.current_step_price is None:
                robot.current_step_price = self.current_price
            multiplicator = 1 + self.strategy.step/100
            new_price = robot.current_step_price * multiplicator

            # Check if new price lies in given range
            if new_price <= self.strategy.ceiling:

                # Perform step up operation
                self.cancel_orders()
                robot.current_step_price = new_price
                session.commit()
                self.place_orders()

                # Inform about step
                send_telegram_message(f'Step up!\n'
                                      f'Strategy: {self.strategy.name}\n'
                                      f'New price: {robot.current_step_price}')

        except Exception as e:
            session.rollback()
            raise KrakenBotError('step_up: ' + str(e))

    def step_down(self):
        session = self.session
        try:
            # Get robot
            robot = self.strategy.robot
            # Check if robot exists
            if robot is None:
                raise KrakenBotError('robot does not exist')

            # Calculate new price
            if robot.current_step_price is None:
                robot.current_step_price = self.current_price
            multiplicator = 1 + self.strategy.step/100
            new_price = robot.current_step_price / multiplicator

            # Check if new price lies in given range
            if new_price >= self.strategy.bottom:

                # Perform step down operation
                self.cancel_orders()
                robot.current_step_price = new_price
                session.commit()
                self.place_orders()

                # Inform about step
                send_telegram_message(f'Step down!\n'
                                      f'Strategy: {self.strategy.name}\n'
                                      f'New price: {robot.current_step_price}')

        except Exception as e:
            session.rollback()
            raise KrakenBotError('step_down: ' + str(e))

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
        try:
            # Check if strategy is active
            if self.strategy.active:
                # Check that robot exists
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
                    # Start new robot if it doesn't exist
                    self.start_robot()
            else:
                # Stop robot if strategy is not active
                self.stop_robot()
        except Exception as e:
            raise KrakenBotError('run_robot: ' + str(e))
        finally:
            self.session.close()


def kraken_bot():
    session = new_session()
    # noinspection PyBroadException
    try:
        # Get all strategies
        strategies = Strategy.get_all(session)

        # Get current prices
        pairs = []
        for strategy in strategies:
            if strategy.pair_name not in pairs:
                pairs.append(strategy.pair_name)

        current_prices = get_current_price(pairs)

        # Update all open orders
        orm_orders = Order.get_by_status(session, 'open')
        orders_id_list = []
        for orm_order in orm_orders:
            orders_id_list.append(orm_order.id)
        if len(orders_id_list) > 0:
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
            bot = Bot(strategy.id, current_prices[strategy.pair_name])
            bot.run_robot()

    except Exception as e:
        # Print error
        print('kraken_bot: ' + str(e))
        # noinspection PyBroadException
        try:
            # Send error to DB log
            Error.post('kraken_bot: ' + str(e))
            # Send error notification
            send_telegram_message('Error happened: kraken_bot: ' + str(e))
        except Exception as e:
            pass

    finally:
        session.close()
