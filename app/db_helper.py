from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, false, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from contextlib import contextmanager
import json
from sqlalchemy import UniqueConstraint, Index, text
import re

# Configuração do banco de dados
DATABASE_URL = 'postgresql://monteiro:V%40l0rant!@10.2.10.49:5432/postgres'
engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


# Gerenciamento de sessão seguro
@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Erro na transação: {e}")
    finally:
        session.close()


# Modelo da Tabela Vaga
class Vaga(Base):
    __tablename__ = 'rh_vagas'
    __table_args__ = (
        Index('idx_vaga_nome_vaga', 'nome_vaga'),
        Index('idx_vaga_data_inicial', 'data_inicial'),
        Index('idx_vaga_data_final', 'data_final'),
        {'schema': 'monteiro'}  # O dicionário com o schema deve vir no final
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), unique=True)
    nome_vaga = Column(String, nullable=False)
    departamento_vaga = Column(String, nullable=False)
    requisitos = Column(String, nullable=False)
    diferencial = Column(String, nullable=True)
    url_link = Column(String, nullable=True)
    imagem_capa = Column(String, nullable=True)
    limit_candidatos = Column(Integer, nullable=True)
    isInternalSelection = Column(Boolean, default=False)
    data_inicial = Column(DateTime, nullable=False)
    data_final = Column(DateTime, nullable=True)
    criado_por = Column(String, nullable=True)
    data_criacao = Column(DateTime, server_default=func.now())
    data_update = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_ativo = Column(Boolean, default=True)
    candidatos = relationship("Candidate", back_populates="vaga")
    
    #Alteração
    salary = Column(String, nullable=False)
    location = Column(String, nullable=False)

#        Index('idx_candidate_email', 'email', unique=True),
# Modelo da Tabela Candidate
class Candidate(Base):
    __tablename__ = 'rh_candidatos'
    __table_args__ = (
        Index('idx_candidate_vaga_id', 'vaga_id'),
        Index('idx_candidate_cpf', 'cpf'),
        UniqueConstraint('cpf', 'vaga_id', name='unique_candidate_vaga'),
        {'schema': 'monteiro'}  # O dicionário com o schema deve ser o último elemento
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), unique=True)
    vaga_id = Column(UUID(as_uuid=True), ForeignKey('monteiro.rh_vagas.id'), nullable=False)
    cpf = Column(String, nullable=False)
    email = Column(String, nullable=False)
    nome_completo = Column(String, nullable=False)
    cep = Column(String, nullable=False)
    bairro = Column(String)
    cidade = Column(String)
    estado = Column(String)
    address = Column(String)
    numero = Column(String)
    complemento = Column(String)
    telefone = Column(String)
    is_disponivel = Column(String)
    is_primeiraexperiencia = Column(Boolean, default=False)
    matricula = Column(String, default=None)
    foto_perfil = Column(String)
    file_cv = Column(String)
    adicionado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_analizado = Column(Boolean, default=False)
    vaga = relationship("Vaga", back_populates="candidatos")
    analises = relationship("Analise", back_populates="candidato")


# Modelo da Tabela Analise
class Analise(Base):
    __tablename__ = 'rh_analise'
    __table_args__ = (
        UniqueConstraint('candidate_id', 'vaga_id', name='unique_candidate_vaga_analise'),
        Index('idx_analise_vaga_id', 'vaga_id'),
        Index('idx_analise_candidate_id', 'candidate_id'),
        {'schema': 'monteiro'}  # O dicionário com o schema deve vir no final
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), unique=True)
    vaga_id = Column(UUID(as_uuid=True), ForeignKey('monteiro.rh_vagas.id'), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('monteiro.rh_candidatos.id'), nullable=False)
    fullName = Column(String, nullable=False)
    cv_critica = Column(String, nullable=False)
    skills = Column(String)
    education = Column(String)
    languages = Column(String)
    score = Column(Float, nullable=False)
    observation = Column(String)
    data_criacao = Column(DateTime, server_default=func.now())
    data_update = Column(DateTime, server_default=func.now(), onupdate=func.now())

    candidato = relationship("Candidate", back_populates="analises")


# Criar as tabelas no banco
Base.metadata.create_all(engine)




def get_cargos():
    with engine.connect() as conn:
        result = conn.execute(text('select distinct novo_cargo as cargo from ruby.cargos_de_para cdp where novo_cargo not in (\'SOCIO ADMINISTRADOR\') order by 1'))
        return [row[0] for row in result]




# Funções de CRUD da Tabela Vaga
def add_vaga(vaga):
    try:
        with session_scope() as session:
            session.add(vaga)
            session.commit()
            print(f'ID da nova vaga: {vaga.id}')
            return vaga.id
    except Exception as e:
        print(f'Erro ao adicionar vaga: {str(e)}')
        return {'error': str(e)}

def update_vaga(vaga_id, **kwargs):
    with session_scope() as session:
        vaga = session.query(Vaga).filter(Vaga.id == vaga_id).first()
        if vaga:
            for key, value in kwargs.items():
                setattr(vaga, key, value)
            session.commit()
        return vaga.__dict__

def get_all_vagas():
    with session_scope() as session:
        vagas = session.query(Vaga).all()
        return json.dumps([vaga.__dict__ for vaga in vagas], default=str)



def get_all_vagas_v2():
    with session_scope() as session:
        vagas = session.query(Vaga).filter(Vaga.is_ativo == True).all()
        vagas_list = []
        for vaga in vagas:
            vagas_list.append({
                'id': vaga.id,
                'title': vaga.nome_vaga.strip().capitalize(),
                'location': 'Manaus - AM',
                'type': 'Seleção Interna' if vaga.isInternalSelection else 'Todos',
                'department': vaga.departamento_vaga.strip().capitalize()
            })
        
        return vagas_list

def get_vaga_v2(vaga_id):
    with session_scope() as session:
        vaga_up = session.query(Vaga).filter(Vaga.id == vaga_id).first()
        if vaga_up:
            return {
                'id': vaga_up.id,
                'title': vaga_up.nome_vaga.strip().capitalize(),
                'location': 'Manaus, AM',
                'type': 'Seleção Interna' if vaga_up.isInternalSelection else 'Todos',
                'department': vaga_up.departamento_vaga.strip().capitalize(),
                'salary': 'R$ 2.500,00',
                'schedule': '17:00 às 23:00',
                'requirements': [req.strip().capitalize() for req in vaga_up.requisitos.split(',')],
                'responsibilities': [req.strip().capitalize() for req in vaga_up.diferencial.split(',')],
                'benefits': [req.strip().capitalize() for req in vaga_up.diferencial.split(',')],
            }

        else:
            return {}



def get_vaga(vaga_id):
    with session_scope() as session:
        vaga_up = session.query(Vaga).filter(Vaga.id == vaga_id).first()
        if vaga_up:
            session.refresh(vaga_up)
            vaga_dict = vaga_up.__dict__.copy()
            del vaga_dict['_sa_instance_state']
            return vaga_dict
        else:
            return {}

def delete_vaga(vaga_id):
    with session_scope() as session:
        vaga = session.query(Vaga).filter(Vaga.id == vaga_id).first()
        if vaga:
            vaga.is_ativo = False
            session.commit()
        return vaga.__dict__

def is_vaga_exists(vaga_id):
    with session_scope() as session:
        vaga = session.query(Vaga).filter(Vaga.id == vaga_id).first()
        return vaga is not None


# Funções de CRUD da Tabela Candidate

def add_candidate(candidate):
    try:
        with session_scope() as session:
            session.add(candidate)
            session.commit()
            retorno ={
                'id': candidate.id,
                'vaga_id': candidate.vaga_id,
                'cpf': candidate.cpf,
                'nome_completo': candidate.nome_completo,
                'email': candidate.email,
                'cep': candidate.cep,
                'bairro': candidate.bairro,
                'cidade': candidate.cidade,
                'estado': candidate.estado,
                'address': candidate.address,
                'numero': candidate.numero,
                'complemento': candidate.complemento,
                'telefone': candidate.telefone,
                'is_primeiraexperiencia': candidate.is_primeiraexperiencia,
                'is_disponivel': candidate.is_disponivel,
                'foto_perfil': candidate.foto_perfil,
                'file_cv': candidate.file_cv,
                'adicionado_em': candidate.adicionado_em,
                'atualizado_em': candidate.atualizado_em,
                'is_analizado': candidate.is_analizado
            }
            return retorno
    except Exception as e:
        return {'error': str(e)}

def delete_candidate(candidate_id, vaga_id):
    with session_scope() as session:
        candidate = session.query(Candidate).filter(Candidate.id == candidate_id, Candidate.vaga_id == vaga_id).first()
        if candidate:
            session.delete(candidate)
            session.commit()
        return candidate.__dict__

def update_candidate(candidate_id, vaga_id, **kwargs):
    with session_scope() as session:
        candidate = session.query(Candidate).filter(Candidate.id == candidate_id, Candidate.vaga_id == vaga_id).first()
        if candidate:
            for key, value in kwargs.items():
                setattr(candidate, key, value)
            session.commit()
        return candidate.__dict__

def get_all_candidates(vaga_id):
    with session_scope() as session:
        candidates = session.query(Candidate).filter(Candidate.vaga_id == vaga_id).all()

        candidatos_analises = []
        for candidate in candidates:
            analise = session.query(Analise).filter(
                Analise.candidate_id == candidate.id, Analise.vaga_id == vaga_id
            ).first()

            candidatos_analises.append({
                'candidate': {
                    'id': str(candidate.id),
                    'cpf': candidate.cpf,
                    'nome_completo': candidate.nome_completo,
                    'email': candidate.email,
                    'telefone': candidate.telefone,
                    'is_primeiraexperiencia': candidate.is_primeiraexperiencia,
                    'is_disponivel': candidate.is_disponivel,
                    'file_perfil': candidate.foto_perfil if candidate.foto_perfil else '',
                    'file_cv': candidate.file_cv,
                    'is_analizado': candidate.is_analizado,
                },
                'analise': {
                    'score': analise.score if analise else '',
                    'cv_resumo': analise.cv_critica if analise else '',
                    'skills': analise.skills if analise else '',
                    'education': analise.education if analise else '',
                    'status': analise.observation if analise else '',
                }
            })

        return candidatos_analises






def get_all_talentos(page: int = 1, limit: int = 30):
    with session_scope() as session:
        offset = (page - 1) * limit
        candidates = session.query(Candidate).order_by(Candidate.adicionado_em.desc()).offset(offset).limit(limit).all()

        candidatos_analises = []
        for candidate in candidates:
            analise = session.query(Analise).filter(
                Analise.candidate_id == candidate.id, Analise.vaga_id == candidate.vaga_id
            ).first()

            candidatos_analises.append({
                'candidate': {
                    'id': str(candidate.id),
                    'cpf': candidate.cpf,
                    'nome_completo': candidate.nome_completo,
                    'email': candidate.email,
                    'telefone': candidate.telefone,
                    'is_primeiraexperiencia': candidate.is_primeiraexperiencia,
                    'is_disponivel': candidate.is_disponivel,
                    'file_perfil': candidate.foto_perfil if candidate.foto_perfil else '',
                    'file_cv': candidate.file_cv,
                    'is_analizado': candidate.is_analizado,
                },
                'analise': {
                    'score': analise.score if analise else '',
                    'cv_resumo': analise.cv_critica if analise else '',
                    'skills': analise.skills if analise else '',
                    'education': analise.education if analise else '',
                    'status': analise.observation if analise else '',
                }
            })

        return candidatos_analises







def get_candidate(candidate_id):
    with session_scope() as session:
        candidate = session.query(Candidate).filter(Candidate.id == candidate_id).first()
        analise = session.query(Analise).filter(Analise.candidate_id == candidate_id).first()

        if candidate:
            analise_dict = analise.__dict__ if analise else {}
            analise_dict['status'] = analise_dict.pop('observation', '')
            return {
                'candidate': candidate.__dict__,
                'analise': analise_dict
            }
        return None


def is_candidate_exists(cpf, vaga_id):
    with session_scope() as session:
        candidate = session.query(Candidate).filter(Candidate.cpf == cpf, Candidate.vaga_id == vaga_id).first()
        return candidate is not None

def get_catidato_sem_analise():
    with session_scope() as session:
        candidatos = []
        for candidate in session.query(Candidate).filter(Candidate.is_analizado == False).all():
            vaga = session.query(Vaga).filter(Vaga.id == candidate.vaga_id).first()
            retorno ={
                'id': str(candidate.id),
                'vaga_id': str(candidate.vaga_id),
                'cpf': candidate.cpf,
                'nome_completo': candidate.nome_completo,
                'email': candidate.email,
                'telefone': candidate.telefone,
                'is_primeiraexperiencia': candidate.is_primeiraexperiencia,
                'is_disponivel': candidate.is_disponivel,
                'file_cv': candidate.file_cv,
                'is_analizado': candidate.is_analizado,
                'vaga': {
                    'id': str(vaga.id),
                    'nome_vaga': vaga.nome_vaga,
                    'departamento_vaga' :vaga.departamento_vaga,
                    'requisitos' : vaga.requisitos,
                    'diferencial' : vaga.diferencial,
                    'url_link' : vaga.url_link,
                    'imagem_capa' : vaga.imagem_capa,
                    'limit_candidatos' : vaga.limit_candidatos,
                    'isInternalSelection' : vaga.isInternalSelection,
                    'data_inicial' : vaga.data_inicial,
                    'data_final' : vaga.data_final,
                    'criado_por' : vaga.criado_por
                }
            }

            candidatos.append(retorno)

        return candidatos

def add_analise(analise):
    with session_scope() as session:
        session.add(analise)
        session.commit()
        # Atualizar o candidato que foi analisado
        candidate = session.query(Candidate).filter(Candidate.id == analise.candidate_id, Candidate.vaga_id == analise.vaga_id).first()
        candidate.is_analizado = True
        session.commit()

        return analise







def is_funcionario_ruby_valido(cpf):

    cpf = re.sub('[^0-9]', '', cpf)
    if len(cpf) != 11:
        return False

    with session_scope() as session:
        return session.execute(
            text("""
            select
                exists (
                    select 1
                    from ruby.funcionarios
                    where numerocpf = :cpf and idafastamento <> 7
                )
            """),
            {"cpf": cpf}
        ).scalar()




def update_analise(candidate_id, vaga_id, status):
    with session_scope() as session:
        analise = session.query(Analise).filter(Analise.candidate_id == candidate_id, Analise.vaga_id == vaga_id).first()
        if analise:
            analise.observation = status
            session.commit()
        return analise






if __name__ == '__main__':

    vg= Vaga(
        nome_vaga='Desenvolvedor(a) Full Stack',
        departamento_vaga='Tecnologia',
        requisitos='Experiência com React, Node.js e Python',
        diferencial='Habilidades em desenvolvimento de software',
        url_link='https://trabalheconosco.com.br/vaga/123',
        imagem_capa='capa.jpg',
        limit_candidatos=10,
        data_inicial='2023-01-01',
        data_final='2023-12-31',
        criado_por='admin'
    )
    #nova_vaga = add_vaga(vg)

    vaga_id = 'f055ce70-a53d-4eb1-91a0-603374f75ef0'
    #out = get_catidato_sem_analise(vaga_id)

    #candidatos = get_all_candidates(vaga_id)

    cpf = '74339524204'
    matricula = '6541'

    is_valid = is_funcionario_ruby_valido(cpf, matricula)

    print(is_valid)