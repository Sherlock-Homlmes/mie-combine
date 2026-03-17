import errno
import os
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

import aiofiles
import aiofiles.os

# lib
import aiohttp
from fastuuid import uuid4


async def path_exists(path: Union[Path, str]) -> bool:
    try:
        await aiofiles.os.stat(str(path))
    except OSError as e:
        if e.errno not in (errno.ENOENT, errno.ENOTDIR, errno.EBADF, errno.EACCES):
            raise
        return False
    except ValueError:
        return False
    return True


def random_filename_from_url(url: str) -> str:
    """Random filename, lấy extension từ URL attachment"""
    ext = os.path.splitext(urlparse(url).path)[1]
    return str(uuid4()) + ext


async def save_image(
    url: str, target_path: Optional[str] = None, use_cache: Optional[bool] = False
) -> str:
    if use_cache and await path_exists(target_path):
        return target_path
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                img_name = (
                    target_path if target_path else url.split("/")[6].split("?")[0]
                )
                f = await aiofiles.open(img_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
                return img_name


def delete_image(image):
    os.remove(image)
