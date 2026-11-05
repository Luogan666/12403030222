学号：12403030222
姓名：张三
个人参数：S=22, A=1, B=2, C=2
运行环境：Python 3.10+ (依赖库 pymongo, redis)
数据库环境：MongoDB 8.3.11 (单节点副本集 rs0), Redis 三主三从集群 (端口 30222-30227)

各题执行方法：
- task1：使用 mongosh 执行 task1_init.js 初始化数据，再执行 task1_commands.js 进行业务操作。
- task2：直接在终端运行 python task2.py 即可测试四个事务场景。
- task3：直接在终端运行 python test3.py 即可测试 Redis 数据结构及过期。
- task4：直接在终端运行 python task4.py 测试逐条写入与 Pipeline 的性能对比。