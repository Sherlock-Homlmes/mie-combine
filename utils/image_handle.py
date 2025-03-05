import os
from typing import Optional, Union
from pathlib import Path, _ignore_error as pathlib_ignore_error

# lib
import aiohttp
import aiofiles
import aiofiles.os


async def path_exists(path: Union[Path, str]) -> bool:
    try:
        await aiofiles.os.stat(str(path))
    except OSError as e:
        if not pathlib_ignore_error(e):
            raise
        return False
    except ValueError:
        return False
    return True


async def save_image(
    url: str, target_path: Optional[str] = None, use_cache: Optional[bool] = False
) -> str:
    if use_cache and await path_exists(target_path):
        return target_path
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                img_name = target_path if target_path else url.split("/")[6].split("?")[0]
                f = await aiofiles.open(img_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
                return img_name


def delete_image(image):
    os.remove(image)
