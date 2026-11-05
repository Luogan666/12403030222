from redis.cluster import RedisCluster, ClusterNode
import time

print("正在连接 Redis 集群...")
startup_nodes = [
    ClusterNode(host="127.0.0.1", port=30222),
    ClusterNode(host="127.0.0.1", port=30223),
    ClusterNode(host="127.0.0.1", port=30224)
]

r = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
SID = "12403030222"
print("集群连接成功！\n")

# ====== 1. 学生信息维护 (Hash) ======
print("==== 1. 学生信息维护 (Hash) ====")
hash_key = f"exam:{SID}:student"

# 逐个字段插入，避免集群模式下的 mapping 参数兼容性问题
r.hset(hash_key, "studentId", SID)
r.hset(hash_key, "name", "张三")
r.hset(hash_key, "className", "计算机科学与技术班")
r.hset(hash_key, "courseId", f"COURSE-{SID}-01")
r.hset(hash_key, "status", "learning")

# 将 status 修改为 completed
r.hset(hash_key, "status", "completed")

# 单独读取
print("单独读取 name:", r.hget(hash_key, "name"))
print("单独读取 status:", r.hget(hash_key, "status"))

# 输出完整 Hash
print("完整 Hash 数据:", r.hgetall(hash_key))
print()
# ====== 2. 已完成章节记录 (Set) ======
print("==== 2. 已完成章节记录 (Set) ====")
set_key = f"exam:{SID}:chapters"
chapters = ["CH01", "CH02", "CH02", "CH03"]
for ch in chapters:
    r.sadd(set_key, ch)
    print(f"提交 {ch} 后，已完成章节数量: {r.scard(set_key)}")
print("最终全部章节:", r.smembers(set_key))
print("判断 CH02 是否已完成:", r.sismember(set_key, "CH02"))
print("判断 CH04 是否已完成:", r.sismember(set_key, "CH04"))
print()

# ====== 3. 成绩排行榜 (Sorted Set) ======
print("==== 3. 成绩排行榜 (Sorted Set) ====")
zset_key = f"exam:{SID}:rank"
r.zadd(zset_key, {
    f"Student:{SID}": 72,
    "demo:01": 85,
    "demo:02": 90,
    "demo:03": 60,
    "demo:04": 80
})
print("初始前3名:", r.zrevrange(zset_key, 0, 2, withscores=True))
r.zincrby(zset_key, 20, f"Student:{SID}")
print("加分后前3名:", r.zrevrange(zset_key, 0, 2, withscores=True))
score = r.zscore(zset_key, f"Student:{SID}")
rank_index = r.zrevrank(zset_key, f"Student:{SID}")
print(f"本人更新后分数: {score}，名次: 第 {rank_index + 1} 名")
print()

# ====== 4. 会话生命周期 (String) ======
print("==== 4. 会话生命周期 (String) ====")
session_key = f"exam:{SID}:session"
r.set(session_key, "session_token_abc", ex=5)
print("创建后立即读取值:", r.get(session_key))
print("创建后立即读取 TTL(秒):", r.ttl(session_key))

print("等待 6 秒...")
time.sleep(6)

print("等待 6 秒后，键是否存在 (1存在/0不存在):", r.exists(session_key))
print("等待 6 秒后，TTL:", r.ttl(session_key))
print("(TTL 为 -2 表示键已过期不存在，过期验证通过)")