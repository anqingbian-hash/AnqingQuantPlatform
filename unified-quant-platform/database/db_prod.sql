-- 正式环境数据库初始化脚本
-- 创建日期：2026-03-01
-- 用途：初始化正式环境数据库

-- 删除旧数据库（如果存在）
DROP DATABASE IF EXISTS quant_prod;

-- 创建新数据库
CREATE DATABASE quant_prod
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE quant_prod;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 股票自选表
CREATE TABLE IF NOT EXISTS watchlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    stocks TEXT NOT NULL COMMENT 'JSON格式的股票列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票自选表';

-- 分析任务表
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    result TEXT COMMENT 'JSON格式的分析结果',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析任务表';

-- 市场扫描结果表
CREATE TABLE IF NOT EXISTS market_scan_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scan_date DATE NOT NULL,
    stocks TEXT NOT NULL COMMENT 'JSON格式的股票列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='市场扫描结果表';

-- 股票分析结果表
CREATE TABLE IF NOT EXISTS stock_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    analysis_date DATE NOT NULL,
    ntdf_score DECIMAL(5,2) COMMENT 'NTDF信号评分',
    quant_score DECIMAL(5,2) COMMENT '量化因子评分',
    fusion_score DECIMAL(5,2) COMMENT '融合评分',
    recommendation VARCHAR(20) COMMENT '买卖建议',
    confidence VARCHAR(20) COMMENT '信心度',
    result_json TEXT COMMENT '完整分析结果JSON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_stock_date (stock_code, analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票分析结果表';

-- 回测结果表
CREATE TABLE IF NOT EXISTS backtest_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15,2) NOT NULL,
    final_capital DECIMAL(15,2) NOT NULL,
    total_return DECIMAL(10,4) COMMENT '总收益率',
    annual_return DECIMAL(10,4) COMMENT '年化收益率',
    max_drawdown DECIMAL(10,4) COMMENT '最大回撤',
    sharpe_ratio DECIMAL(10,4) COMMENT '夏普比率',
    win_rate DECIMAL(5,2) COMMENT '胜率',
    profit_loss_ratio DECIMAL(10,4) COMMENT '盈亏比',
    trades_count INT COMMENT '交易次数',
    result_json TEXT COMMENT '完整回测结果JSON',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测结果表';

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX idx_analysis_tasks_user_id ON analysis_tasks(user_id);
CREATE INDEX idx_analysis_tasks_status ON analysis_tasks(status);
CREATE INDEX idx_market_scan_results_user_id ON market_scan_results(user_id);
CREATE INDEX idx_market_scan_results_date ON market_scan_results(scan_date);
CREATE INDEX idx_stock_analysis_code ON stock_analysis(stock_code);
CREATE INDEX idx_stock_analysis_date ON stock_analysis(analysis_date);
CREATE INDEX idx_backtest_results_user_id ON backtest_results(user_id);
CREATE INDEX idx_backtest_results_strategy ON backtest_results(strategy_name);

-- 注意：正式环境不插入测试数据
-- 用户需要通过 Web 界面注册

-- 显示初始化结果
SELECT 'Database initialized successfully!' AS status;
SELECT 'Created tables:' AS info;
SELECT '  - users' AS info;
SELECT '  - watchlists' AS info;
SELECT '  - analysis_tasks' AS info;
SELECT '  - market_scan_results' AS info;
SELECT '  - stock_analysis' AS info;
SELECT '  - backtest_results' AS info;
SELECT 'No test data inserted (production environment)' AS info;
