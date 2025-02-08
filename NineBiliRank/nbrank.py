import asyncio

from logger import logger
import startup
from buildin_apis.basic.v1 import basic_v1_router
from buildin_hooks.reg_video_from_file import reg_video_from_file
from scheduler.reset_database import reset_database

"""
NineBiliRank
在这里编辑你的启动配置
这是个启动脚本示例
"""

# 在routers列表内写入你要启用的路由模块

if __name__ == "__main__":
    # 初始化NineBiliRank
    startup.init(
        tasks_=[
            [
                (reset_database, "cron"),
                {"day_of_week": "sat", "hour": 0},
            ]
        ],
        routers_=[basic_v1_router],
        start_hooks_=[reg_video_from_file],
        async_start_tasks_=[reset_database],
    )
    # 启动NineBiliRank
    startup.run()
