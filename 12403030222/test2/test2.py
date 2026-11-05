from pymongo import MongoClient
import pymongo

# 注意：因为你的环境改成了副本集，连接字符串必须加上 ?replicaSet=rs0
SID = "12403030222"
BUY = 2  # 1 + A = 2
STOCK = 7  # 5 + C = 7

# 连接数据库
client = MongoClient("mongodb://127.0.0.1:27017/?replicaSet=rs0")
db = client[f"exam_{SID}"]
inventory = db["inventory"]
orders = db["orders"]


def reset_data(initial_stock):
    """重置库存和订单集合"""
    inventory.delete_many({})
    orders.delete_many({})
    inventory.insert_one({
        "_id": f"BOOK-{SID}",
        "title": "NoSQL数据库教材",
        "stock": initial_stock
    })


def place_order(requestId, forceError=False):
    """执行事务进行扣减和插入"""
    with client.start_session() as session:
        session.start_transaction()
        try:
            # 1. 原子扣减：筛选库存 >= BUY
            result = inventory.update_one(
                {"_id": f"BOOK-{SID}", "stock": {"$gte": BUY}},
                {"$inc": {"stock": -BUY}},
                session=session
            )

            # 如果没匹配到文档，说明库存不足
            if result.matched_count == 0:
                session.abort_transaction()
                return False, "库存不足或不存在"

            # 2. 模拟异常（forceError）
            if forceError:
                raise Exception("主动抛出异常，验证回滚")

            # 3. 插入订单
            orders.insert_one({
                "_id": requestId,
                "bookId": f"BOOK-{SID}",
                "studentId": SID,
                "quantity": BUY
            }, session=session)

            # 4. 提交事务
            session.commit_transaction()
            return True, "成功"
        except Exception as e:
            session.abort_transaction()
            return False, str(e)


def run_scenario(scene_name, initial_stock, orders_to_make, force_error=False):
    """运行并打印单个场景的结果"""
    reset_data(initial_stock)

    success_count = 0
    fail_count = 0

    for i in range(orders_to_make):
        req_id = f"REQ-{scene_name}-{i}"
        success, msg = place_order(req_id, forceError=force_error)
        if success:
            success_count += 1
        else:
            fail_count += 1

    final_stock = inventory.find_one({"_id": f"BOOK-{SID}"})["stock"]
    final_orders = orders.count_documents({})

    # 计算预期值，用于核验
    expected_success = orders_to_make
    expected_fail = 0

    if scene_name == "T2":
        expected_success = 0
        expected_fail = 1
    elif scene_name == "T3":
        expected_success = 0
        expected_fail = 1
    elif scene_name == "T4":
        expected_success = initial_stock // BUY
        expected_fail = 1

    # 判断是否通过核验
    is_passed = (success_count == expected_success and fail_count == expected_fail)
    passed_str = "是 (通过)" if is_passed else "否 (不通过)"

    print(f"--- 场景 {scene_name} ---")
    print(f"初始库存: {initial_stock}, 购买数量: {BUY}")
    print(f"成功次数: {success_count}, 失败次数: {fail_count}")
    print(f"最终库存: {final_stock}, 最终订单数: {final_orders}")
    print(f"是否通过本人编写的核验: {passed_str}\n")


# ====== 运行四个场景 ======
if __name__ == "__main__":
    # T1 正常订购（初始 7，买 2 次即可，或者买 1 次看结果。按题意执行一次正常订购）
    run_scenario("T1", initial_stock=7, orders_to_make=1)

    # T2 库存不足（初始 1，买 2）
    run_scenario("T2", initial_stock=1, orders_to_make=1)

    # T3 中途异常（初始 7，forceError=True）
    run_scenario("T3", initial_stock=7, orders_to_make=1, force_error=True)

    # T4 连续购买（初始 7，买 7//2 + 1 = 4 次）
    run_scenario("T4", initial_stock=7, orders_to_make=4)