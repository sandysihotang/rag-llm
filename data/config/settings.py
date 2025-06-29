import asyncio
import os
from nsq import Writer
import nsq
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import tornado.options
from sqlalchemy.pool import QueuePool
from data.constant import Const
from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env')

class Settings:
    def __init__(self) -> None:
        self.AISettings= OpenAISettings()
        self.ConnDB = OpenConnectionDB()
        self.nsq = PubliserNSQ()
        self.consumer = HandlerNSQ()
        self.key_password = os.getenv(key=Const().KEY_PASSWORD)
    
    def getAISettings(self):
        return self.AISettings
    
    def get_key_password(self):
        return self.key_password
    
    def getConnectionDB(self): 
        return self.ConnDB.ConnectDB
    
    def getNSQConnection(self):
        return self.nsq.ConnectNSQ()
    def register_cumsumer(self, handler):
        self.consumer.register_handler_nsq(handler)

class OpenAISettings:
    def __init__(self):
        self.api_key: str = os.getenv(key=Const().API_KEY)
    def getApiKey(self):
        return self.api_key
    

class OpenConnectionDB():
    def __init__(self):
        self.URL = os.getenv(key=Const().DB_URL)
        conn = create_engine(self.URL, echo=False,poolclass=QueuePool,  
                             pool_size=5,  
                             max_overflow=10,  
                             pool_timeout=30,  
                             pool_recycle=3600)
        self.session = sessionmaker(autocommit= False, autoflush = False, bind=conn)
        
    def ConnectDB(self)->Session:
        db = self.session()
        try:
            yield db
        finally:
            db.close()
    
class PubliserNSQ():
    def __init__(self) -> None:
        pass
        
    def ConnectNSQ(self):
        host = os.getenv(key=Const().NSQ_HOST)
        try:
            # Connect to the NSQ writer (publisher)
            writer = Writer([host])  # Ensure the host is correctly set (e.g., '127.0.0.1:4150')
            return writer
        except Exception as e:
            print(f"Error connecting to NSQ: {e}")
            return None

class HandlerNSQ():
    def register_handler_nsq(self,handler):
        tornado.options.parse_command_line()
        reader = nsq.Reader(topic='my_topic', 
                            channel='my_channel', 
                            nsqd_tcp_addresses=[os.getenv(key=Const().NSQ_READER)],
                            lookupd_http_addresses=[os.getenv('NSQ_LOOKUPD')],
                            message_handler=handler, 
                            max_in_flight=10,)
        nsq.run()
    

        
        