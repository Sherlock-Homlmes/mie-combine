import os

# lib
import aiohttp
import aiofiles


async def save_image(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                img_name = url.split("/")[6].split("?")[0]
                f = await aiofiles.open(img_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
                return img_name


def delete_image(image):
    os.remove(image)
