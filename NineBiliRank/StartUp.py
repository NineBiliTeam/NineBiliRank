from contextlib import asynccontextmanager
from types import coroutine

import fastapi_cdn_host
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, APIRouter
from fastapi.params import Depends
from starlette.responses import JSONResponse
from uvicorn_loguru_integration import run_uvicorn_loguru

from buildin_apis.depends.key_auth import key_auth
from config import get_config, get_apikey, get_config_from_file, Config
from exceptions.BilibiliException import BilibiliException
from filter.BaseFilter import BaseFilter
from http_utils.proxy.BaseProxyPool import BaseProxyPool
from logger import logger

tasks, scheduler = list(), AsyncIOScheduler()
routers = list()


@asynccontextmanager
async def start_hook(_app: FastAPI):
    """
    FastAPI启动钩子
    """
    for task in tasks:
        scheduler.add_job(*task[0], **task[1])
        logger.success(f"成功启用定时任务：{task[0][0].__name__}")
    scheduler.start()
    for hook_ in start_hooks:
        logger.info(f"正在运行启动钩子：{hook_.__name__}")
        await hook_()
    logger.success("启动挂钩执行完毕")
    host = config["basic_config"]["server"]["host"]
    port = config["basic_config"]["server"]["port"]
    logger.success(
        f"服务器启动完成...：\n"
        f"    -- 地址：http://{host}:{port}\n"
        f"    -- 文档地址：http://{host}:{port}/redoc\n"
        f"    -- OpenAPI: http://{host}:{port}/openapi.json\n"
        f"    -- API密钥（原始）：{get_config()["basic_config"]["server"]["apikey"]}\n"
        f"    -- API密钥（md5散列后）:{get_apikey()}\n"
        f"    -- API全局锁开启状态：{get_config()["basic_config"]["server"]["enable_lock"]}\n"
    )
    yield


def init(
    filter_=None,
    tasks_=None,
    proxy_pool=None,
    routers_=None,
):
    """
    初始化NineBiliRank
    :param filter_: 视频过滤器
    :param tasks_: 定时任务列表：[[函数名, 触发器], {其他参数的字典...}]
    :param proxy_pool: 自定义代理源
    :param routers_: 自定义APIRouter列表
    :return:
    """
    global tasks, routers
    if tasks_ is None:
        tasks_ = []
    if routers_ is None:
        routers_ = []
    Config.get_instance(proxy_pool=proxy_pool, filter_=filter_)
    routers = routers_
    tasks = tasks_


config = get_config_from_file()
fastapi_app: FastAPI = FastAPI(
    lifespan=start_hook,
    dependencies=(
        []
        if not get_config()["basic_config"]["server"]["enable_lock"]
        else [Depends(key_auth)]
    ),
    title=config["basic_config"]["server"]["title"],
    version=config["basic_config"]["server"]["version"],
)

fastapi_cdn_host.patch_docs(fastapi_app)

start_hooks = list()


def reg_start_hooks(func: callable):
    start_hooks.append(func)

from buildin_hooks import reg_video_from_file


@logger.catch
def run(debug: bool = False, *args, **kwargs):
    logger.info(f"服务器启动中...")
    host = config["basic_config"]["server"]["host"]
    port = config["basic_config"]["server"]["port"]
    if routers == []:
        logger.warning("没有发现任何路由...")
    for router in routers:
        fastapi_app.include_router(router)
        logger.success(f"成功导入路由：{router.prefix}")

    if debug:
        uvicorn.run(
            "StartUp:fastapi_app", host=host, port=port, reload=True, reload_delay=0.01
        )
    else:
        run_uvicorn_loguru(
            uvicorn.Config(
                "StartUp:fastapi_app",
                host=host,
                port=port,
                reload=debug,
                reload_delay=0.01,
            )
        )


@fastapi_app.exception_handler(BilibiliException)
async def bilibili_exception_handler(_, exception: BilibiliException):
    return JSONResponse(
        {
            "message": f"{exception.__class__.__name__}: {exception.args}",
            "code": -400,
            "data": [],
        }
    )
