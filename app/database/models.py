from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.models.document import DocumentStatusEnum
from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, nullable=False)
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.ADDED, nullable=False)
    chunks = relationship("ChunkEmbedding", back_populates="document")


class ChunkEmbedding(Base):
    __tablename__ = "chunk_embeddings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    text = Column(Text, nullable=False)
    vector = Column(Vector(), nullable=False)
    document = relationship("Document", back_populates="chunks")
