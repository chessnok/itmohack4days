from langchain_core.tools import create_retriever_tool
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_postgres import PGEngine
from langchain_postgres.v2.vectorstores import PGVectorStore

from app.core.config import settings
from app.models.file import FileObject, FileChunk
from app.services.embeddings import embedding_pipeline

meta = list(set([k for k in FileObject.model_fields.keys() if k not in ["id", "embedding", "content"]] +[k for k in FileChunk.model_fields.keys() if k not in ["id", "embedding","content"]]))
vectorstore2 = PGVectorStore.create_sync(
    engine=PGEngine.from_connection_string( url=f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"),
    embedding_service=embedding_pipeline.emb,
    embedding_column="embedding",
    id_column="id",
    metadata_columns=meta,
    table_name="v_file_chunks"

)
retriever: VectorStoreRetriever = vectorstore2.as_retriever()
file_search_tool = create_retriever_tool(
    retriever,
    name="file_search",
    description=(
        "Ищет релевантную информацию в пользовательских файлах (PDF, DOCX, изображения и др.), "
        "используя эмбеддинги и pgvector. "
        "Полезно, если нужно ответить на вопрос, используя содержимое загруженных документов."
    ),
)
