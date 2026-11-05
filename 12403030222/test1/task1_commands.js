// 1. 查询课程
examDB.courses.aggregate([
  { $match: { teacher: "张老师", status: "OPEN" } },
  { $project: {
      _id: 0,
      courseId: "$_id",
      title: 1,
      chapterCount: { $size: "$chapters" }
  }}
]);

// 2. 修改章节标题
examDB.courses.updateOne(
  { _id: "COURSE-12403030222-01", "chapters.chapterId": "CH02" },
  { $set: { "chapters.$.title": "Redis基础与应用-22" } }
);
examDB.courses.findOne({ _id: "COURSE-12403030222-01" });

// 3. 增加章节并防止重复
const A = 1; 
const newChapter = { chapterId: "CH03", title: "Redis高级操作", hours: 2 + A };
examDB.courses.updateOne(
  { _id: "COURSE-12403030222-01" },
  { $addToSet: { chapters: newChapter } }
);
// 第二次
examDB.courses.updateOne(
  { _id: "COURSE-12403030222-01" },
  { $addToSet: { chapters: newChapter } }
);

// 4. 验证结果
examDB.courses.aggregate([
  { $match: { _id: "COURSE-12403030222-01" } },
  { $unwind: "$chapters" },
  { $match: { "chapters.chapterId": "CH02" } },
  { $project: { _id: 0, title: "$chapters.title" } }
]);

examDB.courses.aggregate([
  { $match: { _id: "COURSE-12403030222-01" } },
  { $unwind: "$chapters" },
  { $match: { "chapters.chapterId": "CH03" } },
  { $count: "ch03Count" }
]);

examDB.courses.aggregate([
  { $match: { _id: "COURSE-12403030222-01" } },
  { $project: { chapterCount: { $size: "$chapters" } } }
]);

examDB.courses.findOne(
  { _id: "COURSE-12403030222-01" },
  { teacher: 1, status: 1 }
);