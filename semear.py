# Script de inserção de dados baseado no modelo fornecido e nas regras da imagem
# Este script utiliza SQLAlchemy assíncrono e a configuração real do .env

import asyncio
from datetime import datetime, timedelta
import random

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models import User, Estacionamento, RegistroEstacionamento

# --- Configurações do fluxo conforme a imagem ---
TOTAL_VEICULOS = 175
PERCENTUAL_ESTA1 = 0.60
PERCENTUAL_ESTA2 = 0.25
PERCENTUAL_DISTANTES = 0.15

MOTOS = 18
ELETRICOS = 10
ESPECIAIS = 12

HORARIO_INICIO = datetime.strptime("07:30", "%H:%M")
HORARIO_FIM = datetime.strptime("09:00", "%H:%M")

TIPOS_VAGA = ["carro", "moto", "eletrico", "especial"]

# Gera horários aleatórios entre 07:30 e 09:00

def gerar_horario():
    delta = HORARIO_FIM - HORARIO_INICIO
    segundos = random.randint(0, int(delta.total_seconds()))
    return HORARIO_INICIO + timedelta(seconds=segundos)


async def popular_dados():
    async for session in get_session():  # obtém sessão real

        # --- Criar vagas de estacionamento ---
        vagas = []
        for i in range(300):
            vaga = Estacionamento(
                codigo=f"VAGA-{i+1}",
                posicao=random.choice(["P1", "P2", "P3"]),
                tipo_vaga=random.choice(TIPOS_VAGA),
            )
            vagas.append(vaga)
            session.add(vaga)

        await session.flush()

        # --- Criando usuários (ocupantes dos veículos) ---
        usuarios = []

        num_esta1 = int(TOTAL_VEICULOS * PERCENTUAL_ESTA1)
        num_esta2 = int(TOTAL_VEICULOS * PERCENTUAL_ESTA2)
        num_distantes = TOTAL_VEICULOS - num_esta1 - num_esta2

        distribuicao_locais = ([]
            + ["ESTA1"] * num_esta1
            + ["ESTA2"] * num_esta2
            + ["DISTANTE"] * num_distantes
        )
        random.shuffle(distribuicao_locais)

        tipos_veiculos = (
            ["moto"] * MOTOS
            + ["eletrico"] * ELETRICOS
            + ["especial"] * ESPECIAIS
        )
        tipos_veiculos += ["carro"] * (TOTAL_VEICULOS - len(tipos_veiculos))
        random.shuffle(tipos_veiculos)

        for i in range(TOTAL_VEICULOS):
            usuario = User(
                username=f"user{i+1}",
                password="senha123",
                tipo_do_veiculo=tipos_veiculos[i],
                local=distribuicao_locais[i],
                email=f"user{i+1}@empresa.com",
            )
            usuarios.append(usuario)
            session.add(usuario)

        await session.flush()

        # --- Atribuir vagas e gerar registros de entrada ---
        for usuario in usuarios:
            # Filtra vagas compatíveis com o tipo do veículo
            vagas_compativeis = [v for v in vagas if v.tipo_vaga == usuario.tipo_do_veiculo]
            if not vagas_compativeis:
                vaga_escolhida = random.choice(vagas)  # fallback
            else:
                vaga_escolhida = random.choice(vagas_compativeis)

            registro = RegistroEstacionamento(
                user_id=usuario.id,
                vaga_id=vaga_escolhida.id,
                entrou=True,
            )

            session.add(registro)

        await session.commit()
        print("Dados inseridos com sucesso!")


if __name__ == "__main__":
    asyncio.run(popular_dados())