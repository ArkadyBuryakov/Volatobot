select * from t_strategies;
select * from t_orders;
select * from t_robots;

insert into t_orders(id, strategy_id, type, amount, price, open_position, closed_position, status)
VALUES ('123', 'BTC/USDT', 'sell', 0.001, 30000, 30000, 0, 'opened')
;

delete from t_robots where True;

commit;