from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base

class Ativo(Base):
    __tablename__ = "ativos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), index=True)
    descricao = Column(String(10000), nullable=True)

    # Relacionamento com Chamados
    chamados = relationship("Chamado", back_populates="ativo")



class Chamado(Base):
    __tablename__ = 'chamados'

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    responsavel = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    prioridade = Column(String(50), nullable=False)
    descricao = Column(String(500), nullable=True)  # Nova propriedade
    ativo_id = Column(Integer, ForeignKey('ativos.id'))

    ativo = relationship("Ativo")

class Ferramenta(Base):
    __tablename__ = 'ferramentas'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)  # Adicionando o campo nome
    categoria = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=False)
    codigo_sap = Column(String(255), nullable=False)
    estado = Column(Enum("Disponível", "Em Uso"), default="Disponível")

