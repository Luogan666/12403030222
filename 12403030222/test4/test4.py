from redis.cluster import RedisCluster, ClusterNode
import time

# 连接你的 Redis 集群
startup_nodes = [
    ClusterNode(host="127.0.0.1", port=30222),
    ClusterNode(host="127.0.0.1", port=30223),
    ClusterNode(host="127.0.0.1", port=30224)
]
r = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

SID = "12403030222"
N = 1222  # 1000 + 100*C + S
Q = 100   # 每批最多 100 条

print(f"==== 第四题 Pipeline 性能比较 (N={N}, Q={Q}) ====\n")

# ==========================================
# 方案甲：逐条写入（每次命令收到返回后，再发送下一条）
# ==========================================
print("正在执行方案甲：逐条写入...")
start_time = time.time()

for i in range(1, N + 1):
    r.set(f"exam:{SID}:seq:{i}", f"value-{SID}-{i}")

end_time = time.time()
time_sequential = end_time - start_time
print(f"方案甲耗时: {time_sequential:.4f} 秒\n")

# ==========================================
# 方案乙：普通 Pipeline 分批写入
# ==========================================
print("正在执行方案乙：Pipeline 分批写入...")
start_time = time.time()

for i in range(1, N + 1, Q):
    # 使用 transaction=False，表示普通管道，不使用事务包装
    pipe = r.pipeline(transaction=False)
    # 处理最后不足 Q 条的情况
    batch_end = min(i + Q, N + 1)
    for j in range(i, batch_end):
        pipe.set(f"exam:{SID}:pipe:{j}", f"value-{SID}-{j}")
    # 一批执行并取得全部结果
    pipe.execute()

end_time = time.time()
time_pipeline = end_time - start_time
print(f"方案乙耗时: {time_pipeline:.4f} 秒\n")

# ==========================================
# 结果输出与说明
# ==========================================
print("==== 计时与结果输出 ====")
print(f"命令总数: {N}")
print(f"逐条写入耗时 (方案甲): {time_sequential:.4f} 秒")
print(f"Pipeline耗时 (方案乙): {time_pipeline:.4f} 秒")
print(f"加速比: {time_sequential / time_pipeline:.2f} 倍\n")

# 验证数据完整性（尾批处理）
count_seq = 0
count_pipe = 0
for i in range(1, N + 1):
    if r.exists(f"exam:{SID}:seq:{i}"):
        count_seq += 1
    if r.exists(f"exam:{SID}:pipe:{i}"):
        count_pipe += 1

print(f"数据完整性验证：方案甲成功写入 {count_seq} 条，方案乙成功写入 {count_pipe} 条。")
if count_seq == N and count_pipe == N:
    print("验证通过：尾批处理正确，数据完整！")
else:
    print("验证失败：数据缺失！")