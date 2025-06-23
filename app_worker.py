# import nsq
# from data.config.settings import Settings
# from src.services.document_service import DocumentService
# from src.services.request import FilesRequest

# settings = Settings()
# document_service = DocumentService(settings=settings)

# def message_handler(message:nsq.Message):
#     try:
#         message_data= message.body.decode('utf-8')
#         data = FilesRequest.from_json(message_data)
#         document_service.process_files(data.id)
#         message.finish()  # Ensure the message is acknowledged
#     except Exception as e:
#         print(f"Error handling message: {e}")
#         message.requeue()
 
# def app_worker(settings=Settings()):
#     settings.register_cumsumer(message_handler)
    
# if __name__ == '__main__':
#     app_worker()

from apscheduler.schedulers.background import BackgroundScheduler
import time

from data.config.settings import Settings
from src.services.document_service import DocumentService


settings = Settings()
document_service = DocumentService(settings=settings)

def jobs():
    document_service.process_files()
    
    
if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(jobs, 'interval', seconds=10)
    scheduler.start()
    try:
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()