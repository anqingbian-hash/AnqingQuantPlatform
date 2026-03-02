# 黄金白银贵金属首饰管理系统 - API 测试脚本

**项目名称**：黄金白银贵金属首饰管理系统
**版本**：1.0.0
**测试工具**：Postman / curl
**项目路径**：/root/.openclaw/workspace/gold-jewelry-system

---

## 一、测试准备

### 1.1 环境变量

```bash
# API 地址
export API_BASE_URL="http://localhost:8080/api"

# 登录账号
export USERNAME="admin"
export PASSWORD="admin123"
```

### 1.2 获取 Token

```bash
# 登录获取 Token
TOKEN=$(curl -s -X POST $API_BASE_URL/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{
      \"username\": \"$USERNAME\",
      \"password\": \"$PASSWORD\"
    }" | jq -r '.data.token')

echo "Token: $TOKEN"
```

---

## 二、认证模块测试（2 个接口）

### 2.1 用户登录

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
      "username": "admin",
      "password": "admin123"
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "realName": "管理员"
    }
  }
}
```

### 2.2 用户登出

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

---

## 三、商品管理测试（9 个接口）

### 3.1 分页查询商品

**请求**：
```bash
curl -X GET "$API_BASE_URL/v1/products?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "list": [
      {
        "id": 1,
        "productCode": "TEST001",
        "name": "18K 黄金项链",
        "category": {
          "id": 1,
          "name": "黄金项链"
        },
        "weight": 5.68,
        "purity": "Au99.99",
        "craftFee": 1500,
        "status": 1
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

### 3.2 添加商品

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "name": "测试商品",
      "category_id": 1,
      "weight": 10.5,
      "purity": "Au99.99",
      "craft_fee": 500
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 100,
    "productCode": "TEST202602240001",
    "name": "测试商品"
  }
}
```

### 3.3 更新商品

**请求**：
```bash
curl -X PUT $API_BASE_URL/v1/products/100 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "name": "测试商品（已修改）",
      "category_id": 1,
      "weight": 10.5,
      "purity": "Au99.99",
      "craft_fee": 600
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 100,
    "name": "测试商品（已修改）"
  }
}
```

### 3.4 删除商品

**请求**：
```bash
curl -X DELETE $API_BASE_URL/v1/products/100 \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 3.5 根据编号查询商品

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/products/code/TEST001 \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 1,
    "productCode": "TEST001",
    "name": "18K 黄金项链"
  }
}
```

### 3.6 根据分类查询商品

**请求**：
```bash
curl -X GET "$API_BASE_URL/v1/products/category/1?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "list": [...],
    "total": 50
  }
}
```

### 3.7 查询所有商品

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/products/all \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": [...]
}
```

---

## 四、库存管理测试（6 个接口）

### 4.1 查询库存

**请求**：
```bash
curl -X GET "$API_BASE_URL/v1/inventory?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "list": [
      {
        "id": 1,
        "product": {
          "id": 1,
          "productCode": "TEST001",
          "name": "18K 黄金项链"
        },
        "store": {
          "id": 1,
          "name": "测试店铺"
        },
        "quantity": 100,
        "frozenQuantity": 0,
        "status": 1
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

### 4.2 入库

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/inventory/stock-in \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "product_id": 1,
      "store_id": 1,
      "quantity": 10,
      "operator_id": 1,
      "order_no": "TEST_IN_001",
      "remark": "测试入库"
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "入库成功",
  "data": {
    "beforeQuantity": 100,
    "afterQuantity": 110,
    "quantity": 10
  }
}
```

### 4.3 出库

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/inventory/stock-out \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "product_id": 1,
      "store_id": 1,
      "quantity": 5,
      "operator_id": 1,
      "order_no": "TEST_OUT_001",
      "remark": "测试出库"
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "出库成功",
  "data": {
    "beforeQuantity": 110,
    "afterQuantity": 105,
    "quantity": 5
  }
}
```

### 4.4 查询店铺库存

**请求**：
```bash
curl -X GET "$API_BASE_URL/v1/inventory/store/1?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "list": [...],
    "total": 30
  }
}
```

### 4.5 查询低库存商品

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/inventory/low-stock \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": [...]
}
```

### 4.6 查询库存总数

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/inventory/store/1/total \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "totalCount": 1050,
    "totalValue": 5250000.00
  }
}
```

---

## 五、价格管理测试（2 个接口）

### 5.1 获取实时金价

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/prices/gold-price \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "goldPrice": 520.50,
    "silverPrice": 6.20,
    "updateTime": "2026-02-24 20:00:00"
  }
}
```

### 5.2 计算商品售价

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/prices/calculate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "product_id": 1,
      "quantity": 2
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "计算成功",
  "data": {
    "unitPrice": 3500.00,
    "totalPrice": 7000.00,
    "goldPrice": 520.50,
    "weight": 5.68,
    "craftFee": 1500
  }
}
```

---

## 六、销售管理测试（5 个接口）

### 6.1 创建销售订单

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/sales \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "store_id": 1,
      "customer_name": "张三",
      "customer_phone": "13800138000",
      "payment_method": "wechat",
      "items": [
        {
          "product_id": 1,
          "quantity": 2
        }
      ]
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 100,
    "orderNo": "SO2026022420000001",
    "totalAmount": 7000.00,
    "status": 1
  }
}
```

### 6.2 取消订单

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/sales/100/cancel \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "取消成功",
  "data": null
}
```

### 6.3 根据订单编号查询

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/sales/order-no/SO2026022420000001 \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 100,
    "orderNo": "SO2026022420000001",
    "customerName": "张三",
    "customerPhone": "13800138000",
    "totalAmount": 7000.00,
    "status": 1
  }
}
```

### 6.4 根据店铺查询订单

**请求**：
```bash
curl -X GET "$API_BASE_URL/v1/sales/store/1?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "list": [...],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

### 6.5 分页查询订单

**请求**：
```bash
curl -X GET "$API_BASE_URL/v1/sales?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

---

## 七、店铺管理测试（6 个接口）

### 7.1 查询所有店铺

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/stores \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "id": 1,
      "name": "测试店铺",
      "address": "测试地址",
      "phone": "13800138000",
      "status": 1
    }
  ]
}
```

### 7.2 添加店铺

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/stores \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "name": "测试分店",
      "address": "测试分店地址",
      "phone": "13800138001",
      "status": 1
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 100,
    "name": "测试分店"
  }
}
```

### 7.3 更新店铺

**请求**：
```bash
curl -X PUT $API_BASE_URL/v1/stores/100 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "name": "测试分店（已修改）",
      "address": "测试分店地址",
      "phone": "13800138001",
      "status": 1
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 100,
    "name": "测试分店（已修改）"
  }
}
```

### 7.4 删除店铺

**请求**：
```bash
curl -X DELETE $API_BASE_URL/v1/stores/100 \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 7.5 根据 ID 查询店铺

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/stores/1 \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 1,
    "name": "测试店铺",
    "address": "测试地址",
    "phone": "13800138000",
    "status": 1
  }
}
```

### 7.6 根据状态查询店铺

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/stores/status/1 \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": [...]
}
```

---

## 八、调拨管理测试（3 个接口）

### 8.1 创建调拨单

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/transfers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "from_store_id": 1,
      "to_store_id": 2,
      "items": [
        {
          "product_id": 1,
          "quantity": 10
        }
      ],
      "operator_id": 1,
      "remark": "测试调拨"
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 100,
    "transferNo": "TF2026022420000001",
    "status": 0
  }
}
```

### 8.2 确认调拨

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/transfers/TF2026022420000001/confirm \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "确认成功",
  "data": null
}
```

### 8.3 接收调拨

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/transfers/TF2026022420000001/receive \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "接收成功",
  "data": null
}
```

---

## 九、盘点管理测试（7 个接口）

### 9.1 创建盘点单

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/stocktakes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "store_id": 1,
      "type": 1,
      "operator_id": 1,
      "remark": "测试盘点"
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 100,
    "stocktakeNo": "ST2026022420000001",
    "status": 0
  }
}
```

### 9.2 添加盘点明细

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/stocktakes/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "stocktake_id": 100,
      "product_id": 1,
      "book_quantity": 100,
      "actual_quantity": 105
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 100,
    "productId": 1,
    "bookQuantity": 100,
    "actualQuantity": 105,
    "diffQuantity": 5
  }
}
```

### 9.3 完成盘点

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/stocktakes/100/complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "operator_id": 1
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "完成成功",
  "data": null
}
```

### 9.4 审核盘点

**请求**：
```bash
curl -X POST $API_BASE_URL/v1/stocktakes/100/review \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
      "passed": true,
      "reviewer_id": 1,
      "remark": "审核通过"
    }'
```

**预期返回**：
```json
{
  "code": 200,
  "message": "审核成功",
  "data": null
}
```

### 9.5 查询店铺盘点列表

**请求**：
```bash
curl -X GET "$API_BASE_URL/v1/stocktakes/store/1?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "list": [...],
    "total": 20,
    "page": 1,
    "size": 10
  }
}
```

### 9.6 查询盘点明细

**请求**：
```bash
curl -X GET $API_BASE_URL/v1/stocktakes/100/items \
  -H "Authorization: Bearer $TOKEN"
```

**预期返回**：
```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "id": 100,
      "productId": 1,
      "bookQuantity": 100,
      "actualQuantity": 105,
      "diffQuantity": 5,
      "status": 1
    }
  ]
}
```

---

## 十、测试总结

### 10.1 测试覆盖

| 模块 | 接口数 | 已测试 | 未测试 |
|------|--------|--------|--------|
| 认证模块 | 2 | 0 | 2 |
| 商品管理 | 7 | 0 | 7 |
| 库存管理 | 6 | 0 | 6 |
| 价格管理 | 2 | 0 | 2 |
| 销售管理 | 5 | 0 | 5 |
| 店铺管理 | 6 | 0 | 6 |
| 调拨管理 | 3 | 0 | 3 |
| 盘点管理 | 6 | 0 | 6 |
| **总计** | **37** | **0** | **37** |

### 10.2 使用方法

**使用 curl 测试**：
```bash
# 1. 设置环境变量
export API_BASE_URL="http://localhost:8080/api"

# 2. 获取 Token
TOKEN=$(curl -s -X POST $API_BASE_URL/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.token')

# 3. 测试接口
curl -X GET "$API_BASE_URL/v1/products?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**使用 Postman 测试**：
1. 导入 Postman Collection
2. 设置环境变量
3. 运行测试

---

**测试脚本编制**：变形金刚（AI 总经理）
**编制日期**：2026-02-24
**脚本版本**：1.0.0
