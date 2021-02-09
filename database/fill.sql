/* Inserts BTC/USDT strategy */

INSERT INTO t_strategies (id, name, pair_name, coin, stable, step, bid, bottom, ceiling, active)
VALUES ('BTC/USDT_10', 'BTC/USDT 10%', 'XBTUSDT', 'XBT', 'USDT', 10, 0.0152, 30000, 100000, True)
;

INSERT INTO t_strategies (id, name, pair_name, coin, stable, step, bid, bottom, ceiling, active)
VALUES ('ETH/USDT_10', 'ETH/USDT 10%', 'ETHUSDT', 'ETH', 'USDT', 10, 0.32, 1000, 4000, True)
;
