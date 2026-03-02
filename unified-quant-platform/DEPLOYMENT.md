# OpenClaw 统一量化交易平台 v5.0 - 部署指南

## 部署环境要求

### 最低配置
- **操作系统**: Linux (Ubuntu 20.04+, CentOS 7+, Debian 10+)
- **Python**: 3.11+
- **内存**: 2GB+
- **磁盘**: 20GB+
- **网络**: 公网 IP 或内网访问

### 推荐配置
- **操作系统**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **内存**: 4GB+
- **磁盘**: 50GB+
- **CPU**: 2核+

## 环境准备

### 1. 安装 Python 3.11

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# 验证安装
python3 --version  # 应显示 3.11.x
```

### 2. 安装依赖包

```bash
# 进入项目目录
cd /root/.openclaw/workspace/unified-quant-platform

# 安装依赖
pip install flask flask-sqlalchemy pyjwt werkzeug pyyaml

# 验证安装
python3 -c "import flask, sqlalchemy, jwt, yaml; print('依赖安装成功')"
```

### 3. 创建目录结构

```bash
# 创建数据目录
mkdir -p data/test data/prod
mkdir -p logs
mkdir -p cache/test cache/prod
mkdir -p temp/test temp/prod

# 设置权限
chmod 755 data test prod logs cache temp
```

### 4. 配置数据库

#### SQLite（测试环境）

```bash
# 测试环境使用 SQLite，无需额外配置
# 数据库文件: data/test/quant_test.db
```

#### MySQL（生产环境）

```bash
# 安装 MySQL
sudo apt install -y mysql-server mysql-client

# 启动 MySQL
sudo systemctl start mysql

# 创建数据库和用户
sudo mysql -u root -p <<EOF
CREATE DATABASE quant_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'quant_user'@'localhost' IDENTIFIED BY 'quant_password';
GRANT ALL PRIVILEGES ON quant_prod.* TO 'quant_user'@'localhost';
FLUSH PRIVILEGES;
EOF
```

## 部署步骤

### 步骤 1: 配置环境

#### 测试环境

```bash
# 进入项目目录
cd /root/.openclaw/workspace/unified-quant-platform

# 编辑测试环境配置
vi config/config_test.yaml
```

配置文件内容：
```yaml
app:
  name: "OpenClaw 统一量化交易平台 v5.0"
  version: "5.0.0"
  environment: "test"
  debug: true

server:
  host: "0.0.0.0"
  port: 5000
  workers: 1

database:
  type: "sqlite"
  sqlite:
    path: "data/test/quant_test.db"
  mysql:
    host: "localhost"
    port: 3306
    user: "quant_user"
    password: "quant_password"
    database: "quant_prod"

security:
  secret_key: "change-this-to-a-random-32-char-string"
  jwt:
    algorithm: "HS256"
    expiration_hours: 24

logging:
  level: "INFO"
  file: "logs/test.log"

cors:
  enabled: true
  origins: ["*"]
```

#### 生产环境

```bash
# 编辑生产环境配置
vi config/config_prod.yaml
```

配置文件内容（生产环境）：
```yaml
app:
  name: "OpenClaw 统一量化交易平台 v5.0"
  version: "5.0.0"
  environment: "prod"
  debug: false

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

database:
  type: "mysql"
  sqlite:
    path: "data/prod/quant_prod.db"
  mysql:
    host: "localhost"
    port: 3306
    user: "quant_user"
    password: "quant_password"
    database: "quant_prod"

security:
  secret_key: "change-this-to-a-random-32-char-string"
  jwt:
    algorithm: "HS256"
    expiration_hours: 24

logging:
  level: "WARNING"
  file: "logs/prod.log"

cors:
  enabled: true
  origins: ["https://example.com", "https://api.example.com"]
```

### 步骤 2: 启动服务

#### 测试环境

```bash
# 启动测试环境
python3 run_server.py test
```

#### 生产环境

```bash
# 启动生产环境
python3 run_server.py prod
```

### 步骤 3: 验证服务

```bash
# 测试基础 API
curl http://localhost:5000/health

# 测试登录 API
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 测试实时分析 API
curl http://localhost:5000/api/analysis/realtime/600000
```

## 生产环境部署

### 1. 使用 Gunicorn（推荐）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --bind 0.0.0.0:8000 \
  app:app
```

### 2. 使用 Supervisor（进程管理）

```bash
# 安装 Supervisor
sudo apt install -y supervisor

# 创建配置文件
sudo vi /etc/supervisor/conf.d/quant-platform.conf
```

配置内容：
```ini
[program:quant-platform]
command=/root/.openclaw/workspace/unified-quant-platform/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
directory=/root/.openclaw/workspace/unified-quant-platform
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/quant-platform/access.log
stderr_logfile=/var/log/quant-platform/error.log
```

启动服务：
```bash
# 重载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start quant-platform

# 查看状态
sudo supervisorctl status quant-platform
```

### 3. 使用 Nginx（反向代理）

```bash
# 安装 Nginx
sudo apt install -y nginx

# 创建 Nginx 配置
sudo vi /etc/nginx/sites-available/quant-platform
```

配置内容：
```nginx
server {
    listen 80;
    server_name: api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/quant-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 安全配置

### 1. 修改密钥

```bash
# 编辑生产环境配置
vi config/config_prod.yaml

# 修改 security.secret_key 为随机字符串
```

### 2. 配置防火墙

```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. 配置 SSL 证书

```bash
# 使用 Let's Encrypt（免费）
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --standalone -d api.example.com

# 更新 Nginx 配置
sudo vi /etc/nginx/sites-available/quant-platform
```

## 监控和日志

### 1. 查看日志

```bash
# 应用日志
tail -f logs/prod.log

# Nginx 访问日志
tail -f /var/log/nginx/access.log

# Supervisor 日志
tail -f /var/log/quant-platform/access.log
```

### 2. 监控进程

```bash
# 查看 Gunicorn 进程
ps aux | grep gunicorn

# 查看 Supervisor 状态
sudo supervisorctl status quant-platform

# 查看 Nginx 状态
sudo systemctl status nginx
```

## 备份和恢复

### 1. 数据库备份

```bash
# 备份数据库（SQLite）
cp data/prod/quant_prod.db backups/quant_prod_$(date +%Y%m%d).db

# 备份数据库（MySQL）
mysqldump -u quant_user -pquant_password quant_prod | gzip > backups/quant_prod_$(date +%Y%m%d).sql.gz
```

### 2. 数据库恢复

```bash
# 恢复数据库（SQLite）
cp backups/quant_prod_20260301.db data/prod/quant_prod.db

# 恢复数据库（MySQL）
gunzip < backups/quant_prod_20260301.sql.gz | mysql -u quant_user -pquant_password quant_prod
```

## 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_stocks_code ON stocks(code);
```

### 2. 缓存配置

```python
# 使用 Redis 缓存（可选）
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
```

### 3. 连接池配置

```python
# 使用 SQLAlchemy 连接池
engine = create_engine(
    database_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)
```

## 故障排查

### 1. 端口被占用

```bash
# 查看端口占用
sudo netstat -tlnp | grep 5000

# 杀死进程
kill -9 <PID>
```

### 2. 数据库连接失败

```bash
# 检查 MySQL 服务
sudo systemctl status mysql

# 测试连接
mysql -u quant_user -pquant_password -h localhost quant_prod
```

### 3. 500 错误

```bash
# 查看应用日志
tail -f logs/prod.log

# 检查 Nginx 日志
tail -f /var/log/nginx/error.log
```

## 总结

### 部署清单

- [x] 环境准备完成
- [x] 依赖安装完成
- [x] 配置文件配置完成
- [x] 数据库创建完成
- [ ] 服务启动测试
- [ ] API 功能测试
- [ ] 安全配置完成
- [ ] SSL 证书配置
- [ ] Nginx 反向代理配置
- [ ] 监控系统配置
- [ ] 备份策略配置

### 部署注意事项

1. **安全优先**: 修改默认密码、配置防火墙
2. **数据备份**: 定期备份数据库
3. **监控告警**: 配置日志监控和告警
4. **性能优化**: 根据实际情况调整配置

---

**部署指南** | OpenClaw 统一量化交易平台 v5.0
**更新时间**: 2026-03-01 20:30
**版本**: v5.0
