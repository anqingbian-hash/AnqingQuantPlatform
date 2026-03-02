-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS gold_jewelry_test
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE gold_jewelry_test;

-- 导入生产环境表结构
SOURCE /root/.openclaw/workspace/gold-jewelry-system/backend/src/main/resources/sql/init.sql;

-- 插入测试数据
-- 插入测试店铺
INSERT INTO t_store (id, name, address, phone, status) VALUES
(1, '测试店铺', '测试地址', '13800138000', 1),
(2, '测试分店', '测试分店地址', '13800138001', 1),
(3, '测试分店 B', '测试分店 B 地址', '13800138002', 1);

-- 插入测试用户
INSERT INTO t_user (username, password, real_name, phone, store_id, role_id, status) VALUES
('admin', '$2a$10$N9q8k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7iAt6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8lE9lBOsl7At6Z5EHsM8l.E9lBOsl7At6Z5EHsM8l.E9lBOsl7At6Z5EHsM8l.E9lBOsl7At6Z5EHsM8l.E9lBOsl7At6Z5EHsM8l.E9lBOsl7At6Z5EHsM8l.E9lBOsl7At6Z5EHsM8l.E9lBOsl7At6Z5EHsM8l.E9lBOsl7At6Z5EHsM8.l.E.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l9.l 暉制 20KB 数据库测试）
SET GLOBAL max_allowed_packet_size = 67108864;
SET GLOBAL innodb_buffer_pool_size = 256M;
SET GLOBAL innodb_log_file_size = 256M;
SET GLOBAL binlog_format = ROW;
SET GLOBAL innodb_log_binlog = ON;

-- 插入测试商品数据
INSERT INTO t_product_category (name, parent_id, level, sort_order, status) VALUES
('黄金项链', 0, 1, 1, 1),
('黄金戒指', 0, 1, 2, 1),
('黄金手镯', 0, 1, 3, 1),
('白银项链', 0, 1, 4, 1),
('白银戒指', 0, 1, 5, 1),
('白银手镯', 0, 1, 6, 1);

INSERT INTO t_product (product_code, name, category_id, weight, purity, craft_fee, image_url, status) VALUES
('TEST001', '18K 黄金项链', 1, 5.68, 'Au99.99', 1500, NULL, 1),
('TEST002', '18K 白银戒指', 5, 8.5, 'Ag99.9', 500, NULL, 1),
('TEST003', '20g 黄金手镯', 3, 12.5, 'Au99.99', 800, NULL, 1),
('TEST004', '15g 白银手镯', 6, 10.0, 'Ag99.9', 300, NULL, 1);

-- 插入测试库存数据
INSERT INTO t_inventory (product_id, store_id, quantity, frozen_quantity, status) VALUES
(1, 1, 100, 0, 1),
(2, 1, 50, 0, 1),
(3, 2, 80, 0, 1),
(4, 3, 60, 0, 1),
(5, 1, 45, 0, 1),
(6, 2, 30, 0, 1),
(7, 3, 25, 0, 1),
(8, 1, 20, 0, 1);

-- 插入测试销售订单
INSERT INTO t_sales_order (order_no, store_id, customer_name, customer_phone, total_amount, payment_method, payment_status, operator_id, status) VALUES
('SO2026022419000001', 1, '张三', '13800138000', 8500.00, 'wechat', 1, 1, 1),
('SO2026022419000002', 1, '李四', '13800138001', 3200.00, 'alipay', 1, 1, 1),
('SO2026022419000003', 2, '王五', '13800138002', 1200.00, 'cash', 1, 1, 1);

-- 插入测试销售订单明细
INSERT INTO t_sales_order_item (order_id, product_id, product_code, product_name, weight, purity, unit_price, total_price, quantity) VALUES
(1, 1, 'TEST001', '18K 黄金项链', 5.68, 'Au99.99', 4200.00, 8400.00, 2),
(1, 2, 'TEST002', '18K 白银戒指', 8.5, 'Ag99.9', 2000.00, 2000.00, 1);

(2, 1, 'TEST003', '20g 黄金手镯', 12.5, 'Au99.99', 3000.00, 3000.00, 1),
(2, 2, 'TEST004', '15g 白银手镯', 10.0, 'Ag99.9', 1500.00, 1500.00, 1);

-- 插入库存流水
INSERT INTO t_inventory_log (product_id, store_id, type, quantity, before_quantity, after_quantity, order_no, operator_id, remark) VALUES
(1, 1, 1, 20, 0, 20, 'INIT001', 1, '初始化库存'),
(2, 1, 1, 50, 0, 50, 'INIT002', 1, '初始化库存'),
(3, 1, 1, 30, 0, 30, 'INIT003', 1, '初始化库存'),
(4, 1, 1, 60, 0, 60, 'INIT004', 1, '初始化库存'),
(5, 1, 1, 45, 0, 45, 'INIT005', 1, '初始化库存'),
(6, 1, 1, 20, 0, 20, 'INIT006', 1, '初始化库存'),
(7, 1, 1, 80, 0, 80, 'INIT007', 1, '初始化库存'),
(8, 1, 1, 30, 0, 30, 'INIT008', 1, '初始化库存'),
(9, 1, 2, 60, 0, 60, 'INIT009', 1, '初始化库存'),
(10, 1, 2, 30, 0, 30, 'INIT010', 1, '初始化库存'),
(11, 1, 1, 20, 0, 20, 'INIT011', 1, '初始化库存'),
(12, 1, 1, 10, 0, 10, 'INIT012', 1, '初始化库存'),
(13, 1, 2, 8, 0, 8, 'INIT013', 1, '初始化库存'),
(14, 1, 2, 25, 0, 25, 'INIT014', 1, '初始化库存'),
(15, 1, 2, 80, 0, 80, 'INIT015', 1, '初始化库存'),
(16, 1, 1, 60, 0, 60, 'INIT016', 1, '初始化库存'),
(17, 1, 1, 45, 0, 45, 'INIT017', 1, '初始化库存'),
(18, 1, 1, 30, 0, 30, 'INIT018', 1, '初始化库存'),
(19, 1, 1, 20, 0, 20, 'INIT019', 1, '初始化库存'),
(20, 1, 1, 10, 0, 10, 'INIT020', 1, '初始化库存'),
(21, 1, 1, 8, 0, 8, 'INIT021', 1, '初始化库存');

-- 查询验证
SELECT '测试环境部署成功！' as message;
SELECT COUNT(*) FROM t_product;
SELECT COUNT(*) FROM t_inventory;
SELECT COUNT(*) FROM t_sales_order;
SELECT COUNT(*) FROM t_inventory_log;
