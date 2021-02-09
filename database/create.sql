CREATE TABLE t_strategies (
	id varchar NOT NULL PRIMARY KEY,
    name varchar NOT NULL,
    pair_name varchar NOT NULL,
	coin varchar NOT NULL,
	stable varchar NOT NULL,
	step numeric NOT NULL,
	bid numeric NOT NULL,
    bottom numeric NOT NULL,
    ceiling numeric NOT NULL,
    active boolean NOT NULL
)
;

CREATE TABLE t_orders (
    id varchar NOT NULL PRIMARY KEY,
    strategy_id varchar NOT NULL REFERENCES t_strategies (id),
    type varchar NOT NULL,
    amount numeric NOT NULL,
    price numeric NOT NULL,
    open_position numeric NOT NULL,
    closed_position numeric NOT NULL,
    status varchar NOT NULL
)
;

CREATE TABLE t_robots (
    id varchar NOT NULL PRIMARY KEY,
    strategy_id varchar NOT NULL REFERENCES t_strategies (id),
    current_step_price numeric,
    sell_order_id varchar REFERENCES t_orders (id),
    buy_order_id varchar REFERENCES t_orders (id)
)
;

CREATE TABLE t_error_log(
    id serial PRIMARY KEY,
    created timestamp WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message varchar
)
;