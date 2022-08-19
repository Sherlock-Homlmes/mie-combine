import os

# environment = "replit"
environment = "local"
if environment == "replit":
	my_secret = os.environ['BOT_TOKEN']
elif environment == "local":
	from dotenv import load_dotenv
	load_dotenv()
	my_secret = os.environ.get('BOT_TOKEN')