import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_core.documents import Document
from langchain_community.document_loaders.csv_loader import CSVLoader

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

import json
import pandas as pd
import ast
from dotenv import load_dotenv



# 환경 변수 로드
load_dotenv(override=True)

# Google API 키 설정
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# 웹 문서 로더
def load_url_and_split_documents(urls: list):
    """
    여러 URL에서 문서를 로드하고 청크로 분할합니다.

    Args:
        urls (list): 데이터를 가져올 URL 리스트.

    Returns:
        list: 분할된 문서 청크 리스트.
    """
    all_docs = []
    for url in urls:
        print(f"Loading data from: {url}")
        loader = WebBaseLoader(url)
        docs = loader.load()
        all_docs.extend(docs)
    
    # chunk_size를 더 크게 설정
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
        chunk_overlap=80)
    splits = text_splitter.split_documents(all_docs)
    return splits


# csv 데이터 문서 로더
def load_csv_and_split_documents(file_path):
    """
    csv 파일 형태의 데이터를 로딩해서 데이터 스플릿함
    """

    loader = CSVLoader(
        file_path=file_path, 
        source_column="제목명",
        # metadata_columns=['일련번호','미디어유형','제목명','장소명','장소유형','관련장소설명','운영시간','휴식시간','휴무일안내내용','주소','위치위도','위치경도','전화번호','최종수정일자'],
        encoding='utf-8',
        # csv_args={
        #     'encoding': 'utf-8',
        #     'delimiter': ',',
        #     'quotechar': '"',
        #     'on_bad_lines': 'skip'
        # }
    )
    all_docs = loader.load()

    print("파일이 로딩 됐습니다.")
    # chunk_size를 더 크게 설정
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, 
        chunk_overlap=50
        )
    splits = text_splitter.split_documents(all_docs)
    return splits

# 벡터 DB 구성
def create_vector_db_with_google(splits: list):
    """
    분할된 문서 청크를 사용하여 ChromaDB 벡터 DB를 생성합니다.

    Args:
        splits (list): 분할된 문서 청크 리스트.

    Returns:
        Chroma: 생성된 Chroma 벡터 DB.
    """
    print("Creating vector database with Google AI Embeddings...")
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embedding)
    return vectorstore



# 하드디스크 저장
def create_vector_db_with_hf(splits: list, 
                             db_path: str = "./chroma_db",
                             collection_name: str = "documents",
                             ):
    """
    분할된 문서 청크를 사용하여 ChromaDB 벡터 DB를 생성하고 파일로 저장합니다.
    Hugging Face의 한국어 임베딩 모델을 사용합니다.

    Args:
        splits (list): 분할된 문서 청크 리스트.
        db_path (str): 벡터 DB 파일이 저장될 디렉터리 경로.

    Returns:
        Chroma: 생성된 Chroma 벡터 DB.
    """
    print("Creating vector database with Hugging Face Embeddings (Sentence-Transformers)...")
    
    # 'jhgan/ko-sbert-nli' 모델 로드
    model_name = "jhgan/ko-sbert-nli"
    embedding = HuggingFaceEmbeddings(model_name=model_name)
    
    # DB 파일 저장 경로 확인 및 생성
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    
    # persist_directory를 사용하여 DB를 파일로 저장
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=db_path,
        collection_name=collection_name
    )
    
    # DB 저장
    print(f"\nVector DB successfully created and saved at: {db_path}")

    return vectorstore

# Chroma DB 로드 (한국어 SBERT 모델 사용)
def load_vector_db(persist_directory: str = "./chroma_db", 
                   collection_name: str = "documents",
                   model_name: str = "jhgan/ko-sbert-nli"):
    """
    기존 Chroma DB 로드
    
    Args:
        persist_directory: Chroma DB 저장 경로
        collection_name: 컬렉션 이름
        model_name: HuggingFace 임베딩 모델명
    
    Returns:
        Chroma vectorstore 객체
    """
    # 한국어 SBERT 모델 초기화 (저장할 때와 동일한 모델 사용)
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    # Chroma DB 로드
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=collection_name
    )
    print("크로마DB 로딩 완료.")
    
    return vectorstore

# 1. 원하는 JSON 구조를 정의하는 Pydantic 모델
class LocationInfo(BaseModel):
    장소: str = Field(description="영화/드라마 촬영 장소의 이름")
    주소: str = Field(description="영화/드라마 촬영 장소의 주소")
    장면_설명: str = Field(description="해당 장소에서 촬영된 영화/드라마 장면의 상세 설명")
    장소_설명: str = Field(description="촬영 장소 상세 설명")
    위도: float = Field(description="위도")
    경도: float = Field(description="경도")

# vector DB 검색, 검색 형식 json
def get_rag_chain_with_json_output(vectorstore):
    """
    RAG 파이프라인을 구성하고, LLM 답변을 JSON 형식으로 반환합니다.

    Args:
        vectorstore (Chroma): Chroma 벡터 DB.

    Returns:
        RetrievalChain: JSON 출력 파서가 적용된 RAG 체인.
    """
    print("Creating RAG chain with Gemini and JSON output...")
    
    # 2. 검색기 설정
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # 3. LLM 설정
    llm = GoogleGenerativeAI(model="models/gemini-2.5-flash") 
    
    # 4. JSON 출력 파서 초기화
    json_parser = JsonOutputParser(pydantic_object=LocationInfo)
    
    # 5. 프롬프트 템플릿 정의
    prompt = ChatPromptTemplate.from_template("""
    주어진 맥락을 사용하여 질문에 답변하세요.
    사용자가 입력한 드라마 제목에서 촬영장소 2개를 출력해주세요.                                        
    맥락에 없는 내용은 답변하지 마세요.

    {format_instructions}

    맥락:
    {context}

    질문: {input}
    """)
    
    # 프롬프트에 JSON 출력 형식 지시사항을 추가
    prompt = prompt.partial(format_instructions=json_parser.get_format_instructions())
    
    # 6. 체인 구성
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    return retrieval_chain


# RAG 기반 쿼리
def run_rag_query(chain, query: str):

    """
    구성된 RAG 체인을 실행하여 사용자 질문에 대한 답변을 생성합니다.
    """
    print(f"\nSearching for: {query}")
    response = chain.invoke({"input": query})
    
    # RAG의 Context와 Answer를 분리하여 출력
    print("\n--- Retrieved Context (Top 5) ---")
    for doc in response['context']:
        print(f"Source: {doc.metadata.get('source')}")
        print(f"Content: {doc.page_content}\n")

    return response["answer"]


if __name__ == "__main__":
    
    # 1. 데이터 로드 및 분할
    # 1-1 웹 url 문서 로더
    # 여러 URL 리스트
    # urls = [
    #     "https://namu.wiki/w/%EC%8A%AC%EA%B8%B0%EB%A1%9C%EC%9A%B4%20%EC%9D%98%EC%82%AC%EC%83%9D%ED%99%9C",
    #     "https://ko.wikipedia.org/wiki/%EC%8A%AC%EA%B8%B0%EB%A1%9C%EC%9A%B4_%EC%9D%98%EC%82%AC%EC%83%9D%ED%99%9C",
    #     "https://blog.naver.com/everydayhealth/223774177210",
    # ]
    # document_splits = load_url_and_split_documents(urls)


    # 1-2 csv 파일 로더
    # folder_path와 file_name을 결합하여 file_path = './data/KC_MEDIA_VIDO_AREA_DATA_2023.csv'
    folder_path = 'data'
    file_name = 'test_data_small.csv'
    # file_path = os.path.join(folder_path, file_name)
    file_path=f'{folder_path}/{file_name}'
    document_splits = load_csv_and_split_documents(file_path)
    
    
    # 2. 벡터 DB 생성
    vector_db = create_vector_db_with_hf(document_splits)
    

    # vector db 구성 되어있을 경우
    vector_db = load_vector_db()

    # 3. RAG 체인 구성
    # rag_chain = get_rag_chain(vector_db)
    rag_chain = get_rag_chain_with_json_output(vector_db)
    
    # 4. 사용자 쿼리 실행
    # query = "18 어게인"
    # query = "좋은 맛에 취하다"
    query = "슬기로운 의사생활"
    resutl = run_rag_query(rag_chain, query)
    print("--- Generated Answer ---")

    print(resutl)
