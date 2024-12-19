import mongoengine as me
import os

from dotenv import load_dotenv
load_dotenv()
# if :
#     raise FileNotFoundError(os.getenv("MONGO_URI"))

me.connect(host=os.getenv("MONGO_URI"))