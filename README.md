# Instagram 粉丝爬虫

一个用于爬取 Instagram 用户粉丝数据的爬虫工具，支持多线程、自动 Cookie 管理和代理验证。

## 功能特性

- **多线程爬取**：根据 Cookie 数量自动调整线程数，提高爬取效率
- **智能 Cookie 管理**：自动验证、评分和清理 Cookie，确保爬虫稳定运行
- **代理支持**：自动验证和清理代理，提高爬取成功率
- **分页获取**：自动处理分页，获取完整的粉丝数据
- **数据存储**：将爬取的数据存储到 MySQL 数据库
- **详细日志**：完善的日志系统，便于问题排查
- **配置灵活**：通过配置文件调整爬虫参数

## 项目结构

```
Ins_Crawler/
├── core/             # 核心爬虫逻辑
│   ├── crawler.py    # 爬虫主逻辑
│   ├── db_worker.py  # 数据库工作线程
│   └── scheduler.py  # 任务调度器
├── pool/             # 资源池管理
│   ├── cookie_pool.py # Cookie 池管理
│   └── proxy_pool.py  # 代理池管理
├── db/               # 数据库操作
│   ├── dao.py        # 数据访问对象
│   └── mysql.py      # MySQL 连接管理
├── task_queue/       # 任务队列
│   └── task_queue.py # 任务队列实现
├── utils/            # 工具函数
│   ├── logger.py     # 日志管理
│   └── tools.py      # 工具函数
├── data/             # 数据文件
│   ├── cookies.txt   # Cookie 列表
│   ├── proxies.txt   # 代理列表
│   └── user_ids.txt  # 用户 ID 列表
├── sql/              # SQL 脚本
│   └── init.sql      # 初始化数据库脚本
├── config.py         # 配置文件
├── main.py           # 主入口文件
└── path.py           # 路径管理
```

## 环境要求

- Python 3.11+
- MySQL 5.7+
- 依赖库：
  - requests
  - pymysql
  - DBUtils
  - colorama

## 安装与配置

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/Ins_Crawler.git
   cd Ins_Crawler
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置数据库**
   - 修改 `config.py` 中的数据库配置
   - 运行 `sql/init.sql` 创建数据库和表

4. **准备数据文件**
   - 在 `data/` 目录下创建以下文件：
     - `user_ids.txt`：每行一个 Instagram 用户 ID
     - `cookies.txt`：每行一个 Instagram Cookie
     - `proxies.txt`：每行一个代理，格式为 `host:port:user:pass`

## 运行爬虫

```bash
python main.py
```

## 配置说明

在 `config.py` 文件中可以调整以下参数：

- `DB_CONFIG`：数据库连接配置
- `USE_PROXY`：是否使用代理
- `MAX_WORKERS`：最大线程数
- `MAX_ATTEMPTS`：最大重试次数
- `QUEUE_SIZE`：任务队列大小
- `BATCH_SIZE`：数据库批处理大小
- `COOKIE_THREAD_RATIO`：线程数与 Cookie 数的最大比例
- `HEADERS`：请求头配置

## 工作原理

1. **初始化**：加载配置、验证 Cookie 和代理
2. **任务调度**：根据 Cookie 数量计算线程数，创建线程池
3. **爬取数据**：每个线程负责爬取一个用户的粉丝数据
4. **数据处理**：将爬取的数据放入任务队列
5. **数据库存储**：数据库工作线程批量处理任务队列中的数据
6. **错误处理**：自动处理 Cookie 失效、网络错误等情况

## 注意事项

1. **Cookie 管理**：定期更新 Cookie，避免被 Instagram 封禁
2. **代理使用**：使用高质量的代理，提高爬取成功率
3. **请求频率**：爬虫会自动控制请求频率，避免被 Instagram 识别为机器人
4. **数据存储**：确保 MySQL 数据库可用，且配置正确

## 常见问题

1. **Cookie 失效**：爬虫会自动检测并删除失效的 Cookie，请确保 `cookies.txt` 中有足够的有效 Cookie
2. **代理不可用**：爬虫会自动检测并删除不可用的代理，请确保 `proxies.txt` 中有足够的有效代理
3. **数据库连接失败**：检查数据库配置和网络连接
4. **爬取速度慢**：可以适当增加 Cookie 数量，爬虫会自动调整线程数

## 改进建议

1. **增加 Cookie 自动更新机制**：定期自动更新 Cookie
2. **实现分布式爬取**：支持多台机器协同爬取
3. **增加数据导出功能**：支持导出为 CSV、JSON 等格式
4. **添加 Web 界面**：方便监控和管理爬虫

## 免责声明

本工具仅供学习和研究使用，请勿用于任何非法或违反 Instagram 服务条款的行为。使用本工具造成的任何后果，由使用者自行承担。
