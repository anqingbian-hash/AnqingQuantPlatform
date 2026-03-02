# 黄金白银贵金属首饰管理系统 - 上线部署指南

**项目名称**：黄金白银贵金属首饰管理系统
**版本**：1.0.0
**部署日期**：2026-02-24
**部署人员**：变形金刚（AI 总经理）
**项目路径**：/root/.openclaw/workspace/gold-jewelry-system

---

## 一、服务器环境要求

### 1.1 硬件配置（推荐）

| 配置项 | 最小配置 | 推荐配置 |
|--------|----------|----------|
| CPU | 2 核 4G | 4 核 8G |
| 内存 | 4G | 8G |
| 硬盘 | 50GB SSD | 100GB SSD |
| 带宽 | 10Mbps | 100Mbps |

### 1.2 软件环境

| 软件 | 版本 | 用途 |
|------|------|------|
| Java | 17+ | 后端运行环境 |
| MySQL | 8.0+ | 数据库 |
| Maven | 3.9+ | 后端构建工具 |
| Node.js | 18+ | 前端运行环境 |
| Nginx | 1.20+ | 反向代理 |
| Redis | 7.x+ | 缓存（可选） |

---

## 二、环境安装

### 2.1 安装 Java 17

```bash
# 1. 下载 OpenJDK 17
wget https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz

# 2. 解压
tar -xzf openjdk-17.0.2_linux-x64_bin.tar.gz
mv jdk-17.0.2 /usr/local/java/

# 3. 配置环境变量
echo 'export JAVA_HOME=/usr/local/java' >> ~/.bashrc
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc
source ~/.bashrc

# 4. 验证安装
java -version
```

### 2.2 安装 MySQL 8.0

```bash
# 1. 下载 MySQL Yum Repository
wget https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm

# 2. 安装 Repository
rpm -ivh mysql80-community-release-el7-3.noarch.rpm

# 3. 安装 MySQL
yum install mysql-server -y

# 4. 启动 MySQL
systemctl start mysqld
systemctl enable mysqld

# 5. 获取临时密码
grep 'temporary password' /var/log/mysqld.log

# 6. 登录并修改密码
mysql -u root -p
# 输入临时密码，然后修改密码
ALTER USER 'root'@'localhost' IDENTIFIED BY 'YourNewPassword!';
FLUSH PRIVILEGES;
EXIT;
```

### 2.3 安装 Maven 3.9+

```bash
# 1. 下载 Maven
wget https://dlcdn.apache.org/maven/maven-3/3.9.5/binaries/apache-maven-3.9.5-bin.tar.gz

# 2. 解压
tar -xzf apache-maven-3.9.5-bin.tar.gz
mv apache-maven-3.9.5 /usr/local/maven/

# 3. 配置环境变量
echo 'export MAVEN_HOME=/usr/local/maven' >> ~/.bashrc
echo 'export PATH=$PATH:$MAVEN_HOME/bin' >> ~/.bashrc
source ~/.bashrc

# 4. 验证安装
mvn -version
```

### 2.4 安装 Nginx

```bash
# 1. 安装 Nginx
yum install nginx -y

# 2. 启动 Nginx
systemctl start nginx
systemctl enable nginx

# 3. 验证安装
nginx -v
```

### 2.5 安装 Redis（可选）

```bash
# 1. 下载 Redis
wget http://download.redis.io/releases/redis-7.0.14.tar.gz

# 2. 解压并编译
tar -xzf redis-7.0.14.tar.gz
cd redis-7.0.14
make

# 3. 安装
make install

# 4. 启动 Redis
redis-server &

# 5. 验证安装
redis-cli ping
# 应该返回 PONG
```

---

## 三、数据库配置

### 3.1 创建生产数据库

```bash
# 1. 登录 MySQL
mysql -u root -p

# 2. 创建数据库
CREATE DATABASE gold_jewelry CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 3. 创建用户（可选，更安全）
CREATE USER 'goldjewelry'@'localhost' IDENTIFIED BY 'YourPassword!';
GRANT ALL PRIVILEGES ON gold_jewelry.* TO 'goldjewelry'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3.2 导入数据库结构

```bash
# 1. 上传初始化脚本到服务器
scp /root/.openclaw/workspace/gold-jewelry-system/backend/src/main/resources/sql/init.sql root@your-server:/root/

# 2. 导入数据库结构
mysql -u root -p gold_jewelry < init.sql

# 3. 验证导入
mysql -u root -p gold_jewelry -e "SHOW TABLES;"
```

---

## 四、后端部署

### 4.1 上传代码

```bash
# 1. 压缩项目
cd /root/.openclaw/workspace
tar -czf gold-jewelry-system.tar.gz gold-jewelry-system/

# 2. 上传到服务器
scp gold-jewelry-system.tar.gz root@your-server:/root/

# 3. 解压
ssh root@your-server
cd /root
tar -xzf gold-jewelry-system.tar.gz
cd gold-jewelry-system/backend
```

### 4.2 修改配置文件

```bash
# 1. 编辑 application.yml
vim backend/src/main/resources/application.yml
```

修改以下配置：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/gold_jewelry?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
    username: root
    password: YourPassword

  redis:
    host: localhost
    port: 6379
    password:  # 如果有密码

app:
  name: 黄金白银贵金属首饰管理系统
  environment: production
```

### 4.3 编译打包

```bash
cd backend

# 清理并打包
mvn clean package -Dmaven.test.skip=true

# 打包成功后，生成 JAR 文件
# backend/target/gold-jewelry-management-system-1.0.0.jar
```

### 4.4 启动后端

```bash
# 方式 1：直接启动（开发环境）
java -jar target/gold-jewelry-management-system-1.0.0.jar

# 方式 2：后台启动（生产环境推荐）
nohup java -jar target/gold-jewelry-management-system-1.0.0.jar > logs/app.log 2>&1 &

# 方式 3：使用 systemd 管理服务（生产环境最佳）
vim /etc/systemd/system/gold-jewelry.service
```

添加以下内容：

```ini
[Unit]
Description=Gold Jewelry Management System
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/gold-jewelry-system/backend
ExecStart=/usr/local/java/bin/java -jar /root/gold-jewelry-system/backend/target/gold-jewelry-management-system-1.0.0.jar
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
systemctl daemon-reload
systemctl start gold-jewelry
systemctl enable gold-jewelry

# 查看状态
systemctl status gold-jewelry

# 查看日志
journalctl -u gold-jewelry -f
```

### 4.5 验证后端启动

```bash
# 1. 检查端口
netstat -tlnp | grep 8080

# 2. 测试 API
curl http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
      "username": "admin",
      "password": "admin123"
    }'

# 预期返回：
{
  "code": 200,
  "message": "登录成功",
  "data": {...}
}
```

---

## 五、前端部署

### 5.1 上传代码

```bash
# 前端代码已经在 gold-jewelry-system.tar.gz 中
cd /root/gold-jewelry-system/frontend
```

### 5.2 安装依赖

```bash
# 安装依赖
npm install

# 如果安装慢，可以使用淘宝镜像
npm install --registry=https://registry.npmmirror.com
```

### 5.3 构建生产版本

```bash
# 构建生产版本
npm run build

# 构建成功后，生成 dist 目录
# frontend/dist/
```

### 5.4 配置 Nginx

```bash
# 1. 创建 Nginx 配置文件
vim /etc/nginx/conf.d/gold-jewelry.conf
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或服务器 IP

    # 前端静态资源
    location / {
        root /root/gold-jewelry-system/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 日志配置
    access_log /var/log/nginx/gold-jewelry-access.log;
    error_log /var/log/nginx/gold-jewelry-error.log;
}
```

### 5.5 启动 Nginx

```bash
# 1. 测试配置
nginx -t

# 2. 重启 Nginx
systemctl restart nginx

# 3. 验证 Nginx 启动
systemctl status nginx
```

### 5.6 验证前端部署

```bash
# 访问前端
# 浏览器打开：http://your-domain.com/

# 应该看到登录页面
```

---

## 六、SSL 证书配置

### 6.1 申请 Let's Encrypt SSL 证书

```bash
# 1. 安装 Certbot
yum install certbot python2-certbot-nginx -y

# 2. 申请证书（自动配置 Nginx）
certbot --nginx -d your-domain.com

# 3. 自动续期
certbot renew --dry-run
```

### 6.2 手动配置 SSL（可选）

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... 其他配置 ...
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 七、域名解析

### 7.1 配置 DNS

1. 登录域名注册商（阿里云、腾讯云等）
2. 找到域名管理
3. 添加 DNS 记录：

| 类型 | 主机记录 | 记录值 |
|------|----------|--------|
| A | @ | 服务器 IP 地址 |
| A | www | 服务器 IP 地址 |

### 7.2 验证 DNS 解析

```bash
# 1. 检查 DNS 解析
nslookup your-domain.com

# 2. 检查服务器防火墙
firewall-cmd --list-all

# 3. 开放 HTTP/HTTPS 端口
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

---

## 八、防火墙配置

### 8.1 开放端口

```bash
# 1. 开放 HTTP/HTTPS 端口
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https

# 2. 开放 SSH 端口（如果需要）
firewall-cmd --permanent --add-port=22/tcp

# 3. 重新加载防火墙
firewall-cmd --reload

# 4. 查看防火墙状态
firewall-cmd --list-all
```

### 8.2 禁用不必要端口

```bash
# 禁用 3306（MySQL）外部访问
firewall-cmd --permanent --remove-port=3306/tcp

# 禁用 6379（Redis）外部访问
firewall-cmd --permanent --remove-port=6379/tcp

# 重新加载防火墙
firewall-cmd --reload
```

---

## 九、监控告警

### 9.1 应用监控（可选）

**Spring Boot Actuator**：

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: always
```

访问健康检查：
```bash
curl http://localhost:8080/actuator/health
```

### 9.2 数据库监控

**MySQL 慢查询日志**：

```sql
-- 在 MySQL 中执行
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';
```

### 9.3 日志管理

**日志轮转**：

```bash
# 1. 创建日志轮转配置
vim /etc/logrotate.d/gold-jewelry
```

添加以下内容：

```
/root/gold-jewelry-system/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

---

## 十、备份与恢复

### 10.1 数据库备份

```bash
# 1. 创建备份脚本
vim /root/backup-db.sh
```

添加以下内容：

```bash
#!/bin/bash
# 数据库备份脚本

# 配置
DB_NAME="gold_jewelry"
DB_USER="root"
DB_PASS="YourPassword"
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/gold_jewelry_$DATE.sql.gz

# 删除 7 天前的备份
find $BACKUP_DIR -name "gold_jewelry_*.sql.gz" -mtime +7 -delete

echo "Backup completed: gold_jewelry_$DATE.sql.gz"
```

```bash
# 2. 添加执行权限
chmod +x /root/backup-db.sh

# 3. 设置定时任务（每天凌晨 2 点备份）
crontab -e
```

添加以下内容：

```
0 2 * * * /root/backup-db.sh >> /root/backup-db.log 2>&1
```

### 10.2 数据库恢复

```bash
# 1. 解压备份文件
gunzip -c /root/backups/gold_jewelry_20260224_020000.sql.gz | mysql -u root -p gold_jewelry

# 2. 验证恢复
mysql -u root -p gold_jewelry -e "SELECT COUNT(*) FROM t_product;"
```

### 10.3 代码备份

```bash
# 定期备份代码（可选）
rsync -avz /root/gold-jewelry-system/ /root/backups/code-backup/
```

---

## 十一、安全加固

### 11.1 MySQL 安全

```sql
-- 1. 删除匿名用户
DELETE FROM mysql.user WHERE User='';

-- 2. 删除测试数据库
DROP DATABASE IF EXISTS test;

-- 3. 禁用 root 远程登录
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- 4. 刷新权限
FLUSH PRIVILEGES;
```

### 11.2 系统安全

```bash
# 1. 更新系统
yum update -y

# 2. 安装 fail2ban（防止暴力破解）
yum install fail2ban -y

# 3. 配置 fail2ban
vim /etc/fail2ban/jail.local
```

添加以下内容：

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/secure
```

```bash
# 4. 启动 fail2ban
systemctl start fail2ban
systemctl enable fail2ban
```

---

## 十二、上线检查清单

### 12.1 部署前检查

- [ ] 服务器硬件满足要求
- [ ] Java 17 已安装
- [ ] MySQL 8.0 已安装
- [ ] Maven 3.9+ 已安装
- [ ] Nginx 已安装
- [ ] 数据库已创建
- [ ] 数据库结构已导入
- [ ] 代码已上传
- [ ] 配置文件已修改
- [ ] 防火墙已配置

### 12.2 部署后检查

- [ ] 后端服务已启动
- [ ] 前端服务已启动
- [ ] Nginx 已启动
- [ ] 数据库连接正常
- [ ] Redis 连接正常（如果使用）
- [ ] 域名解析正确
- [ ] SSL 证书已安装
- [ ] 日志正常输出
- [ ] 备份脚本已配置
- [ ] 监控告警已配置

### 12.3 功能检查

- [ ] 登录功能正常
- [ ] 商品管理正常
- [ ] 库存管理正常
- [ ] 销售管理正常
- [ ] 店铺管理正常
- [ ] 调拨管理正常
- [ ] 盘点管理正常

---

## 十三、常见问题

### 13.1 后端无法启动

**问题**：后端启动失败，报错 Connection refused

**解决方案**：
1. 检查 MySQL 是否启动：`systemctl status mysqld`
2. 检查数据库连接配置：`vim application.yml`
3. 检查数据库是否存在：`mysql -u root -p -e "SHOW DATABASES;"`

### 13.2 前端无法访问

**问题**：访问域名，显示 404 或 502 错误

**解决方案**：
1. 检查 Nginx 是否启动：`systemctl status nginx`
2. 检查 Nginx 配置：`nginx -t`
3. 检查前端文件是否存在：`ls -la /root/gold-jewelry-system/frontend/dist`
4. 检查后端是否启动：`curl http://localhost:8080/actuator/health`

### 13.3 数据库连接失败

**问题**：后端报错，无法连接数据库

**解决方案**：
1. 检查 MySQL 是否启动：`systemctl status mysqld`
2. 检查数据库用户名和密码
3. 检查数据库防火墙：`firewall-cmd --list-ports`
4. 检查 MySQL 允许的 IP：`mysql -u root -p -e "SELECT host, user FROM mysql.user;"`

---

## 十四、优化建议

### 14.1 性能优化

**数据库优化**：
- 添加索引：`CREATE INDEX idx_product_code ON t_product(product_code);`
- 优化查询：避免 SELECT *，只查询需要的字段
- 使用连接池：HikariCP 已配置

**应用优化**：
- 启用 Redis 缓存（减少数据库查询）
- 使用 CDN（加速静态资源加载）
- 开启 Gzip 压缩（Nginx 已配置）

### 14.2 安全优化

- 定期更新系统：`yum update -y`
- 定期备份数据库：每天自动备份
- 配置防火墙：只开放必要的端口
- 使用 SSL 证书：HTTPS 加密传输
- 限制登录失败次数：防止暴力破解

### 14.3 可用性优化

- 配置主从复制（数据库）
- 配置负载均衡（多台服务器）
- 配置自动故障转移（Keepalived）
- 配置日志告警（钉钉/邮件）

---

## 十五、联系方式

**技术支持**：
- 邮箱：support@goldjewelry.com
- 电话：400-XXX-XXXX
- 微信：goldjewelry-support

**紧急联系**：
- 电话：138-XXXX-XXXX

---

**部署指南编制**：变形金刚（AI 总经理）
**编制日期**：2026-02-24
**指南版本**：1.0.0
