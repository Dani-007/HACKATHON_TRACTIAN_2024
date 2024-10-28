from fastapi import FastAPI, Request, Depends, Form, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import requests

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="pages")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependência de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota para a página inicial
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota para listar chamados
@app.get("/chamados/", response_class=HTMLResponse)
def listar_chamados(request: Request, db: Session = Depends(get_db)):
    chamados = db.query(models.Chamado).all()
    return templates.TemplateResponse("chamados_list.html", {"request": request, "chamados": chamados})

# Rota para criação de chamados
@app.get("/chamados/create/", response_class=HTMLResponse)
def novo_chamado(request: Request, db: Session = Depends(get_db)):
    ativos = db.query(models.Ativo).all()
    return templates.TemplateResponse("chamados_create.html", {"request": request, 'ativos': ativos})

@app.post("/chamados/")
async def create_chamado_post(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    titulo = form_data.get("titulo")
    responsavel = form_data.get("responsavel")
    status = form_data.get("status")
    prioridade = form_data.get("prioridade")
    descricao = form_data.get("descricao")  # Nova descrição
    ativo_id = form_data.get("ativo_id")  # O ativo selecionado
    novo_chamado = models.Chamado(titulo=titulo, responsavel=responsavel, status=status, prioridade=prioridade, descricao=descricao, ativo_id=ativo_id)
    db.add(novo_chamado)
    db.commit()
    return RedirectResponse(url="/chamados/", status_code=303)


# Rota para editar chamados
@app.get("/chamados/{chamado_id}/edit", response_class=HTMLResponse)
def editar_chamado(request: Request, chamado_id: int, db: Session = Depends(get_db)):
    ativos = db.query(models.Ativo).all()
    chamado = db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()
    if chamado is None:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return templates.TemplateResponse("chamados_edit.html", {"request": request, "chamado": chamado, "ativos": ativos})

@app.post("/chamados/{chamado_id}")
async def edit_chamado_post(chamado_id: int, request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    titulo = form_data.get("titulo")
    responsavel = form_data.get("responsavel")
    status = form_data.get("status")
    prioridade = form_data.get("prioridade")
    descricao = form_data.get("descricao")  # Capturando a nova descrição
    ativo_id = form_data.get("ativo_id")  # O ativo selecionado

    chamado = db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()
    
    if chamado:
        chamado.titulo = titulo
        chamado.responsavel = responsavel
        chamado.status = status
        chamado.prioridade = prioridade
        chamado.descricao = descricao  # Atualizando a descrição
        chamado.ativo_id = ativo_id
        
        db.commit()

    return RedirectResponse(url="/chamados/", status_code=303)

# Rota para deletar chamados
@app.get("/chamados/{chamado_id}/delete")
def deletar_chamado(chamado_id: int, db: Session = Depends(get_db)):
    chamado = db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()
    if chamado is None:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    db.delete(chamado)
    db.commit()
    return RedirectResponse(url="/chamados/", status_code=303)


# Rotas para Ativos
@app.get("/ativos/", response_class=HTMLResponse)
def listar_ativos(request: Request, db: Session = Depends(get_db)):
    ativos = db.query(models.Ativo).all()
    return templates.TemplateResponse("ativos_list.html", {"request": request, "ativos": ativos})

@app.get("/ativos/create/", response_class=HTMLResponse)
def novo_ativo(request: Request):
    return templates.TemplateResponse("ativos_create.html", {"request": request})

@app.post("/ativos/")
async def criar_ativo(
    nome: str = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db)
):
    ativo = models.Ativo(nome=nome, descricao=descricao)
    db.add(ativo)
    db.commit()
    return RedirectResponse(url="/ativos/", status_code=303)

@app.get("/ativos/{ativo_id}/edit", response_class=HTMLResponse)
def editar_ativo(request: Request, ativo_id: int, db: Session = Depends(get_db)):
    ativo = db.query(models.Ativo).filter(models.Ativo.id == ativo_id).first()
    if ativo is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return templates.TemplateResponse("ativos_edit.html", {"request": request, "ativo": ativo})

@app.post("/ativos/{ativo_id}")
async def atualizar_ativo(
    ativo_id: int,
    nome: str = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db)
):
    ativo = db.query(models.Ativo).filter(models.Ativo.id == ativo_id).first()
    if ativo is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    ativo.nome = nome
    ativo.descricao = descricao

    db.commit()
    return RedirectResponse(url="/ativos/", status_code=303)

@app.get("/ativos/{ativo_id}/delete")
def deletar_ativo(ativo_id: int, db: Session = Depends(get_db)):
    ativo = db.query(models.Ativo).filter(models.Ativo.id == ativo_id).first()
    if ativo is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    db.delete(ativo)
    db.commit()
    return RedirectResponse(url="/ativos/", status_code=303)

# Rota para criar uma nova ferramenta

@app.get("/ferramentas/create/", response_class=HTMLResponse)
async def create_ferramenta_form(request: Request):
    return templates.TemplateResponse("ferramentas_create.html", {"request": request})


# Rota para processar o formulário e criar uma nova ferramenta
@app.post("/ferramentas/")
async def create_ferramenta(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    nome = form_data.get("nome")
    categoria = form_data.get("categoria")
    descricao = form_data.get("descricao")
    codigo_sap = form_data.get("codigo_sap")
    estado = form_data.get("estado")
    descricao = form_data.get("descricao")  # Nova descrição
    ferramenta = models.Ferramenta(nome=nome, categoria=categoria, descricao=descricao, codigo_sap=codigo_sap, estado=estado)
    db.add(ferramenta)
    db.commit()
    db.refresh(ferramenta)
    return RedirectResponse(url="/ferramentas/", status_code=303)

# Rota para listar todas as ferramentas
@app.get("/ferramentas/", response_class=HTMLResponse)
async def read_ferramentas(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    ferramentas = db.query(models.Ferramenta).offset(skip).limit(limit).all()
    return templates.TemplateResponse("ferramentas_list.html", {"request": request, "ferramentas": ferramentas})

# Rota para editar uma ferramenta
@app.get("/ferramentas/{ferramenta_id}/edit", response_class=HTMLResponse)
async def edit_ferramenta(request: Request, ferramenta_id: int, db: Session = Depends(get_db)):
    ferramenta = db.query(models.Ferramenta).filter(models.Ferramenta.id == ferramenta_id).first()
    if ferramenta is None:
        raise HTTPException(status_code=404, detail="Ferramenta não encontrada")
    return templates.TemplateResponse("ferramentas_edit.html", {"request": request, "ferramenta": ferramenta})

@app.post("/ferramentas/{ferramenta_id}/")
async def update_ferramenta(request: Request, ferramenta_id: int, db: Session = Depends(get_db)):
    form_data = await request.form()
    nome = form_data.get("nome")
    categoria = form_data.get("categoria")
    descricao = form_data.get("descricao")
    codigo_sap = form_data.get("codigo_sap")
    estado = form_data.get("estado")

    ferramenta = db.query(models.Ferramenta).filter(models.Ferramenta.id == ferramenta_id).first()

    if ferramenta is None:
        raise HTTPException(status_code=404, detail="Ferramenta não encontrada")

    if ferramenta:
        ferramenta.nome = nome
        ferramenta.categoria = categoria
        ferramenta.descricao  = descricao
        ferramenta.codigo_sap  = codigo_sap 
        ferramenta.estado  = estado
    
    db.commit()

    return RedirectResponse(url="/ferramentas/", status_code=303)

# Rota para deletar uma ferramenta
@app.get("/ferramentas/{ferramenta_id}/delete")
def delete_ferramenta(ferramenta_id: int, db: Session = Depends(get_db)):
    ferramenta = db.query(models.Ferramenta).filter(models.Ferramenta.id == ferramenta_id).first()
    if ferramenta is None:
        raise HTTPException(status_code=404, detail="Ferramenta não encontrada")
    
    db.delete(ferramenta)
    db.commit()
    return RedirectResponse(url="/ferramentas/", status_code=303)


@app.get("/audio-chamado/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("audio_chamado.html", {"request": request})


# Função para chamar o ChatGPT para extrair informações de chamado do texto transcrito
def get_chamado_details_from_gpt(transcription: str):
    gpt_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OpenAI}",
        "Content-Type": "application/json"
    }
    prompt = (
        "Analise o texto transcrito abaixo e extraia informações para criar um chamado:\n\n"
        f"{transcription}\n\n"
        "Responda com o título, responsável, status (Aberto, Em Progresso, Resolvido), prioridade (Baixa, Media, Alta) e descrição do chamado."
    )
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    response = requests.post(gpt_url, headers=headers, json=data)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Erro ao obter detalhes do chamado do GPT")

    response_data = response.json()
    result = response_data["choices"][0]["message"]["content"]
    
    # Aqui você precisa tratar o `result` para extrair os valores exatos para cada campo
    # Exemplo básico (pode variar conforme o formato da resposta do GPT):
    details = {}
    for line in result.splitlines():
        if "Título:" in line:
            details["titulo"] = line.split("Título:")[1].strip()
        elif "Responsável:" in line:
            details["responsavel"] = line.split("Responsável:")[1].strip()
        elif "Status:" in line:
            details["status"] = line.split("Status:")[1].strip()
        elif "Prioridade:" in line:
            details["prioridade"] = line.split("Prioridade:")[1].strip()
        elif "Descrição:" in line:
            details["descricao"] = line.split("Descrição:")[1].strip()
    
    return details


# Endpoint para transcrição e criação do chamado
@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verifica o tipo do arquivo
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Arquivo não é do tipo áudio.")
    
    # Envia o arquivo para a API Whisper da OpenAI
    whisper_url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {"file": (audio_file.filename, await audio_file.read(), audio_file.content_type)}
    data = {"model": "whisper-1"}
    
    response = requests.post(whisper_url, headers=headers, files=files, data=data)
    
    # Verifica se a resposta foi bem-sucedida
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    transcription = response.json().get("text")

    # Obtém os detalhes do chamado usando o ChatGPT
    chamado_details = get_chamado_details_from_gpt(transcription)

    # Cria o chamado no banco de dados
    novo_chamado = models.Chamado(
        titulo=chamado_details["titulo"],
        responsavel=chamado_details["responsavel"],
        status=chamado_details["status"],
        prioridade=chamado_details["prioridade"],
        descricao=chamado_details["descricao"]
    )
    
    db.add(novo_chamado)
    db.commit()


    chamado_id = novo_chamado.id

    return {"message": "Chamado criado com sucesso", "chamado": chamado_details, "id": chamado_id}