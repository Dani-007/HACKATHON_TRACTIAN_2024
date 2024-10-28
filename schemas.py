from pydantic import BaseModel
from enum import Enum

class StatusEnum(str, Enum):
    aberto = "Aberto"
    em_progresso = "Em Progresso"
    resolvido = "Resolvido"

class PrioridadeEnum(str, Enum):
    baixa = "Baixa"
    media = "Média"
    alta = "Alta"

class ChamadoBase(BaseModel):
    titulo: str
    responsavel: str
    status: StatusEnum
    prioridade: PrioridadeEnum

class ChamadoCreate(ChamadoBase):
    pass

class ChamadoResponse(ChamadoBase):
    id: int

    class Config:
        orm_mode = True
