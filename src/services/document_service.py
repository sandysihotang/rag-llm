


import os
import re

from sqlalchemy.orm import Session
from openai import OpenAI
import pandas as pd
from tqdm import tqdm 
import fitz
from data.config.settings import Settings
from data.repository.data_embedding import data_embedding
from data.repository.document import FilesRepository
from models.embeddings import Embeddings
from spacy.lang.en import English

from models.files_model import Files

MODEL = "text-embedding-ada-002"

class DocumentService:
    def __init__(self,settings: Settings, file_upload_dir="/uploads"):
        self.file_upload_dir = file_upload_dir
        self.nlp = English()
        self.nlp.add_pipe('sentencizer')
        self.openAI = OpenAI(api_key=settings.getAISettings().getApiKey())
        self.session = settings.getConnectionDB
        self.api_key = settings.getAISettings().getApiKey()
        pass
    def open_and_read_pdf(self, pdf_path: str) -> list[dict]:
        doc = fitz.open(pdf_path)
        page_and_text = []
        for page_number, page in tqdm(enumerate(doc)):
            text = page.get_text()
            text = text.replace('\n', " ").strip()
            page_and_text.append({"page_number": page_number,
                                  "page_char_count": len(text),
                                  "page_word_count": len(text.split(" ")),
                                  "page_token_count": len(text)/4,
                                  "text": text})
        return page_and_text
    
    def process_file_pdf(self, filedata:Files, session: Session, min_token_length=30,num_sentence_chunk_size=10):
        filepath = os.path.join(self.file_upload_dir,filedata.file_name)
        try:
            pages_and_text = self.open_and_read_pdf(pdf_path = filepath)
        except Exception as e:
            raise
            
        
        for item in tqdm(pages_and_text):
            item['sentences'] = list(self.nlp(item['text']).sents)

            item['sentences'] = [str(sentence) for sentence in item['sentences']]
            item['page_sentences_count_spacy'] = len(item['sentences'])
            item['sentence_chunks'] = self.split_list(input_list=item['sentences'], slice_size=num_sentence_chunk_size)
            item['num_chunks'] = len(item['sentence_chunks'])

        pages_and_chunks = []
        
        for item in tqdm(pages_and_text):
            for sentence_chunk in item['sentence_chunks']:
                chunk_dict = {}
                
                chunk_dict['page_number'] = item['page_number']
                chunk_dict['source_file'] = filedata.original_file_name

                joined_sentence_chunk = "".join(sentence_chunk).replace("  ", "").strip()
                joined_sentence_chunk = re.sub('r\.(A-Z)',r'. \1', joined_sentence_chunk)

                chunk_dict['sentence_chunk'] = joined_sentence_chunk
                chunk_dict['chunk_char_count'] = len(joined_sentence_chunk)
                chunk_dict['chunk_word_count'] = len([word for word in joined_sentence_chunk.split(' ')])
                chunk_dict['chunk_token_count'] = len(joined_sentence_chunk)/4

                pages_and_chunks.append(chunk_dict)
                

        df = pd.DataFrame(pages_and_chunks)
        pages_and_chunks_over_min_token_len = df[df['chunk_token_count'] > min_token_length].to_dict(orient="records")
        new_datas = []
        for item in tqdm(pages_and_chunks_over_min_token_len):
            new_data = Embeddings()
            new_data.page_number = item['page_number']
            new_data.source_file = item['source_file']
            new_data.type_source = 1
            new_data.files_id = filedata.id
            new_data.sentence_chunk = item['sentence_chunk']
            item['embedding'] = self.getVectorData(item['sentence_chunk'])
            
            new_data.embedding_data = item['embedding']
            new_datas.append(new_data)
        try:    
            data_embedding.insert_data_embedding(session=session, data=new_datas)
        except Exception as e:
            print(f"Error occured: {e}")
            raise e
        
    def process_file_txt(self, filedata:Files, session: Session, min_token_length=30,num_sentence_chunk_size=10):
        filepath = os.path.join(self.file_upload_dir,filedata.file_name)
        with open(filepath,'r') as f:
            content = f.read()
            
        item = {}
        
        item['sentences'] = list(self.nlp(content).sents)

        item['sentences'] = [str(sentence) for sentence in item['sentences']]
        item['page_sentences_count_spacy'] = len(item['sentences'])
        item['sentence_chunks'] = self.split_list(input_list=item['sentences'], slice_size=num_sentence_chunk_size)
        item['num_chunks'] = len(item['sentence_chunks'])

        pages_and_chunks = []
        
        
        for sentence_chunk in item['sentence_chunks']:
            chunk_dict = {}
                
            chunk_dict['source_file'] = filedata.original_file_name

            joined_sentence_chunk = "".join(sentence_chunk).replace("  ", "").strip()
            joined_sentence_chunk = re.sub('r\.(A-Z)',r'. \1', joined_sentence_chunk)

            chunk_dict['sentence_chunk'] = joined_sentence_chunk
            chunk_dict['chunk_char_count'] = len(joined_sentence_chunk)
            chunk_dict['chunk_word_count'] = len([word for word in joined_sentence_chunk.split(' ')])
            chunk_dict['chunk_token_count'] = len(joined_sentence_chunk)/4

            pages_and_chunks.append(chunk_dict)
                

        df = pd.DataFrame(pages_and_chunks)
        pages_and_chunks_over_min_token_len = df[df['chunk_token_count'] > min_token_length].to_dict(orient="records")
        new_datas = []
        for item in tqdm(pages_and_chunks_over_min_token_len):
            new_data = Embeddings()
            new_data.source_file = item['source_file']
            new_data.type_source = 2
            new_data.page_number=0
            new_data.files_id = filedata.id
            new_data.sentence_chunk = item['sentence_chunk']
            item['embedding'] = self.getVectorData(item['sentence_chunk'])
            
            new_data.embedding_data = item['embedding']
            new_datas.append(new_data)
        try:    
            data_embedding.insert_data_embedding(session=session, data=new_datas)
        except Exception as e:
            print(f"Error occured: {e}")
            raise e
    # def process_files(self, session: Session):
    #     files_data = FilesRepository.get_data_source(session=session)
    #     if len(files_data) == 0:
    #         print("No data need to process")
    #         return
    #     for data in files_data:
    #         try:
    #             if data.type_data == 1:
    #                 self.process_file_pdf(filedata=data, session= session)
    #             else:
    #                 self.process_file_txt(data)
    #         except Exception as e:
    #             session.rollback()
    #             raise e
            
    #         try:
    #             FilesRepository.update_status_file(session, data.id)
    #         except Exception as e:
    #             session.rollback()
    #             raise e
            
    #         try:
    #             os.remove(path=os.path.join(self.file_upload_dir,data.file_name))  # Delete the file
    #         except Exception as e:
    #             session.rollback()
    #             print(f"Error occurred while deleting the file: {e}")
    #             raise e
    #     session.commit()
        
    def process_files_by_id(self, session: Session, id:int):
        data = FilesRepository.get_data_source_by_id(session=session, id=id)
        if data.status == 2:
            print("No data need to process")
            return
        
        try:
            if data.type_data == 1:
                self.process_file_pdf(filedata=data, session= session)
            else:
                self.process_file_txt(filedata=data, session= session)
        except Exception as e:
            session.rollback()
            raise e
        
        try:
            FilesRepository.update_status_file(session, data.id)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        
        try:
            os.remove(path=os.path.join(self.file_upload_dir,data.file_name))  # Delete the file
        except Exception as e:
            session.rollback()
            print(f"Error occurred while deleting the file: {e}")
            raise e
        
        
    def getVectorData(self, data: str):
        dataEmbedding = self.openAI.embeddings.create(
            model=MODEL,
            input=data,
            encoding_format="float"
        )
        return dataEmbedding.data[0].embedding
    
    def split_list(self, input_list:list[str], slice_size:int=10):
        return [input_list[i:i+slice_size] for i in range (0, len(input_list), slice_size)]
    