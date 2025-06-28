# import asyncio
from datetime import datetime
import json
import re
import uuid
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse
# from nsq import Error
import os
from openai import OpenAI
import requests
from data.config.settings import Settings
from data.repository.chat_history import ChatHistoryRepository
from data.repository.data_embedding import data_embedding
from data.repository.document import FilesRepository
from fastapi import HTTPException, status
from models.chat_history import ChatHistory
from models.files_model import Files
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

MODEL = "text-embedding-ada-002"

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # Convert SQLAlchemy model to dictionary
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)


class RagModel():
    def __init__(self, settings: Settings, file_upload_dir="uploads"):
        self.file_upload_dir = file_upload_dir
        self.allowed_files = {'pdf'}
        self.openAI = OpenAI(api_key=settings.getAISettings().getApiKey())
        self.session = settings.getConnectionDB()
        self.api_key = settings.getAISettings().getApiKey()
        # self.publiser = settings.getNSQConnection()
        
        
    async def publish_message(self, message:str):
        try:
            await self.publiser.pub('my_topic', message.encode(), callback=self.on_publish)
        except Exception as e:
            print(f"Error while publishing message: {e}")
    
    def on_publish(self,conn, data):
        if isinstance(data, Error):
            print("Error Published data")
        else:
            print("success published data")

    def getVectorData(self, data: str):
        dataEmbedding = self.openAI.embeddings.create(
            model=MODEL,
            input=data,
            encoding_format="float"
        )
        return dataEmbedding.data[0].embedding

    def prompt_formatter(self, query: str, history_chat:list ,context_items):
        context = ''
        for item in context_items:
            pages = ''
            if item['page_number'] != 0:
                pages += f", Page: {item['page_number']+1}"
            context += '- ' + f'Document: {item["source_file"]}' + pages + f', Context: {item["sentence_chunk"]}\n'        
        base_prompt = """
            # Role and Purpose
            You are an AI assistant designed to assist the user. Your task is to synthesize a coherent and helpful answer based on the given question and the relevant context retrieved from a knowledge database.

            # Guidelines:
            1. Provide a clear and concise answer to the user's question.
            2. Only use the information from the relevant context or previous chat history (if available) to support your answer.
            3. The context is retrieved based on cosine similarity, so some information may be missing or irrelevant. Be mindful of this.
            4. If there is insufficient information to fully answer the question, be transparent and clearly state that.
            5. Avoid making up or inferring information not present in the provided context.
            6. If the question has related previous content, incorporate it into the current answer for completeness.
            7. Maintain a helpful, professional, and polite tone throughout your response.
            8. Ensure your response is helpful, staying faithful to the provided information without speculating.
            9. When referencing the provided document and page (if available), give the answer with the document and page number from the context, and write your the document and pages at the bottom.

            Remember: Your goal is to be as helpful as possible while strictly adhering to the provided context and history.

            Please review the question and relevant context before responding!!!
            """
        
        history_chat.append({
            'role': 'user',
            'content': f'All Context: {context}, Question: {query}'
        })
        history_chat.append({
            'role': 'system',
            'content': base_prompt
        })
        return history_chat

    def get_history_message(self, user_id: int, session:Session):
        try: 
            history_message = ChatHistoryRepository.get_history_message(session,user_id=user_id)
            data = [history.to_dict() for history in history_message]
            return JSONResponse(status_code=200, content=data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
    def generate_history_message(self, history_chat: list[ChatHistory]):
        history_chats = []
        for i in range(len(history_chat)-1, -1, -1):
            item = history_chat[i]
            if item.messages_from == 1:
                history_chats.append({
                    'role': 'user',
                    'content': item.messages
                })
            else:
                context_if_exist = f'{"Context answer: " if len(item.context_answer) != 0 else ""} {item.context_answer}'
                history_chats.append({
                    'role': 'assistant',
                    'content': f'{item.messages}\n\n{context_if_exist}'
                })
        return history_chats
    def ask(self,query,user_id: int, session: Session, format_answer_text=True,return_answer_only=True):
        embedding = self.getVectorData(query)
        
        similarity_data = data_embedding.search_data_embedding(session,embedding, user_id=user_id)
        if len(similarity_data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User never upload the context")
        chat_history_context = ChatHistoryRepository.get_history_message_for_context(session, user_id=user_id)
        prompt_history_messsage = self.generate_history_message(history_chat=chat_history_context)
        prompt= self.prompt_formatter(query=query, history_chat=prompt_history_messsage ,context_items=similarity_data)
        try:
            new_chat_user = ChatHistory(user_id=user_id, messages= query, messages_from= 1, create_time=datetime.now())
            ChatHistoryRepository.insert_new_chat(session, new_chat_user)
        except Exception as e:
            session.rollback()
            raise e
        self.chat_gpt_client = OpenAI(api_key=self.api_key)

        response = self.chat_gpt_client.chat.completions.create(
            messages=prompt,
            model="gpt-3.5-turbo"
        )
        output_text = response.choices[0].message.content
        if format_answer_text:
            output_text = output_text.strip()

        if return_answer_only:
            return output_text
        
        reference = []
        map_source = {}
        for item in similarity_data:
            if item["type_data"] == 1:
                if f'{item["source_file"]}-{str(item["page_number"]+1)}' not in map_source:
                    reference.append({"source": item["source_file"], "page":item["page_number"]+1,"type": 1})
                map_source[f'{item["source_file"]}-{str(item["page_number"]+1)}'] = True
            else:
                if f'{item["source_file"]}' not in map_source:
                    reference.append({"source": item["source_file"], "type":2})
                map_source[f'{item["source_file"]}'] = True
            
        try:
            new_chat_bot = ChatHistory(user_id=user_id, messages= output_text, messages_from= 2, reference= reference, create_time=datetime.now(), context_answer= '- ' + '\n- '.join([item['sentence_chunk'] for item in similarity_data]))
            data = ChatHistoryRepository.insert_new_chat(session, new_chat_bot)
        except Exception as e:
            session.rollback()
            raise e
        
        session.commit()
        return data.to_dict()

    async def processing_file(self, original_file_name: str, content, user_id: int, session:Session):
        if self.allowed_file(filename= original_file_name):
            filename = self.get_new_file_name()
            save_path = f'./uploads/{filename}.pdf'
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(content)
            
            new_files = Files(user_id = user_id, file_name=f'{filename}.pdf', original_file_name= original_file_name, status = 1, type_data=1)
            FilesRepository.insert_data_document(session, new_files)
            
            session.commit()
            
            return JSONResponse(status_code=200, content=f'file {filename} uploaded succesfully')
        else:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File type not allowed')
    
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_files

    def get_new_file_name(self):
        s = uuid.uuid1()
        return f'{s}'
            
    async def publish_message(self, message):
        try:
            await self.publiser.pub('my_topic', message, callback=self.on_publish)
        except Exception as e:
            print(f"Error while publishing message: {e}")

    async def get_text_from_url(self, url:str):
        try:
            r = requests.get(url=url)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text(separator=' ')
            text = text.replace('\n', " ").strip()
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            return JSONResponse(status_code=200,content={"data": cleaned_text.strip(), "title":url})
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
        
    async def get_source(self, user_id: int, session:Session):
        try: 
            all_data = FilesRepository.get_source_data_by_user_id(session, user_id)
            data = [file.to_dict() for file in all_data]
            return JSONResponse(status_code=200, content=data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
        
    async def processing_data(self, title: str, content: str, user_id: int, session: Session):
        content = content.replace('\n', " ").strip()
        cleaned_text = re.sub(r'\s+', ' ', content).strip()
        filename = self.get_new_file_name()
        with open(os.path.join("uploads",f"{filename}.txt"), 'w') as f:
            f.write(cleaned_text)
        new_files = Files(user_id = user_id, file_name=f'{filename}.txt', original_file_name= title, status = 1, type_data=2)
        try:
            FilesRepository.insert_data_document(session, new_files)
            session.commit()
            return JSONResponse(status_code=200, content=f'{title} Processing')
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= e)