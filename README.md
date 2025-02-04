# NineBiliRank


![GitHub License](https://img.shields.io/github/license/NineBiliTeam/NineBiliRank) 
![Python Version](https://badgen.net/pypi/python/black)



# 1. 简介

NineBiliRank是一个用于Bilibili数据收集的数据框架，基于httpx, fastapi与asyncio

依靠NineBiliRank，你可以快速的**二次开发**出一个B站视频数据分析平台

你只需要编写`Filter`就可以控制新增数据，以及使用NineBiliRank处理视频数据的相关对象，无需关心爬虫代理和数据更新

内建API实现基于FastAPI，只需要编写`APIRouter`就可以方便的拓展NineBiliRank

欢迎使用，issue，PR

# 2. 基本使用
1. clone本项目
2. 新建虚拟环境并`pip install requirements.txt`。如果使用其他数据库引擎，可能需要安装对应的异步驱动器
3. `cd NineBiliRank`
4. 修改`nbrank.py`
```python
import StartUp
from buildin_apis.basic.v1 import basic_v1_router # 内建路由模块 BASIC V1
from scheduler.reset_database import reset_database # 内建任务 数据库重置
from buildin_hooks.reg_video_from_file import reg_video_from_file # 内建钩子 从文件注册视频

"""
NineBiliRank
在这里编辑你的启动配置
这是个启动脚本示例
"""

if __name__ == "__main__":
    # 初始化NineBiliRank
    StartUp.init(
        # task_：定时任务列表，每一个定时任务按照APScheduler任务语法写在列表内：[[函数名, 触发器], {其他参数的字典...}]
        tasks_=[
            [
                (reset_database, "cron"),
                {"day_of_week": "sat", "hour": 0},
            ]
        ],
        # routers_：路由列表，在这里放入需要拓展的APIRouter
        routers_=[basic_v1_router],
        start_hooks_=[reg_video_from_file]
    )
    # 启动NineBiliRank
    StartUp.run()
```
5. 修改`BasicConfig.yml`，配置数据库等信息
6. 按照`BasicConfig.yml`的说明，修改其他第三方模块的配置....
7. 运行`alembic upgrade head`
8. 运行`python nbrank.py`

# 3. 二次开发

你可以通过继承`BaseProxyPool`，`BaseFilter`快速的重写过滤器和代理池，并传递给`StartUp.init()`来初始化NineBiliRank

# 4. 与NineBiliRank相关的项目

1. NineVocalRank：开发中....


# 5. 内建模块说明
*如果需要添加新的内置模块，欢迎Issue*
1. 过滤器：

| 名称 | 用处 |
|-----|-----|
|NoneFilter|允许所有视频注册|
|VocaloidChinaFilter|只允许符合[周刊中文虚拟歌手](https://eVocalRank.com)定义的中文虚拟歌手曲目注册|
|NBVCDatabaseFilter|符合NBVCDatabase(施工中)定义的中文虚拟歌手曲目注册|

2. APIRouter

 | 名称 | 用处                     | API文档      |
 |-----|------------------------|------------|
|basic_v1_router| 提供基础的数据增删改查功能，和服务器状态查询 | [APIFox](https://apifox.com/apidoc/shared-a554e842-b1a6-4727-aa4e-66ed2454f95c) |

3. ProxyPool

| 名称 | 说明                                                              |
|-----|-----------------------------------------------------------------| 
|NoneProxyPool| 不使用任何代理（不推荐）                                                    |
|JHaoProxyPool| 使用项目[ProxyPool](https://github.com/jhao104/proxy_pool)提供的代理的代理池 |
|MixinProxyPool| (需要在`init()`实例化此代理池)使用多个代理池                                     |

