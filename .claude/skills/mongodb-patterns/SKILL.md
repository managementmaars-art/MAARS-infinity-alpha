---
name: mongodb-patterns
description: MongoDB patterns — aggregation pipeline, indexes, transactions, schema design, Atlas Search, change streams, Mongoose for MAARS database agents
---

# MongoDB Patterns — MAARS Reference

## Schema Design
```javascript
// EMBED when: data is accessed together, 1-to-few, no standalone access
const postSchema = {
  _id: ObjectId,
  title: String,
  content: String,
  comments: [{  // Embedded — always loaded with post
    author: String,
    text: String,
    createdAt: Date
  }],
  tags: [String],
};

// REFERENCE when: data is large, many-to-many, accessed independently
const orderSchema = {
  _id: ObjectId,
  userId: ObjectId,  // Reference to users collection
  productIds: [ObjectId],  // References to products
  total: Number,
};

// Mongoose
import mongoose, { Schema, Document } from "mongoose";

interface IUser extends Document {
  email: string;
  name: string;
  createdAt: Date;
}

const UserSchema = new Schema<IUser>({
  email: { type: String, required: true, unique: true, lowercase: true },
  name: { type: String, required: true, trim: true },
  role: { type: String, enum: ["admin", "user"], default: "user" },
}, { timestamps: true });

UserSchema.index({ email: 1 });
UserSchema.index({ createdAt: -1 });
```

## Aggregation Pipeline
```javascript
// Sales analytics pipeline
db.orders.aggregate([
  // Stage 1: Filter
  { $match: { 
    status: "completed",
    createdAt: { $gte: new Date("2025-01-01") }
  }},
  
  // Stage 2: Unwind arrays
  { $unwind: "$items" },
  
  // Stage 3: Lookup (JOIN)
  { $lookup: {
    from: "products",
    localField: "items.productId",
    foreignField: "_id",
    as: "product",
    pipeline: [{ $project: { name: 1, category: 1 } }]
  }},
  { $unwind: "$product" },
  
  // Stage 4: Group
  { $group: {
    _id: { month: { $month: "$createdAt" }, category: "$product.category" },
    revenue: { $sum: { $multiply: ["$items.price", "$items.quantity"] } },
    orderCount: { $sum: 1 },
    avgOrderValue: { $avg: "$total" },
  }},
  
  // Stage 5: Add fields
  { $addFields: {
    monthName: { $arrayElemAt: [
      ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
      "$_id.month"
    ]}
  }},
  
  // Stage 6: Sort
  { $sort: { "_id.month": 1, "revenue": -1 } },
  
  // Stage 7: Project output
  { $project: {
    _id: 0,
    month: "$monthName",
    category: "$_id.category",
    revenue: { $round: ["$revenue", 2] },
    orderCount: 1,
  }}
]);
```

## Indexes
```javascript
// Single field
db.users.createIndex({ email: 1 }, { unique: true });
db.posts.createIndex({ createdAt: -1 });

// Compound index
db.orders.createIndex({ userId: 1, status: 1, createdAt: -1 });

// Text search
db.articles.createIndex({ title: "text", content: "text" },
                         { weights: { title: 10, content: 1 } });
db.articles.find({ $text: { $search: "machine learning" } },
                  { score: { $meta: "textScore" } })
           .sort({ score: { $meta: "textScore" } });

// TTL index (auto-delete)
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 86400 });

// Partial index
db.orders.createIndex({ userId: 1 }, {
  partialFilterExpression: { status: "pending" }
});

// Explain query
db.orders.find({ userId: ObjectId("...") }).explain("executionStats");
```

## Transactions
```javascript
const session = await mongoose.startSession();
session.startTransaction();
try {
  const fromAccount = await Account.findByIdAndUpdate(
    fromId, { $inc: { balance: -amount } }, { new: true, session }
  );
  if (fromAccount.balance < 0) throw new Error("Insufficient funds");
  
  await Account.findByIdAndUpdate(
    toId, { $inc: { balance: amount } }, { session }
  );
  
  await Transaction.create([{
    from: fromId, to: toId, amount, type: "transfer"
  }], { session });
  
  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

## Change Streams
```javascript
// Watch for changes in real-time
const changeStream = db.collection("orders").watch([
  { $match: { "operationType": { $in: ["insert", "update"] } } }
], { fullDocument: "updateLookup" });

changeStream.on("change", (change) => {
  if (change.operationType === "insert") {
    notifyNewOrder(change.fullDocument);
  }
  if (change.operationType === "update") {
    syncOrderToElastic(change.fullDocument);
  }
});
```

## Atlas Search
```javascript
// Full-text search with Atlas Search
db.products.aggregate([{
  $search: {
    index: "default",
    compound: {
      must: [{ text: { query: "wireless headphones", path: ["name", "description"],
                        fuzzy: { maxEdits: 1 } } }],
      filter: [{ range: { path: "price", gte: 50, lte: 300 } }],
    },
    highlight: { path: ["name", "description"] },
  }
}, {
  $project: {
    name: 1, price: 1,
    score: { $meta: "searchScore" },
    highlights: { $meta: "searchHighlights" },
  }
}]);
```

## Models to Use
- **Aggregation pipelines**: `claude-opus-4-6` (complex multi-stage reasoning)
- **Schema design**: `claude-sonnet-4-6`
- **Index optimization**: `claude-opus-4-6`
- **Atlas Search queries**: `claude-sonnet-4-6`
