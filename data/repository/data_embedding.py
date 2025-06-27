from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class data_embedding():
    
    @staticmethod
    def insert_data_embedding(session: Session , data: list):
        try:
            session.add_all(data)
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()
            raise
    
    @staticmethod
    def search_data_embedding(session:Session, query: list[float], user_id: int):    
        result = session.execute(text(
        """
        SELECT e.id, e.page_number, f.original_file_name, e.type_source, e.sentence_chunk, e.embedding_data <=> CAST(:query_vector as vector) as similarity_scores, f.type_data
        FROM embedding e inner join files f on e.files_id = f.id
        WHERE f.user_id = :user_id
        ORDER BY similarity_scores
        LIMIT 5
        """),
        {'query_vector': query, 'user_id': user_id}  # Bind the query_vector parameter
    ).fetchall()
        column_names = ['id', 'page_number', 'source_file', 'type_source', 'sentence_chunk', 'similarity_scores', 'type_data']
        datas = []
        for item in result:
            # Zip column names with the tuple values and convert to a dictionary
            item_dict = dict(zip(column_names, item))
            datas.append(item_dict)
        session.close()
        return datas
        