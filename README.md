## 1. 测试命令介绍

测试启动命令：
```commandline
python3 start_stress_test.py [service_name] [test_name] [concurrency] [case_mode]
```
参数介绍：

* service_name: 表示要压测的数据库服务名称，在该脚本中可选`doris`、`hologres`或`relyt`。doris数据库为MySQL语法，hologres和relyt数据为postgresSQL语法。

* test_name:表示测试的项目名称，在该脚本中可选`tpch_1t`、`tpch_10t`、`mqs`。

* concurrency：表示要压测的并发，取值为整型数值，比如吧`1`、`5`、`10`、`100`等。

* case_mode：表示测试用例的使用模式，可选`split`和`reuse`两种模式。`split`模式表示将全量测试case根据压测并发平均分成多份，每个并发使用其中一份，每个测试并发提交的查询Query不会重复。`reuse`模式表示每个并发使用全量的测试case，每个测试并发会将全量测试case的顺序打乱提交。

## 2. 数据库配置

数据库配置文件为`config.py`，其中可以配置各个压测数据库和测试项目连接信息。

例如：
```commandline
doris_tpch_1t_config = {
    'host': '',
    'port': 10000,
    'user': '',
    'password': '',
    'db': 'tpch_1t',
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
```

## 3. 测试Case

测试Case的文本文件存放在`test_case/`目录下，比如：doris_tpch_case.txt。

注意：
* 一个测试SQL文本需要保存在一行，不能跨行
* 相邻的两个测试SQL之间通过换行符分割
* 任意两个测试SQL之间不能有空行。
* 最后一个测试SQL之后不能有空行。

备注：改测试工具对每一个测试SQL和数据库均使用短连接，每一个测试SQL提交之前都需要向数据库发起连接，执行结束之后会主动关闭连接。

## 4. 测试结果审计

所有测试SQL的执行结果最终均会写入一张Doris表中，这张Doris表所在的数据库配置信息同样保存在`config.py`文件中。

```commandline
result_duration_config = {
    'host': '',
    'port': 80,
    'user': 'root',
    'password': '',
    'db': 'stress_test_audit_db',
    'table': 'stress_test_audit_tbl',
    'cursorclass': pymysql.cursors.DictCursor
}
```

审计表结构如下：
```commandline
CREATE TABLE `stress_test_audit_tbl` (
  `test_time` datetime NULL COMMENT '测试启动时间',
  `service_name` varchar(64) NULL COMMENT '测试的数据库服务名称',
  `test_name` varchar(256) NULL COMMENT '测试的项目名称',
  `concurrency` int(11) NULL COMMENT '测试的查询并发',
  `thread_name` varchar(64) NULL COMMENT '查询SQL所在的线程名称',
  `sql_id` varchar(64) NULL COMMENT '查询SQL ID',
  `exec_seq` int(11) NULL COMMENT '查询SQL在线程中的提交顺序',
  `status` varchar(64) NULL COMMENT '查询SQL执行结果状态',
  `query_time` DECIMAL(9, 3) NULL COMMENT '查询SQL执行时间',
  `start_time` varchar(256) NULL COMMENT '查询SQL提交执行时间',
  `end_time` varchar(256) NULL COMMENT '查询SQL执行结束时间',
  `stmt` varchar(*) NULL COMMENT '查询SQL文本',
  `error_message` varchar(*) NULL COMMENT '查询报错信息文本'
) ENGINE=OLAP
DUPLICATE KEY(`test_time`, `service_name`, `test_name`, `concurrency`, `thread_name`, `sql_id`)
COMMENT 'OLAP'
DISTRIBUTED BY HASH(`test_time`, `service_name`, `test_name`, `concurrency`, `thread_name`, `sql_id`) BUCKETS 4
PROPERTIES (
"replication_allocation" = "tag.location.default: 3"
);
```