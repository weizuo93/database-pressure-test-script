import psycopg2
import time
from logger import LOG
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
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(stmt)

        '''
        index = cursor.description
        row = cursor.fetchone()
        while row:
            print("row: " + str(cursor.rownumber) + ". row : " + str(row))
            for i in range(len(index)):
                print(str(index[i][0]) + " : " + str(row[i]))
            row = cursor.fetchone()
        '''
        end_perf = time.perf_counter()
        end_time = datetime.now()
        succeed = True

    except (Exception, psycopg2.Error) as e:
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
