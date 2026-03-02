-- 测试环境数据库初始化脚本（SQLite 版本）
-- 创建日期：2026-03-01
-- 用途：初始化测试环境数据库（使用 SQLite）

-- 删除旧数据库
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS watchlists;
DROP TABLE IF EXISTS analysis_tasks;
DROP TABLE IF EXISTS market_scan_results;
DROP TABLE IF EXISTS stock_analysis;
DROP TABLE IF EXISTS backtest_results;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 股票自选表
CREATE TABLE IF NOT EXISTS watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    stocks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 分析任务表
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stock_code TEXT NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    result TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 市场扫描结果表
CREATE TABLE IF NOT EXISTS market_scan_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    scan_date DATE NOT NULL,
    stocks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 股票分析结果表
CREATE TABLE IF NOT EXISTS stock_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,
    stock_name TEXT,
    analysis_date DATE NOT NULL,
    ntdf_score REAL,
    quant_score REAL,
    fusion_score REAL,
    recommendation TEXT,
    confidence TEXT,
    result_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (stock_code, analysis_date)
);

-- 回测结果表
CREATE TABLE IF NOT EXISTS backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    strategy_name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date NOT NULL,
    initial_capital REAL NOT NULL,
    final_capital REAL NOT NULL,
    total_return REAL,
    annual_return REAL,
    max_drawdown REAL,
    sharpe_ratio REAL,
    win_rate REAL,
    profit_loss_ratio REAL,
    trades_count INTEGER,
    result_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 插入测试数据
INSERT INTO users (username, email, password_hash, role) VALUES
    ('test_admin', 'admin@ntdf.com', 'admin123', 'admin'),
    ('test_user', 'user@ntdf.com', 'user123', 'user');

SELECT 'Database initialized successfully!' AS status;
