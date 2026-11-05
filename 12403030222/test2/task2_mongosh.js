const SID = "12403030222";
const examDB = db.getSiblingDB("exam_" + SID);

examDB.inventory.deleteMany({});
examDB.orders.deleteMany({});

examDB.inventory.insertOne({
  _id: "BOOK-" + SID,
  title: "NoSQL数据库教材",
  stock: 7
});

const filter = {
  _id: "BOOK-12403030222",
  stock: { $gte: 2 }
};
const update = {
  $inc: { stock: -2 }
};
const result = examDB.inventory.updateOne(filter, update);

if (result.matchedCount === 0) {
  print("扣减失败：库存不足或教材不存在");
} else if (result.modifiedCount === 1) {
  print("扣减成功");
}