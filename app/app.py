from fastapi import FastAPI, Form, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel
from db_helper import Analise, add_vaga, Vaga, add_candidate, is_funcionario_ruby_valido, Candidate, get_vaga, update_vaga, update_candidate, is_candidate_exists, delete_vaga, get_all_vagas, get_all_candidates, add_analise, get_catidato_sem_analise, get_cargos, get_all_talentos, update_analise, get_all_vagas_v2, get_vaga_v2     
import uvicorn
import os, json
from datetime import datetime
from email_helper import send_mail_aprovado, send_mail_recusado, send_mail_entrevista
from fastapi.responses import JSONResponse


app = FastAPI()

# Configuração do CORS para permitir todas as origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

@app.post("/vagas")
async def add_vagass(
    nome_vaga: str = Form(...),
    departamento_vaga: str = Form(...),
    requisitos: str = Form(...),
    diferencial: str = Form(default=""),
    url_link: str = Form(default=""),
    imagem_capa: UploadFile = File(...),
    limit_candidatos: int = Form(0),
    isInternalSelection: bool = Form(False),
    data_inicial: datetime = Form(...),
    data_final: datetime = Form(None),
    criado_por: str = Form(default=""),
    #Alteração
    salary: str = Form (...),
    location: str = Form(...)
):
    file_content = await imagem_capa.read()

    vaga = Vaga(
        nome_vaga=nome_vaga,
        departamento_vaga=departamento_vaga,
        requisitos=requisitos,
        diferencial=diferencial,
        url_link=url_link,
        imagem_capa='',
        limit_candidatos=limit_candidatos,
        isInternalSelection=isInternalSelection,
        data_inicial=data_inicial,
        data_final=data_final,
        criado_por=criado_por,
        #Alteração
        salary=salary,
        location=location
    )

    # Salvando a vaga no banco de dados
    nova_vaga = add_vaga(vaga)

    nome = str(nova_vaga)
    # Definindo o nome e o caminho da imagem
    extensao = imagem_capa.filename.split('.')[-1]
    filename = f"{nome}.{extensao}"
    file_path = f"uploads/vagas/{filename}"

    # Salvando a imagem no diretório especificado
    with open(file_path, "wb") as f:
        f.write(file_content)

    update_vaga(nova_vaga, imagem_capa=f'/vagas/files/{filename}')

    return nova_vaga

@app.put("/vagas/{vaga_id}")
async def update_vagas(
    vaga_id: str,
    nome_vaga: str = Form(...),
    departamento_vaga: str = Form(...),
    requisitos: str = Form(...),
    diferencial: str = Form(""),
    url_link: str = Form(""),
    imagem_capa: UploadFile = File(None),
    limit_candidatos: int = Form(0),
    isInternalSelection: bool = Form(False),
    data_inicial: datetime = Form(...),
    data_final: datetime = Form(None),
    criado_por: str = Form(""),
    #Alteração
    salary: str = Form (...),
    location: str = Form(...)
):
    # Preparar os campos recebidos em um dicionário
    kwargs = {
        "nome_vaga": nome_vaga,
        "departamento_vaga": departamento_vaga,
        "requisitos": requisitos,
        "diferencial": diferencial,
        "url_link": url_link,
        "limit_candidatos": limit_candidatos,
        "isInternalSelection": isInternalSelection,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "criado_por": criado_por,
        #Alteração
        "salary":salary,
        "location":location
    }

    # Verificar se a imagem foi enviada
    try:
        file_content = await imagem_capa.read()
        nome = str(vaga_id)
        extensao = imagem_capa.filename.split('.')[-1]
        filename = f"{nome}.{extensao}"
        file_path = f"uploads/vagas/{filename}"

        # Garantir que o diretório exista
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Salvar o arquivo
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Adicionar o caminho da imagem aos dados de atualização
        kwargs['imagem_capa'] = f'/vagas/files/{filename}'

    except Exception as e:
        return {"error": f"Falha ao salvar o arquivo: {str(e)}"}

    # Remover campos que não foram enviados
    update_data = {key: value for key, value in kwargs.items() if value is not None}

    # Atualizar a vaga com os dados filtrados
    try:
        resultado = update_vaga(vaga_id, **update_data)
        return {"message": "Vaga atualizada com sucesso", "data": resultado}
    except Exception as e:
        return {"error": f"Erro ao atualizar vaga: {str(e)}"}



@app.delete("/vagas/{vaga_id}")
async def delete_vagas(vaga_id: str):
    return delete_vaga(vaga_id)

@app.get("/vagas")
async def get_all_vagass():
    return json.loads(get_all_vagas())
    
    


@app.get("/v2/vagas")
async def get_all_vagass():
    return get_all_vagas_v2()

@app.get("/v2/vaga/{vaga_id}")
async def get_vaga_v2s(vaga_id: str):
    return get_vaga_v2(vaga_id)



@app.get("/vagas/files/{imagem_nome}")
async def get_image(imagem_nome: str):
    file_path = f"uploads/vagas/{imagem_nome}"
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            image = f.read()
        return Response(content=image, media_type=f"image/{imagem_nome.split('.')[-1]}")
    else:
        return JSONResponse({"error": "arquivo não encontrado"}, status_code=404)




@app.post("/candidatos")
async def upload_curriculos(
    vaga_id: str = Form(...),
    cpf: str = Form(...),
    matricula: str = Form(None),
    nome_completo: str = Form(...),
    email: str = Form(...),
    cep: str = Form(...),
    bairro: str = Form(default=""),
    cidade: str = Form(default=""),
    estado: str = Form(default=""),
    address: str = Form(default=""),
    numero: str = Form(default=""),
    complemento: str = Form(default=""),
    telefone: str = Form(default=""),
    is_primeiraexperiencia: bool = Form(False),

    is_disponivel: str = Form(...),
    foto_perfil: UploadFile = File(None),
    file: UploadFile = File(...),
):
    if is_candidate_exists(cpf, vaga_id):
        return JSONResponse({"error": "candidato já existe"}, status_code=400)

    get_vagas = get_vaga(vaga_id)

    if get_vagas["isInternalSelection"]:
            if not is_funcionario_ruby_valido(cpf):
                return JSONResponse({"error": "o candidato não é um funcionário válido"}, status_code=400)



    """Recebe um formulário com os dados do candidato e um arquivo de currículo."""
    file_content = await file.read()
    file_content_foto_perfil = await foto_perfil.read()
    filename = f"uploads/cv/{vaga_id}_{cpf}.{file.filename.split('.')[-1]}"
    filename_foto_perfil = f"uploads/perfil/{vaga_id}_{cpf}.{foto_perfil.filename.split('.')[-1]}"

    candidate = Candidate(
        vaga_id=vaga_id,
        cpf=cpf,
        nome_completo=nome_completo,
        email=email,
        cep=cep,
        bairro=bairro,
        cidade=cidade,
        estado=estado,
        address=address,
        numero=numero,
        complemento=complemento,
        telefone=telefone,
        is_primeiraexperiencia=is_primeiraexperiencia,
        is_disponivel=is_disponivel,
        foto_perfil=filename_foto_perfil,
        file_cv=filename
    )

    novo_candidate = add_candidate(candidate)

    # Salvar o currículonao
    with open(f"{filename}", "wb") as f:
        f.write(file_content)
    
    # Salvar o perfil
    with open(f"{filename_foto_perfil}", "wb") as f:
        f.write(file_content_foto_perfil)

    return novo_candidate


@app.get("/candidatos/{vaga_id}")
async def get_candidates(vaga_id: str):
    return get_all_candidates(vaga_id)



@app.put("/candidato/{vaga_id}/{candidate_id}")
async def update_candidates(candidate_id: str, vaga_id: str, **kwargs):
    return update_candidate(candidate_id, vaga_id, **kwargs)

@app.get("/candidato/perfil/{image_name}")
async def get_image(image_name: str):
    file_path = f"uploads/perfil/{image_name}"
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            image = f.read()
        return Response(content=image, media_type=f"image/{image_name.split('.')[-1]}")
    else:
        return JSONResponse({"error": "arquivo não encontrado"}, status_code=404)


@app.get("/candidato/cv/uploads/cv/{image_name}")
async def get_image(image_name: str):
    file_path = f"uploads/cv/{image_name}"
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            image = f.read()
        return Response(content=image, media_type=f"application/pdf")
    else:
        return JSONResponse({"error": "arquivo não encontrado"}, status_code=404)

@app.post("/agent_ai/analise", response_model=None, include_in_schema=False)
async def upload_analise(analise: dict):
    """Recebe um json com os dados da análise."""
    if not analise:
        raise ValueError("Json vazio")
    analise = Analise(**analise)
    return add_analise(analise)


@app.get("/agent_ai/analise/{vaga_id}/", include_in_schema=False)
async def get_analises(vaga_id: str):
    return get_catidato_sem_analise(vaga_id)



@app.get("/cargos")
async def get_ruby_cargoa():
    return get_cargos()



@app.get("/talentos/all/{page}/{limit}")
async def get_talentoss(page: int = 1, limit: int = 30):
    return get_all_talentos(page, limit)



@app.get("/agent_ai/analise", response_model=None, include_in_schema=False)
async def get_analises():
    return get_catidato_sem_analise()


class EmailAprovado(BaseModel):
    candidato_id: str
    vaga_id: str
    para: str
    nome: str
    vaga: str
    loja: str
    horario: str
    escala: str
    modalidade: str
    data_exame: str


@app.post("/email/aprovado", response_model=None)
async def send_mail_aprovados(data: EmailAprovado):
    """Recebe um json com os dados do candidato aprovado e envia um e-mail de aprova o com as informa es da vaga e do exame."""
    if not data.para:
        raise ValueError("para vazio")
    if not data.nome:
        raise ValueError("nome vazio")
    if not data.vaga:
        raise ValueError("vaga vazio")
    if not data.loja:
        raise ValueError("loja vazio")
    if not data.horario:
        raise ValueError("hor rio vazio")
    if not data.escala:
        raise ValueError("escala vazio")
    if not data.modalidade:
        raise ValueError("modalidade vazio")
    if not data.data_exame:
        raise ValueError("data_exame vazio")


    update_analise(data.candidato_id, data.vaga_id, "aprovado")
    
    return send_mail_aprovado(data.para, data.nome, data.vaga, data.loja, data.horario, data.escala, data.modalidade, data.data_exame)




class EmailRecusado(BaseModel):
    candidato_id: str
    vaga_id: str
    para: str
    nome: str
    vaga: str


@app.post("/email/recusado", response_model=None)
async def send_mail_recusados(data: EmailRecusado):
    """Envia um e-mail informando que o candidato foi reprovado para a vaga.
    
    ex: {
            "para":  "william.monteiro@grupotapajos.com.br",
            "nome": "william Monteiro",
            "vaga": "testador"
        }
    """
    if not data:
        raise ValueError("Json vazio")
    para = data.para
    nome = data.nome
    vaga = data.vaga
    update_analise(data.candidato_id, data.vaga_id, "recusado")
    sender = send_mail_recusado(para, nome, vaga)

    return sender


class EmailEntrevista(BaseModel):
    candidato_id: str
    vaga_id: str
    para: str
    nome: str
    vaga: str
    dia_hora_entrevista: str
    escala: str
    salario: str


@app.post("/email/entrevista", response_model=None)
async def send_mail_entrevistas(data: EmailEntrevista):
    """Envia um e-mail informando que o candidato foi agendado para entrevista para a vaga."""
    if not data:
        raise ValueError("Json vazio")
    para = data.para
    nome = data.nome
    vaga = data.vaga
    dia_hora_entevista = data.dia_hora_entrevista
    escala = data.escala
    salario = data.salario

    update_analise(data.candidato_id, data.vaga_id, "entrevista")
    sender = send_mail_entrevista(
        para=para,
        nome=nome,
        vaga=vaga,
        dia_hora_entevista=dia_hora_entevista,
        escala=escala,
        salario=salario,
    )

    return sender


class EmailEliminado(BaseModel):
    candidato_id: str
    vaga_id: str


@app.post("/email/eliminado", response_model=None)
async def send_mail_eliminados(data: EmailEliminado):
    """Informando que o candidato eliminado não aparecendo no banco de talentos"""
    if not data:
        raise ValueError("Json vazio")

    update_analise(data.candidato_id, data.vaga_id, "eliminado")
    return JSONResponse(content={"message": "Candidato eliminado"}, status_code=200)



if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

