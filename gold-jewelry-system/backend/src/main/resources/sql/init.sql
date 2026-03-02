-- =========================================
-- 黄金白银贵金属首饰管理系统
-- 数据库初始化脚本
-- =========================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS gold_jewelry
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE gold_jewelry;

-- =========================================
-- 1. 用户表
-- =========================================
CREATE TABLE IF NOT EXISTS t_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户 ID',
  username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
  password VARCHAR(100) NOT NULL COMMENT '密码（加密）',
  real_name VARCHAR(50) COMMENT '真实姓名',
  phone VARCHAR(20) COMMENT '手机号',
  email VARCHAR(100) COMMENT '邮箱',
  store_id BIGINT COMMENT '所属店铺 ID',
  role_id INT NOT NULL COMMENT '角色 ID：1-超级管理员 2-店长 3-店员 4-财务',
  status TINYINT DEFAULT 1 COMMENT '状态：0-禁用 1-启用',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_store_id (store_id),
  INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- =========================================
-- 2. 店铺表
-- =========================================
CREATE TABLE IF NOT EXISTS t_store (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '店铺 ID',
  name VARCHAR(100) NOT NULL COMMENT '店铺名称',
  address VARCHAR(200) COMMENT '店铺地址',
  phone VARCHAR(20) COMMENT '联系电话',
  status TINYINT DEFAULT 1 COMMENT '状态：0-禁用 1-启用',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='店铺表';

-- =========================================
-- 3. 商品分类表
-- =========================================
CREATE TABLE IF NOT EXISTS t_product_category (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类 ID',
  name VARCHAR(50) NOT NULL COMMENT '分类名称',
  parent_id INT DEFAULT 0 COMMENT '父分类 ID',
  level INT DEFAULT 1 COMMENT '分类层级',
  sort_order INT DEFAULT 0 COMMENT '排序',
  status TINYINT DEFAULT 1 COMMENT '状态：0-禁用 1-启用',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- =========================================
-- 4. 商品表
-- =========================================
CREATE TABLE IF NOT EXISTS t_product (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '商品 ID',
  product_code VARCHAR(50) UNIQUE NOT NULL COMMENT '商品编号',
  name VARCHAR(100) NOT NULL COMMENT '商品名称',
  category_id INT NOT NULL COMMENT '商品分类 ID',
  weight DECIMAL(10,2) NOT NULL COMMENT '金重（克）',
  purity VARCHAR(20) NOT NULL COMMENT '成色：Au99.99/Au99.95/Au99.5/Au99/Au91.6/Au75',
  craft_fee DECIMAL(10,2) NOT NULL COMMENT '工费（元）',
  supplier_id BIGINT COMMENT '供应商 ID',
  certificate_no VARCHAR(100) COMMENT '证书编号',
  image_url VARCHAR(500) COMMENT '图片 URL',
  remark TEXT COMMENT '备注',
  status TINYINT DEFAULT 1 COMMENT '状态：0-禁用 1-启用',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_product_code (product_code),
  INDEX idx_category_id (category_id),
  INDEX idx_supplier_id (supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- =========================================
-- 5. 库存表
-- =========================================
CREATE TABLE IF NOT EXISTS t_inventory (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '库存 ID',
  product_id BIGINT NOT NULL COMMENT '商品 ID',
  store_id BIGINT NOT NULL COMMENT '店铺 ID',
  quantity INT NOT NULL DEFAULT 0 COMMENT '库存数量',
  frozen_quantity INT NOT NULL DEFAULT 0 COMMENT '冻结数量（调拨中）',
  status TINYINT DEFAULT 1 COMMENT '状态：0-禁用 1-启用',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY uk_product_store (product_id, store_id),
  INDEX idx_store_id (store_id),
  INDEX idx_quantity (quantity),
  CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES t_product(id),
  CONSTRAINT fk_inventory_store FOREIGN KEY (store_id) REFERENCES t_store(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存表';

-- =========================================
-- 6. 库存流水表
-- =========================================
CREATE TABLE IF NOT EXISTS t_inventory_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '流水 ID',
  product_id BIGINT NOT NULL COMMENT '商品 ID',
  store_id BIGINT NOT NULL COMMENT '店铺 ID',
  type TINYINT NOT NULL COMMENT '类型：1-入库 2-出库 3-调拨 4-盘点 5-报损',
  quantity INT NOT NULL COMMENT '变动数量（正数入库，负数出库）',
  before_quantity INT NOT NULL COMMENT '变动前数量',
  after_quantity INT NOT NULL COMMENT '变动后数量',
  order_no VARCHAR(50) COMMENT '关联订单号',
  operator_id BIGINT NOT NULL COMMENT '操作人 ID',
  remark TEXT COMMENT '备注',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_product_id (product_id),
  INDEX idx_store_id (store_id),
  INDEX idx_created_at (created_at),
  INDEX idx_order_no (order_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存流水表';

-- =========================================
-- 7. 销售订单表
-- =========================================
CREATE TABLE IF NOT EXISTS t_sales_order (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '订单 ID',
  order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '订单编号',
  store_id BIGINT NOT NULL COMMENT '店铺 ID',
  customer_name VARCHAR(50) COMMENT '客户姓名',
  customer_phone VARCHAR(20) COMMENT '客户电话',
  total_amount DECIMAL(12,2) NOT NULL COMMENT '订单总额',
  payment_method VARCHAR(20) COMMENT '支付方式：wechat-alipay-cash-card',
  payment_status TINYINT DEFAULT 0 COMMENT '支付状态：0-未支付 1-已支付',
  operator_id BIGINT NOT NULL COMMENT '操作人 ID',
  status TINYINT DEFAULT 0 COMMENT '订单状态：0-待支付 1-已完成 2-已取消',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_order_no (order_no),
  INDEX idx_store_id (store_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售订单表';

-- =========================================
-- 8. 销售订单明细表
-- =========================================
CREATE TABLE IF NOT EXISTS t_sales_order_item (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '明细 ID',
  order_id BIGINT NOT NULL COMMENT '订单 ID',
  product_id BIGINT NOT NULL COMMENT '商品 ID',
  product_code VARCHAR(50) NOT NULL COMMENT '商品编号',
  product_name VARCHAR(100) NOT NULL COMMENT '商品名称',
  weight DECIMAL(10,2) NOT NULL COMMENT '金重',
  purity VARCHAR(20) NOT NULL COMMENT '成色',
  unit_price DECIMAL(12,2) NOT NULL COMMENT '单价',
  total_price DECIMAL(12,2) NOT NULL COMMENT '小计',
  quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_order_id (order_id),
  INDEX idx_product_id (product_id),
  CONSTRAINT fk_order_item_order FOREIGN KEY (order_id) REFERENCES t_sales_order(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售订单明细表';

-- =========================================
-- 9. 调拨单表
-- =========================================
CREATE TABLE IF NOT EXISTS t_transfer_order (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '调拨单 ID',
  transfer_no VARCHAR(50) UNIQUE NOT NULL COMMENT '调拨编号',
  from_store_id BIGINT NOT NULL COMMENT '调出店铺',
  to_store_id BIGINT NOT NULL COMMENT '调入店铺',
  status TINYINT DEFAULT 0 COMMENT '状态：0-待确认 1-已确认 2-运输中 3-已完成 4-已取消',
  operator_id BIGINT NOT NULL COMMENT '创建人',
  confirm_at DATETIME COMMENT '确认时间',
  complete_at DATETIME COMMENT '完成时间',
  remark TEXT COMMENT '备注',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_transfer_no (transfer_no),
  INDEX idx_from_store (from_store_id),
  INDEX idx_to_store (to_store_id),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='调拨单表';

-- =========================================
-- 10. 价格记录表
-- =========================================
CREATE TABLE IF NOT EXISTS t_price_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '价格记录 ID',
  product_id BIGINT NOT NULL COMMENT '商品 ID',
  gold_price DECIMAL(10,2) NOT NULL COMMENT '实时金价（元/克）',
  unit_price DECIMAL(12,2) NOT NULL COMMENT '商品单价',
  change_reason VARCHAR(100) COMMENT '调价原因',
  operator_id BIGINT NOT NULL COMMENT '操作人 ID',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_product_id (product_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='价格记录表';

-- =========================================
-- 11. 盘点单表
-- =========================================
CREATE TABLE IF NOT EXISTS t_stocktake_order (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '盘点单 ID',
  stocktake_no VARCHAR(50) UNIQUE NOT NULL COMMENT '盘点编号',
  store_id BIGINT NOT NULL COMMENT '店铺 ID',
  type TINYINT DEFAULT 1 COMMENT '类型：1-周期盘点 2-即时盘点',
  status TINYINT DEFAULT 0 COMMENT '状态：0-盘点中 1-待审核 2-已完成 3-已取消',
  operator_id BIGINT NOT NULL COMMENT '操作人',
  total_count INT DEFAULT 0 COMMENT '盘点总数',
  diff_count INT DEFAULT 0 COMMENT '差异数',
  review_operator_id BIGINT COMMENT '审核人',
  reviewed_at DATETIME COMMENT '审核时间',
  remark TEXT COMMENT '备注',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_stocktake_no (stocktake_no),
  INDEX idx_store_id (store_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='盘点单表';

-- =========================================
-- 12. 盘点明细表
-- =========================================
CREATE TABLE IF NOT EXISTS t_stocktake_item (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '盘点明细 ID',
  stocktake_id BIGINT NOT NULL COMMENT '盘点单 ID',
  product_id BIGINT NOT NULL COMMENT '商品 ID',
  book_quantity INT NOT NULL COMMENT '账面数量',
  actual_quantity INT NOT NULL COMMENT '实际数量',
  diff_quantity INT NOT NULL COMMENT '差异数量',
  status TINYINT DEFAULT 0 COMMENT '状态：0-正常 1-异常',
  remark TEXT COMMENT '备注',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_stocktake_id (stocktake_id),
  INDEX idx_product_id (product_id),
  CONSTRAINT fk_stocktake_item_stocktake FOREIGN KEY (stocktake_id) REFERENCES t_stocktake_order(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='盘点明细表';

-- =========================================
-- 13. 操作日志表
-- =========================================
CREATE TABLE IF NOT EXISTS t_operation_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志 ID',
  user_id BIGINT NOT NULL COMMENT '用户 ID',
  username VARCHAR(50) NOT NULL COMMENT '用户名',
  store_id BIGINT COMMENT '店铺 ID',
  module VARCHAR(50) NOT NULL COMMENT '模块：商品/库存/销售等',
  action VARCHAR(50) NOT NULL COMMENT '操作：新增/修改/删除等',
  target_id BIGINT COMMENT '目标 ID',
  content TEXT COMMENT '操作内容',
  ip VARCHAR(50) COMMENT 'IP 地址',
  user_agent VARCHAR(500) COMMENT 'User-Agent',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_user_id (user_id),
  INDEX idx_store_id (store_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- =========================================
-- 初始化数据
-- =========================================

-- 插入默认店铺
INSERT INTO t_store (id, name, address, phone) VALUES
(1, '总店', '北京市朝阳区XX路XX号', '010-12345678'),
(2, '分店 A', '上海市浦东新区XX路XX号', '021-87654321');

-- 插入默认用户（密码：admin123）
INSERT INTO t_user (username, password, real_name, phone, email, store_id, role_id, status) VALUES
('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '系统管理员', '13800138000', 'admin@goldjewelry.com', 1, 1, 1),
('store1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '张店长', '13800138001', 'store1@goldjewelry.com', 1, 2, 1),
('clerk1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '李店员', '13800138002', 'clerk1@goldjewelry.com', 1, 3, 1);

-- 插入商品分类
INSERT INTO t_product_category (name, parent_id, level, sort_order) VALUES
('黄金项链', 0, 1, 1),
('黄金戒指', 0, 1, 2),
('黄金手镯', 0, 1, 3),
('白银项链', 0, 1, 4),
('白银戒指', 0, 1, 5),
('白银手镯', 0, 1, 6);

-- =========================================
-- 初始化完成
-- =========================================
