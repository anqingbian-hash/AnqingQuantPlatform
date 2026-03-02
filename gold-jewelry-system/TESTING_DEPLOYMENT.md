# 测试部署说明

## 一、环境准备

### 1.1 数据库准备

**检查 MySQL 是否已安装：**
```bash
mysql --version
```

**创建测试数据库：**
```sql
CREATE DATABASE gold_jewelry_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**导入测试数据：**
```bash
mysql -u root -p gold_jewelry_test < /root/.openclaw/workspace/gold-jewelry-system/backend/src/main/resources/sql/init-test.sql
```

### 1.2 后端启动

**使用测试配置启动：**
```bash
cd /root/.openclaw/workspace/gold-jewelry-system/backend
mvn spring-boot:run --spring.profiles.active=application-test
```

**访问测试环境：**
- 前端：http://localhost:8080/api
- API 地址：http://localhost:8080/api/v1/...
- 数据库：gold_jewelry_test:3306

### 1.3 前端启动

**安装依赖：**
```bash
cd /root/.openclaw/workspace/gold-jewelry-system/frontend
npm install
```

**启动开发服务器：**
```bash
npm run dev
```

**访问测试环境：**
- 前端：http://localhost:3000/
- API 地址：http://localhost:8080/api/v1/...

## 二、功能测试清单

### 2.1 后端 API 测试

**认证模块（2 个接口）**
- [ ] POST /api/v1/auth/login - 用户登录
- [ ] POST /api/v1/auth/logout - 用户登出

**商品管理（7 个接口）**
- [ ] GET /api/v1/products - 分页查询商品
- [ ] POST /api/v1/products - 添加商品
- [ ] PUT /api/v1/products/{id} - 更新商品
- [ ] DELETE /api/v1/products/{id} - 删除商品
- [ ] GET /api/v1/products/code/{code} - 根据编号查询
- [ ] GET /api/v1/products/all - 查询所有商品

**库存管理（6 个接口）**
- [ ] GET /api/v1/inventory - 查询库存
- [ ] POST /api/v1/inventory/stock-in - 入库
- [ ] POST /api/v1/inventory/stock-out - 出库
- [ ] GET /api/v1/inventory/store/{storeId} - 店铺库存列表
- [ ] GET /api/v1/inventory/low-stock - 低库存商品
- [ ] GET /api/v1/inventory/store/{storeId}/total - 库铺库存总数

**价格管理（2 个接口）**
- [ ] GET /api/v1/prices/gold-price - 获取实时金价
- [ ] POST /api/v1/prices/calculate - 计算商品售价

**销售管理（5 个接口）**
- [ ] POST /api/v1/sales - 创建销售订单
- [ ] POST /api/v1/sales/{id}/cancel - 取消订单
- [ ] GET /api/v1/sales/order-no/{orderNo} - 根据订单编号查询
- [ ] GET /api/v1/sales/store/{storeId} - 根据店铺 ID 查询订单列表
- [ ] GET /api/v1/sales - 分页查询订单

**店铺管理（6 个接口）**
- [ ] GET /api/v1/stores - 查询所有店铺
- [ ] POST /api/v1/stores - 添加店铺
- [ ] PUT /api/v1/stores/{id} - 更新店铺
- [ ] DELETE /api/v1/stores/{id} - 删除店铺
- [ ] GET /api/v1/stores/{id} - 根据 ID 查询店铺
- [ ] GET /api/v1/stores/status/{status} - 根据状态查询店铺

**调拨管理（3 个接口）**
- [ ] POST /api/v1/transfers - 创建调拨单
- [ ] POST /api/v1/transfers/{transferNo}/confirm - 确认调拨
- [ ] POST /api/v1/transfers/{transferNo}/receive - 接收调拨

**盘点管理（7 个接口）**
- [ ] POST /api/v1/stocktakes - 创建盘点单
- [ ] POST /api/v1/stocktakes/items - 添加盘点明细
- [ ] POST /api/v1/stocktakes/{id}/complete - 完成盘点
- [ ] POST /api/v1/stocktakes/{id}/review - 审核盘点
- [ ] GET /api/v1/stocktakes/store/{storeId} - 店铺盘点列表
- [ ] GET /api/v1/stocktakes/{id}/items - 盘点明细列表

### 2.2 前端页面测试

**登录页面（1 个）**
- [ ] 用户名/密码登录
- [ ] 表单验证
- [ ] 登录状态保持
- [ ] 路由守卫

**首页（1 个）**
- [ ] 统计卡片展示
- [ ] 实时金价展示
- [ ] 低库存预警
- [ ] 列表展示

**商品管理（3 个）**
- [ ] 商品列表展示
- [ ] 商品搜索（按名称/编号）
- [ ] 添加商品表单验证
- [ ] 编辑商品表单验证
- [ ] 删除商品确认
- [ ] 分页功能
- [ ] 图片上传

**库存管理（2 个）**
- [ ] 库存列表展示
- [ ] 库存搜索（按商品编号/店铺）
- [ ] 入库功能表单验证
- [ ] 出库功能表单验证
- [ ] 库存汇总
- [ ] 低库存标识

**销售管理（1 个）**
- [ ] 销售记录列表
- [ ] 搜索功能（订单编号/客户姓名/日期范围）
- [ ] 销售开单功能
- [ ] 订单取消功能

**店铺管理（1 个）**
- [ ] 店铺列表展示
- [ ] 店铺搜索
- [ ] 添加/编辑店铺
- [ ] 启用/禁用操作

**库存盘点（1 个）**
- [ ] 盘点列表
- [ ] 新建盘点单
- [ ] 盘点明细
- [ ] 完成/审核/取消

### 2.3 集成测试

**流程测试：**
1. 用户登录 → 进入系统 → 查看数据
2. 添加商品 → 扫码入库 → 查看库存
3. 销售开单 → 扣码出库 → 更新库存
4. 多店调拨 → 创建调拨单 → 确认调拨 → 接收调拨
5. 库存盘点 → 新建盘点单 → 添加明细 → 完成盘点 → 审核通过

**数据一致性测试：**
- 前后端库存数据同步
- 价格联动准确性
- 库存流水完整性
- 订单状态流转

---

## 三、上线准备

### 3.1 生产环境配置

**服务器配置（参考）：**
- CPU：4 核 8G × 2 台
- 内存：16G × 2 台
- �盘：100GB SSD
- 带宽：100Mbps 专线

**Nginx 配置（反向代理）：**
```nginx
server {
    listen 80;
    server_name localhost;

    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_connect_timeout 300s;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "";
    }
}
```

### 3.2 SSL 证书配置

**域名：** gold-jewelry.com 或 IP 地址
**证书类型：** Let's Encrypt SSL 证书

### 3.3 数据库配置

**主从配置：**
- 主库：读写
- 从库：只读复制
- 复制方式：binlog 增量备份

### 3.4 防火墙配置

**开放端口：**
- 22 端口（HTTP）
- 3306 端口（MySQL）
- 6379 端口（Redis）
- 8080 端口（应用）

**安全规则：**
- 只开放必要的端口
- 启用防火墙
- 配置安全组规则

---

## 四、上线清单

### 4.1 部署前检查

**服务器检查：**
- [ ] 硬盘空间充足
- [ ] 内存充足
- [ ] 防火墙规则配置
- [ ] SSL 证书安装
- [ ] Nginx 反向代理配置

**数据库检查：**
- [ ] 主从复制配置
- [ ] binlog 开启
- [ ] 定时备份脚本

**应用检查：**
- [ ] 配置文件检查
- [ ] 数据库连接检查
- [ ] Redis 连接检查
- [ ] 日志输出检查

### 4.2 部署步骤

**1. 上传代码到服务器**
```bash
scp -r /root/.openclaw/workspace/gold-jewelry-system/* root@your-server:/root/gold-jewelry-system/
```

**2. 创建数据库**
```bash
mysql -u root -p < /root/.openclaw/workspace/gold-jewelry-system/backend/src/main/resources/sql/init.sql
mysql -u root -p gold_jewelry < /root/.openclaw/workspace/gold-jewelry-system/backend/src/main/resources/sql/init.sql
```

**3. 修改配置文件**
```bash
# 修改 application.yml 中的数据库连接信息
# 修改 application-test.yml 中的数据库连接信息
```

**4. 编译打包**
```bash
cd /root/.openclaw/workspace/gold-jewelry-system/backend
mvn clean package install
mvn package install -Dmaven.test.skip=true
```

**5. 启动后端**
```bash
cd /root/.openclaw/workspace/gold-jewelry-system/backend
mvn spring-boot:run --spring.profiles.active=application-test
```

**6. 启动 Nginx**
```bash
# 启动 Nginx
nginx -c /etc/nginx/nginx.conf
```

**7. 启动前端**
```bash
cd /root/.openclaw/workspace/gold-jewelry-system/frontend
npm install
npm run dev
```

**8. 访问测试：**
- 前端：http://your-server:3000/
- 后端：http://your-server:8080/api
- 默认账号：admin / admin123
- 默认店铺：测试店铺

---

## 五、测试用例

### 5.1 功能测试

**用户登录：**
1. 打开前端 http://your-server:3000/
2. 输入账号密码：admin / admin123
3. 点击登录
4. 检查是否成功登录，跳转到首页

**商品管理：**
1. 进入商品管理页面
2. 点击「添加商品」
3. 填写表单并提交
4. 检查商品列表是否显示
5. 编辑、删除商品

**库存管理：**
1. 进入库存管理页面
2. 点击「入库」按钮
3. 输入数量，点击「确认入库」
4. 检查库存是否正确更新
5. 点击「出库」按钮
6. 输入数量，点击「确认出库」
7. 检查库存是否正确更新

**销售管理：**
1. 进入销售管理页面
2. 点击「销售开单」
3. 添加商品，输入数量
4. 选择支付方式
5. 提交订单，检查是否成功
6. 检查销售记录是否显示

### 5.2 接口测试

使用 Postman 或 curl 测试 API：

```bash
# 1. 测试登录接口
curl -X POST http://your-server:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
      "username": "admin",
      "password": "admin123"
    }'

# 2. 测试商品列表
curl -X GET http://your-server:8080/api/v1/products \
  -H "Authorization: Bearer {token}"

# 3. 测试添加商品
curl -X POST http://your-server:8080/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
      "name": "测试商品",
      "category_id": 1,
      "weight": 10.5,
      "purity": "Au99.99",
      "craft_fee": 500
    }'

# 4. 测试入库
curl -X POST http://your-server:8080/api/v1/inventory/stock-in \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
      "product_id": 1,
      "store_id": 1,
      "quantity": 10,
      "operator_id": 1,
      "order_no": "TEST_IN_001"
    }'
```

### 5.3 性能测试

**压测工具：**
- JMeter
- Locust
- Apache Bench

**测试场景：**
- 并发登录
- 批量添加商品
- 批量库存操作
- 大数据查询

---

## 六、上线检查清单

### 6.1 部署后检查

**应用检查：**
- [ ] 应用是否正常启动
- [ ] 端口是否正常监听
- [ ] 日志是否正常输出
- [ ] 数据库连接是否正常

**功能检查：**
- [ ] 登录功能是否正常
- [ ] 商品 CRUD 是否正常
- [ ] 库存管理是否正常
- [ ] 销售管理是否正常
- [ ] 多店管理是否正常
- [ ] 盘点管理是否正常

**数据检查：**
- [ ] 数据库连接池状态
- [ ] Redis 连接状态
- [ ] 消息队列状态

**安全检查：**
- [ ] SQL 注入漏洞
- [ ] XSS 漏洞
- **登录验证**（JWT）
- **权限控制**（RBAC）

---

## 七、监控告警

### 7.1 应用监控

**关键指标：**
- 在线用户数
- QPS（每秒查询数）
- 错误率
- 响应时间（95分位 < 500ms）
- 服务器资源使用率 < 80%

**告警规则：**
- 错误率 > 1%
- 响应时间 > 2 秒
- QPS > 1000
- CPU > 80%

### 7.2 数据库监控

**关键指标：**
- 连接数
- 慢接数
- 慢接数
- 慢接数
- 慢接数

**告警规则：**
- 连接数 > 80%
- 慢接数 > 80%
- 长查询 > 1 秒

### 7.3 系统日志

**日志级别：**
- INFO：正常业务日志
- WARN：警告日志
- ERROR：错误日志

**日志轮转：**
- 每日备份
- 日志清理：保留 30 天

---

## 八、回滚方案

### 8.1 回滚条件

- 严重错误率 >10%
- 数据一致性问题
- 安全漏洞
- 业务逻辑严重问题

### 8.2 回滚步骤

1. 停止新版本发布
2. 切换回上一版本
3. 数据库迁移
4. 功能回退
5. 问题分析

---

## 九、总结

### 9.1 测试重点

**功能测试：**
- 核心业务流程
- API 接口正确性
- 数据一致性

**性能测试：**
- 并发性能
- 数据库性能
- 接口响应时间

**安全测试：**
- SQL 注入
- XSS 攻击
**登录验证**
- **权限控制**

### 9.2 上线标准

**发布标准：**
- 无严重 bug
- 核心功能正常
- 性能满足预期
- 安全无严重漏洞

**监控标准：**
- 应用正常运行
- 日志正常输出
- 告警及时响应
- 错误率 <1%

---

**测试完成即可上线！**
