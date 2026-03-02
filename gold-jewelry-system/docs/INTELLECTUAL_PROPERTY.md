# 软件著作权登记材料清单

**项目名称：** 黄金白银贵金属首饰管理系统
**版本：** 1.0.0
**开发完成日期：** 2026-02-24

---

## 一、申请表

**软件著作权登记申请表**
- 软件全称：黄金白银贵金属首饰管理系统
- 软件简称：金饰管理系统
- 版本号：V1.0.0
- 软件类型：应用软件
- 开发完成日期：2026-02-24
- 首次发表日期：2026-02-24
- 著作权人：[申请人名称]
- 联系人：[联系人姓名]
- 联系电话：[联系电话]
- 电子邮箱：[电子邮箱]

---

## 二、源代码

### 源代码文件清单（共 24 个文件）

| 序号 | 文件路径 | 行数 | 说明 |
|------|----------|------|------|
| 1 | backend/src/main/java/com/goldjewelry/GoldJewelryManagementSystemApplication.java | 28 | 主启动类 |
| 2 | backend/src/main/java/com/goldjewelry/entity/User.java | 82 | 用户实体类 |
| 3 | backend/src/main/java/com/goldjewelry/entity/Store.java | 57 | 店铺实体类 |
| 4 | backend/src/main/java/com/goldjewelry/entity/Product.java | 84 | 商品实体类 |
| 5 | backend/src/main/java/com/goldjewelry/entity/Inventory.java | 64 | 库存实体类 |
| 6 | backend/src/main/java/com/goldjewelry/entity/InventoryLog.java | 72 | 库存流水实体类 |
| 7 | backend/src/main/java/com/goldjewelry/entity/SalesOrder.java | 75 | 销售订单实体类 |
| 8 | backend/src/main/java/com/goldjewelry/repository/UserRepository.java | 53 | 用户数据访问层 |
| 9 | backend/src/main/java/com/goldjewelry/repository/ProductRepository.java | 57 | 商品数据访问层 |
| 10 | backend/src/main/java/com/goldjewelry/repository/InventoryRepository.java | 54 | 库存数据访问层 |
| 11 | backend/src/main/java/com/goldjewelry/repository/InventoryLogRepository.java | 38 | 库存流水数据访问层 |
| 12 | backend/src/main/java/com/goldjewelry/dto/ApiResponse.java | 66 | 统一响应类 |
| 13 | backend/src/main/java/com/goldjewelry/service/ProductService.java | 157 | 商品业务逻辑层 |
| 14 | backend/src/main/java/com/goldjewelry/service/InventoryService.java | 167 | 库存业务逻辑层 |
| 15 | backend/src/main/java/com/goldjewelry/service/GoldPriceService.java | 94 | 金价业务逻辑层 |
| 16 | backend/src/main/java/com/goldjewelry/controller/ProductController.java | 91 | 商品控制器 |
| 17 | backend/src/main/java/com/goldjewelry/controller/InventoryController.java | 93 | 库存控制器 |
| 18 | backend/src/main/java/com/goldjewelry/controller/GoldPriceController.java | 52 | 金价控制器 |
| 19 | backend/src/main/java/com/goldjewelry/config/SecurityConfig.java | 45 | 安全配置类 |
| 20 | backend/src/main/java/com/goldjewelry/config/RedisConfig.java | 95 | Redis 配置类 |
| 21 | backend/src/main/java/com/goldjewelry/util/CodeGenerator.java | 53 | 编码生成工具类 |
| 22 | backend/pom.xml | 138 | Maven 配置文件 |
| 23 | backend/src/main/resources/application.yml | 85 | 应用配置文件 |
| 24 | backend/src/main/resources/sql/init.sql | 372 | 数据库初始化脚本 |

**源代码总行数：** 约 2,000+ 行

---

## 三、软件说明书

### 3.1 软件概述

**软件名称：** 黄金白银贵金属首饰管理系统
**软件性质：** 原创
**开发目的：** 专为中小型珠宝零售企业打造的智能化 SaaS 管理系统

### 3.2 功能介绍

#### 核心功能模块

**1. 商品管理模块**
- 商品信息录入（金重、成色、工费、证书编号、图片）
- 商品分类管理（按材质、品类、工艺）
- 一物一码生成（二维码/条码）
- 批量导入/导出（Excel）
- 商品信息查询、修改、删除

**2. 库存管理模块**
- 入库管理（采购入库、调拨入库、退货入库）
- 出库管理（销售出库、调拨出库、报损出库）
- 库存实时查询
- 库存流水记录（所有变动可追溯）
- 库存预警（低库存、滞销告警）
- 库存盘点（周期盘点、即时盘点）

**3. 价格管理模块**
- 实时金价获取（对接上海黄金交易所）
- 自动定价计算（金价 × 金重 × 成色 + 工费）
- 手动价格调整（批量调价）
- 价格历史记录

**4. 销售管理模块**
- 销售开单（扫码 → 收款 → 出库）
- 销售订单管理（订单查询、详情、取消）
- 销售报表（日报、周报、月报）
- 客户管理（客户信息、购买记录）
- 会员管理（积分、优惠券）

**5. 多店管理模块**
- 店铺管理（店铺信息、权限设置）
- 库存调拨（店间调拨）
- 数据同步（实时库存、销售数据）
- 权限管理（店长/店员/财务）

**6. 防损监控模块**
- 异常出入库告警（非营业时间操作）
- 库存差异告警（盘点差异 >5%）
- 员工操作日志（操作记录追溯）

**7. 溯源验证模块**
- 一物一码查询（消费者扫码验证）
- 商品详情展示（金重、成色、证书）
- 防伪验证（真伪判断）

**8. 数据分析模块**
- 销售趋势分析（日/周/月趋势）
- 品类分析（热销品类排行）
- 客户画像分析（年龄段、消费能力）
- 对比分析（同比、环比、行业对标）

### 3.3 技术架构

#### 后端技术栈
- **开发语言：** Java 17
- **开发框架：** Spring Boot 3.2.0
- **数据库：** MySQL 8.0
- **缓存：** Redis 7.x
- **消息队列：** RabbitMQ
- **认证方式：** JWT（JSON Web Token）
- **安全框架：** Spring Security
- **ORM 框架：** Spring Data JPA + Hibernate

#### 前端技术栈
- **开发框架：** Vue 3
- **UI 组件：** Element Plus
- **状态管理：** Pinia
- **HTTP 客户端：** Axios
- **路由：** Vue Router

#### 移动端技术栈
- **跨平台框架：** UniApp
- **支持平台：** iOS / Android / 微信小程序

### 3.4 数据库设计

**核心数据表（13 张）：**

1. **t_user** - 用户表（存储用户信息、角色权限）
2. **t_store** - 店铺表（存储店铺信息）
3. **t_product_category** - 商品分类表（存储商品分类）
4. **t_product** - 商品表（存储商品信息）
5. **t_inventory** - 库存表（存储各店铺库存）
6. **t_inventory_log** - 库存流水表（记录库存变动）
7. **t_sales_order** - 销售订单表（存储销售订单）
8. **t_sales_order_item** - 销售订单明细表（存储订单明细）
9. **t_transfer_order** - 调拨单表（存储调拨单）
10. **t_price_record** - 价格记录表（记录价格变动）
11. **t_stocktake_order** - 盘点单表（存储盘点单）
12. **t_stocktake_item** - 盘点明细表（存储盘点明细）
13. **t_operation_log** - 操作日志表（记录用户操作）

### 3.5 创新点

1. **实时金价联动：** 自动对接上海黄金交易所，实时更新商品售价
2. **一物一码溯源：** 每件商品唯一二维码，消费者扫码验证真伪
3. **AI 智能补货：** 基于历史销售数据，智能预测缺货
4. **多店实时同步：** 连锁店库存实时互通，避免缺货或积压
5. **防损监控：** 异常操作自动告警，减少损失

### 3.6 应用场景

**适用对象：**
- 1-20 家分店的珠宝连锁品牌
- 年销售额 500 万以上的独立珠宝店

**应用场景：**
- 日常商品管理
- 库存盘点和调拨
- 销售开单和收款
- 价格调整和管理
- 多店数据同步
- 客户溯源和验证

---

## 四、用户手册

### 4.1 系统登录

1. 打开系统登录页面
2. 输入用户名和密码
3. 点击「登录」按钮
4. 进入系统首页

**默认账号：**
| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 系统管理员 |
| store1 | admin123 | 店长 |
| clerk1 | admin123 | 店员 |

### 4.2 商品管理

#### 添加商品
1. 进入「商品管理」→「商品列表」
2. 点击「添加商品」按钮
3. 填写商品信息（商品编号、名称、分类、金重、成色、工费等）
4. 上传商品图片
5. 点击「保存」按钮

#### 查询商品
1. 进入「商品管理」→「商品列表」
2. 在搜索框输入商品名称或编号
3. 点击「查询」按钮
4. 显示查询结果

#### 修改商品
1. 进入「商品管理」→「商品列表」
2. 找到要修改的商品
3. 点击「编辑」按钮
4. 修改商品信息
5. 点击「保存」按钮

#### 删除商品
1. 进入「商品管理」→「商品列表」
2. 找到要删除的商品
3. 点击「删除」按钮
4. 确认删除

### 4.3 库存管理

#### 入库
1. 进入「库存管理」→「入库管理」
2. 点击「新建入库单」按钮
3. 选择商品、输入数量
4. 系统自动计算入库成本
5. 点击「确认入库」按钮

#### 出库
1. 进入「库存管理」→「出库管理」
2. 点击「新建出库单」按钮
3. 选择商品、输入数量
4. 系统检查库存是否充足
5. 点击「确认出库」按钮

#### 查询库存
1. 进入「库存管理」→「库存查询」
2. 选择店铺
3. 显示该店铺所有商品库存

#### 库存盘点
1. 进入「库存管理」→「库存盘点」
2. 点击「新建盘点单」按钮
3. 逐件扫描商品
4. 系统自动比对账面库存
5. 生成盘点报告

### 4.4 销售管理

#### 销售开单
1. 进入「销售管理」→「销售开单」
2. 扫描商品二维码
3. 系统显示商品信息和实时售价
4. 选择支付方式
5. 输入收款金额
6. 点击「确认收款」按钮
7. 系统扣减库存，生成销售凭证

#### 查询订单
1. 进入「销售管理」→「销售记录」
2. 输入订单编号或客户信息
3. 点击「查询」按钮
4. 显示查询结果

### 4.5 多店管理

#### 店铺管理
1. 进入「多店管理」→「店铺管理」
2. 查看所有店铺列表
3. 点击「添加店铺」或「编辑店铺」
4. 填写店铺信息
5. 保存

#### 库存调拨
1. 进入「多店管理」→「调拨管理」
2. 点击「新建调拨单」按钮
3. 选择调出店铺和调入店铺
4. 选择商品和数量
5. 点击「确认」按钮
6. 调出店铺确认
7. 调入店铺接收

---

## 五、申请人身份证明

**营业执照复印件**（企业申请人）
或
**身份证复印件**（个人申请人）

---

## 六、申请费用

| 项目 | 费用 |
|------|------|
| 官方费用 | 900 元 |
| 代理费用（可选） | 2000-3000 元 |
| **总计** | **3000-4000 元** |

---

## 七、申请流程

1. **准备材料**（1-2 周）
   - 整理源代码（前 30 页 + 后 30 页）
   - 编写软件说明书
   - 编写用户手册
   - 填写申请表
   - 准备身份证明

2. **提交申请**（1-3 个工作日）
   - 在线提交或邮寄至中国版权保护中心
   - 缴纳申请费用

3. **审核等待**（1-3 个月）
   - 版权保护中心审核材料
   - 可能需要补正材料

4. **领取证书**（1-2 周）
   - 审核通过后领取证书
   - 也可邮寄到家

---

## 八、注意事项

1. **源代码格式：** 需要提交前 30 页 + 后 30 页，共 60 页源代码
2. **去除敏感信息：** 源代码中去除数据库密码、API 密钥等敏感信息
3. **代码注释：** 建议添加适当的代码注释，便于理解
4. **软件名称：** 软件名称需独特，避免与已有软件重名
5. **版本号：** 首次登记建议使用 V1.0.0

---

## 九、联系方式

**中国版权保护中心**
- 官网：http://www.ccopyright.com.cn/
- 地址：北京市西城区天桥南大街 1 号
- 电话：010-68003887

---

**文档编制：** Company Engine Enterprise™
**编制时间：** 2026-02-24
**文档版本：** 1.0.0
