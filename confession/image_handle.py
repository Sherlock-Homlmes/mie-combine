import requests
import asyncio
import os

def save_image(url):
  img_data = requests.get(url).content
  img_name = url.split("/")[-1]
  with open(img_name, 'wb') as handler:
    handler.write(img_data)
    
  return img_name

async def delete_image(image):
	await asyncio.sleep(3)
	os.remove(image)


