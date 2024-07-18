import pymysql
import time
from logger import LOG
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime


def connect_and_query(sql_id, exec_seq, stmt, db_config):
    result = {}
    succeed = False
    error_message = None
    conn = None
    cursor = None

    end_perf = None
    end_time = None
    start_time = datetime.now()
    start_perf = time.perf_counter()
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(stmt)

        '''
        row = cursor.fetchone()
        while row:
            print("row: " + str(cursor.rownumber) + ". row : " + str(row))
            for key, value in row.items():
                print(str(key) + " : " + str(value))
            row = cursor.fetchone()
        '''
        end_perf = time.perf_counter()
        end_time = datetime.now()
        succeed = True

    except (Exception, pymysql.Error) as e:
        error_message = str(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if succeed:
        query_time = (end_perf - start_perf) * 1000
        result["status"] = "Success"
        result["query_time"] = str(query_time)
        result["end_time"] = str(end_time)
    else:
        LOG.warning("Fail. sql : " + str(stmt) + ". ErrorMsg : " + str(error_message))
        result["status"] = "Fail"
        result["error_message"] = str(error_message).replace("\n", " ")

    result["sql_id"] = str(sql_id)
    result["exec_seq"] = str(exec_seq)
    result["sql"] = str(stmt)
    result["start_time"] = str(start_time)

    return result


def stream_load(host, port, db, table, username, password, label, data):
    url = 'http://%s:%s/api/%s/%s/_stream_load' % (host, port, db, table)
    headers = {
        'Content-Type': 'text/plain; charset=UTF-8',
        'label': label,
        'format': 'csv',
        'line_delimiter': '\\n',
        'column_separator': '|',
        'Expect': '100-continue',
    }
    auth = HTTPBasicAuth(username, password)
    session = requests.sessions.Session()
    session.should_strip_auth = lambda old_url, new_url: False  # Don't strip auth

    resp = session.request(
        'PUT', url=url,
        data=data.encode('utf-8'),  # open('/path/to/your/data.csv', 'rb'),
        headers=headers, auth=auth
    )
    return resp