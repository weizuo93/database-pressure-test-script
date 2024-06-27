import pymysql


doris_tpch_1t_config = {
    'host': '',
    'port': 10000,
    'user': '',
    'password': '',
    'db': 'tpch_1t',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

doris_tpch_10t_config = {
    'host': '',
    'port': 10000,
    'user': '',
    'password': '',
    'db': 'tpch_10t',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

doris_mqs_config = {
    'host': '',
    'port': 10000,
    'user': '',
    'password': '',
    'db': '',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

hologres_tpch_config = {
    "host": "",
    "database": "",
    "user": "",
    "password": "",
    "port": "80",
}

relyt_tpch_config = {
    "host": "",
    "database": "",
    "user": "",
    "password": "",
    "port": "",
}

result_duration_config = {
    'host': '',
    'port': 80,
    'user': '',
    'password': '',
    'db': 'stress_test_audit_db',
    'table': 'stress_test_audit_tbl',
    'cursorclass': pymysql.cursors.DictCursor
}
