import doris
import hologres
import relyt
import random
import threading
import time
from datetime import datetime
from logger import LOG
import config
import sys


def parse_test_case(file_name):
    test_case = []
    file = open(file_name, "r", encoding='utf-8')
    line = file.readline()
    i = 1
    while line:
        line = line.strip()
        if line != "":
            query = {"id": "q" + str(i), "sql": line}
            test_case.append(query)
            i = i + 1
        line = file.readline()
    file.close()

    return test_case


def split_test_case(test_case, n):
    if len(test_case) < n:
        return [test_case[i::n] for i in range(n)]
    else:
        k, m = divmod(len(test_case), n)
        return [test_case[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def single_concurrency_service(service, current_time, test_name, concurrency, thread_name, test_case, db_config):
    shuffled_case = test_case[:]
    random.shuffle(shuffled_case)
    statistics = []
    if service == "doris":
        for j in range(len(shuffled_case)):
            res = doris.connect_and_query(shuffled_case[j]["id"], j + 1, shuffled_case[j]["sql"], db_config)
            statistics.append(res)
            if res["status"] == "Success":
                LOG.info("Succeed to test [" + service + "] [" + test_name + "] [concurrency-" + str(concurrency) +
                         "] case : [" + thread_name + ".case-" + str(j + 1) + "]. query_time : " + str(res["query_time"]) +
                         " ms.")
            else:
                LOG.info("Failed to test [" + service + "] [" + test_name + "] [concurrency-" + str(concurrency) +
                         "] case : [" + thread_name + ".case-" + str(j + 1) + "].")

    elif service == "hologres":
        for j in range(len(shuffled_case)):
            res = hologres.connect_and_query(shuffled_case[j]["id"], j + 1, shuffled_case[j]["sql"], db_config)
            statistics.append(res)
            LOG.info("Finish to test [" + service + "] [" + test_name + "] [concurrency-" + str(concurrency) +
                     "] case : [" + thread_name + ".case-" + str(j + 1) + "]. query_time : " + str(res["query_time"]) +
                     " ms.")
    elif service == "relyt":
        for j in range(len(shuffled_case)):
            res = relyt.connect_and_query(shuffled_case[j]["id"], j + 1, shuffled_case[j]["sql"], db_config)
            statistics.append(res)
            LOG.info("Finish to test [" + service + "] [" + test_name + "] [concurrency-" + str(concurrency) +
                     "] case : [" + thread_name + ".case-" + str(j + 1) + "]. query_time : " + str(res["query_time"]) +
                     " ms.")
    else:
        print("Exit. service name must be 'doris/hologres/relyt'")
        LOG.error("Exit. service name must be 'doris/hologres/relyt'")
        sys.exit(1)

    data = ""
    for k in range(len(statistics)):
        data = (data + str(current_time) + "|" + str(service) + "|" + str(test_name) + "|" + str(concurrency) + "|" +
                str(thread_name) + "|" + str(statistics[k]["sql_id"]) + "|" + str(statistics[k]["exec_seq"]))
        if statistics[k]["status"] == "Success":
            data = (data + "|Success|" + str(statistics[k]["query_time"]) + "|" + str(statistics[k]["start_time"]) +
                    "|" + str(statistics[k]["end_time"]) + "|" + str(statistics[k]["sql"]) + "|NULL")
        else:
            data = (data + "|Fail|NULL|" + str(statistics[k]["start_time"]) + "|NULL|" + str(statistics[k]["sql"]) +
                    "|" + str(statistics[k]["error_message"]))
        data = data + "\n"

    LOG.debug(thread_name + ". Start to duration statistics. statistics : " + str(data))
    resp = doris.stream_load(duration_env_config["host"], duration_env_config["port"], duration_env_config["db"],
                             duration_env_config["table"], duration_env_config["user"],
                             duration_env_config["password"],
                             test_name + "-" + concurrency + "-" + thread_name + "-" + str(int(time.time())), data)
    LOG.info(thread_name + " Finished. End to duration statistics. resp : " + str(resp.text))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Exit. Usage: python3 start_stress_test.py [service_name] [test_name] [concurrency] [case_mode]")
        LOG.error("Exit. Usage: python3 start_stress_test.py [service_name] [test_name] [concurrency] [case_mode]")
        sys.exit(1)

    service = sys.argv[1]
    if service != "doris" and service != "hologres" and service != "relyt":
        print("Exit. Usage: service_name must be doris/hologres/relyt")
        LOG.error("Exit. Usage: service_name must be doris/hologres/relyt")
        sys.exit(1)

    test_name = sys.argv[2]
    if test_name != "tpch_1t" and test_name != "tpch_10t" and test_name != "mqs":
        print("Exit. Usage: test_name must be tpch_1t/tpch_10t/mqs")
        LOG.error("Exit. Usage: test_name must be tpch_1t/tpch_10t/mqs")
        sys.exit(1)

    concurrency = sys.argv[3]
    try:
        if not isinstance(int(concurrency), int):
            print("Exit. Usage: concurrency must be type 'int'")
            LOG.error("Exit. Usage: concurrency must be type 'int'")
            sys.exit(1)
    except ValueError:
        print("Exit. Usage: concurrency must be type 'int'")
        LOG.error("Exit. Usage: concurrency must be type 'int'")
        sys.exit(1)

    case_mode = sys.argv[4]
    if case_mode != "split" and case_mode != "reuse":
        print("Exit. Usage: case_mode must be split/reuse")
        LOG.error("Exit. Usage: case_mode must be split/reuse")
        sys.exit(1)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG.info(
        "Start to test [" + str(service) + "] concurrently. test name : [" + str(test_name) + "]. concurrency : [" +
        str(concurrency) + "]. case mode : [" + str(case_mode) + "]. current time : " + str(current_time))

    test_env_config = None
    test_case_file = "test_case/"
    if service == "doris":
        if test_name == "tpch_1t":
            test_env_config = config.doris_tpch_1t_config
            test_case_file = test_case_file + "doris_tpch_case.txt"
        elif test_name == "tpch_10t":
            test_env_config = config.doris_tpch_10t_config
            test_case_file = test_case_file + "doris_tpch_case.txt"
        elif test_name == "mqs":
            test_env_config = config.doris_mqs_config
            test_case_file = test_case_file + "doris_mqs_case.txt"
        else:
            print("Exit. test name of doris must be 'tpch_1t/tpch_10t'")
            LOG.error("Exit. service name must be 'doris/hologres/relyt'")
            sys.exit(1)
    elif service == "hologres":
        test_env_config = config.hologres_tpch_config
        test_case_file = test_case_file + "hologres_tpch_case.txt"
    elif service == "relyt":
        test_env_config = config.relyt_tpch_config
        test_case_file = test_case_file + "relyt_tpch_case.txt"
    else:
        print("Exit. service name must be 'doris/hologres/relyt'")
        LOG.error("Exit. service name must be 'doris/hologres/relyt'")
        sys.exit(1)

    duration_env_config = config.result_duration_config
    test_case = parse_test_case(test_case_file)
    threads = []
    if case_mode == "reuse":
        for i in range(int(concurrency)):
            t = threading.Thread(target=single_concurrency_service, args=(
                str(service), str(current_time), str(test_name), str(concurrency), "thread-" + str(i + 1),
                test_case, test_env_config))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    elif case_mode == "split":
        split_cases = split_test_case(test_case, int(concurrency))
        for i in range(int(concurrency)):
            t = threading.Thread(target=single_concurrency_service, args=(
                str(service), str(current_time), str(test_name), str(concurrency), "thread-" + str(i + 1),
                split_cases[i], test_env_config))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    else:
        print("Exit. case mode must be 'split/reuse'")
        LOG.error("Exit. case mode must be 'split/reuse'")
        sys.exit(1)

    print("All test task has finished. service : " + str(service) + ", test name : " + str(test_name) +
          ", concurrency : " + str(concurrency) + ", case mode : " + str(case_mode) + ".")
    LOG.info("All test task has finished. service : " + str(service) + ", test name : " + str(test_name) +
             ", concurrency : " + str(concurrency) + ".")
