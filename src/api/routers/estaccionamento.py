from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models import Estacionamento, RegistroEstacionamento, User

Session = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter(prefix="/estacionamento", tags=["estacionamento"])


@router.post(
    "/entrar/{user_id}",
    response_model=Estacionamento  
)
async def registrar_entrada(
    user_id: int,
    session: Session,
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado"
        )

    ultimo_registro_stmt = (
        select(RegistroEstacionamento)
        .where(RegistroEstacionamento.user_id == user_id)
        .order_by(RegistroEstacionamento.horario.desc())
        .limit(1)
    )

    ultimo_registro = await session.scalar(ultimo_registro_stmt)

    if ultimo_registro and ultimo_registro.entrou:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Usuário já está estacionado",
        )

    latest_horario_sq = (
        select(
            RegistroEstacionamento.vaga_id,
            func.max(RegistroEstacionamento.horario).label("max_horario"),
        )
        .group_by(RegistroEstacionamento.vaga_id)
        .subquery("latest_horario_sq")
    )
    occupied_vagas_ids_stmt = (
        select(RegistroEstacionamento.vaga_id)
        .join(
            latest_horario_sq,
            (RegistroEstacionamento.vaga_id == latest_horario_sq.c.vaga_id)
            & (RegistroEstacionamento.horario == latest_horario_sq.c.max_horario),
        )
        .where(RegistroEstacionamento.entrou == True)
    )

    available_vaga_stmt = (
        select(Estacionamento)
        .where(
            Estacionamento.id.notin_(occupied_vagas_ids_stmt),
            Estacionamento.tipo_vaga == user.tipo_do_veiculo,
        )
        .limit(1) 
    )
    
    vaga_disponivel = await session.scalar(available_vaga_stmt)

    if not vaga_disponivel:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Nenhuma vaga disponível encontrada para o tipo: {user.tipo_do_veiculo}",
        )

    # 5. Se achou a vaga, REGISTRAR A ENTRADA
    novo_registro = RegistroEstacionamento(
        user_id=user.id,
        vaga_id=vaga_disponivel.id,
        entrou=True  # Marca como ENTRADA
    )
    session.add(novo_registro)
    await session.commit()
    # Não precisamos dar refresh() pois estamos retornando a 'vaga_disponivel'

    # Retorna a vaga que foi ocupada
    return vaga_disponivel


# --- NOVO ENDPOINT DE SAÍDA ---
@router.post(
    "/sair/{user_id}",
    response_model=RegistroEstacionamento  # Retorna o registro de saída
)
async def registrar_saida(
    user_id: int,
    session: Session,
):
    # 1. Buscar o ÚLTIMO registro do usuário para saber de qual vaga ele sai
    ultimo_registro_stmt = (
        select(RegistroEstacionamento)
        .where(RegistroEstacionamento.user_id == user_id)
        .order_by(RegistroEstacionamento.horario.desc())
        .limit(1)
    )
    ultimo_registro = await session.scalar(ultimo_registro_stmt)

    # 2. Validar se ele está realmente estacionado
    if not ultimo_registro or not ultimo_registro.entrou:
        # Se não tem registro ou o último foi de SAÍDA (False)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Usuário não está estacionado",
        )

    # 3. Criar o novo registro de SAÍDA
    # Ele sai da mesma vaga (ultimo_registro.vaga_id)
    novo_registro_saida = RegistroEstacionamento(
        user_id=user_id,
        vaga_id=ultimo_registro.vaga_id,  # Vaga que ele estava
        entrou=False  # Marca como SAÍDA
    )

    session.add(novo_registro_saida)
    await session.commit()
    
    # Damos refresh para pegar o ID e o 'horario' gerados pelo banco
    await session.refresh(novo_registro_saida) 

    return novo_registro_saida