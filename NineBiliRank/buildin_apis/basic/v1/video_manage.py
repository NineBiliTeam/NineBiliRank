from fastapi import APIRouter
from fastapi.params import Form, Depends

from bilibili_modles.Video import Video
from buildin_apis.basic.v1.models import (
    ResponseStatus,
    ResponseModel,
    ResponseStatusMessage,
)
from buildin_apis.depends.key_auth import key_auth
from config import get_filter
from database.utils.add_video import add_video_to_db
from database.utils.delete_video import delete_video
from database.utils.update_video import update_video

video_manager_router = APIRouter(
    prefix="/video_manager", tags=["Manage"], dependencies=[Depends(key_auth)]
)


@video_manager_router.post("/reg_new_video")
async def reg_video(vid: str = Form(title="视频ID（支持AVID与BVID）")) -> ResponseModel:
    _filter = get_filter()
    video = Video(vid)
    await video.async_update_basic_data()
    is_legal = await _filter.check(video)
    if not is_legal:
        return ResponseModel(
            code=ResponseStatus.video_is_invalid,
            message=ResponseStatusMessage.video_is_invalid,
            data=video,
        )
    await add_video_to_db(video)
    return ResponseModel(
        code=ResponseStatus.success, message=ResponseStatusMessage.success, data=video
    )


@video_manager_router.delete("/delete_video")
async def delete_video_(vid: str = Form("视频ID（支持AVID与BVID）")) -> ResponseModel:
    video = Video(vid)
    await video.async_update_basic_data()
    await delete_video(video)
    return ResponseModel(
        message=ResponseStatusMessage.success, code=ResponseStatus.success, data=video
    )


@video_manager_router.post("/update_video")
async def update_video_(vid: str = Form("视频ID（支持AVID与BVID）")) -> ResponseModel:
    video = Video(vid)
    await video.async_update_basic_data()
    await update_video(video)
    return ResponseModel(
        message=ResponseStatusMessage.success, code=ResponseStatus.success, data=video
    )
