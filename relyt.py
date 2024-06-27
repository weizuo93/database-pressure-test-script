import hologres


def connect_and_query(sql_id, exec_seq, stmt, db_config):
    return hologres.connect_and_query(sql_id, exec_seq, stmt, db_config)
