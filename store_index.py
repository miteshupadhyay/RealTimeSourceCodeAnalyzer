from dotenv import load_dotenv
from src.helper import load_repository_as_documents, load_embeddings_model, repository_clone, text_splitter
from langchain.vectorstores import Chroma
import os

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

#url = "https://github.com/miteshupadhyay/Doc_RAG_Search"

#repository_clone(url)


documents = load_repository_as_documents("repo/")
text_chunks = text_splitter(documents)
embeddings = load_embeddings_model()


# Storing vector in ChromaDB
vectordb = Chroma.from_documents(text_chunks, embedding=embeddings, persist_directory="./db")
vectordb.persist()