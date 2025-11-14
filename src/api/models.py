from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, registry
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
# (table_registry e mapped_as_dataclass já devem estar definidos)


table_registry = registry()


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    tipo_do_veiculo: Mapped[str]
    local: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


@mapped_as_dataclass(table_registry)
class Estacionamento:
    __tablename__ = "estacionamentos"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    
    codigo: Mapped[str] = mapped_column(unique=True) 
    
    posicao: Mapped[str]
    
    tipo_vaga: Mapped[str]


@mapped_as_dataclass(table_registry)
class RegistroEstacionamento:
    __tablename__ = "registros_estacionamento"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    # Chave estrangeira para a tabela 'users'. Isso liga o registro ao usuário.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Chave estrangeira para a tabela 'estacionamentos'. Liga o registro à vaga.
    vaga_id: Mapped[int] = mapped_column(ForeignKey("estacionamentos.id"))

    # Horário do evento (já pega o horário atual por padrão)
    horario: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    
    # Campo booleano: True para Entrada, False para Saída
    entrou: Mapped[bool]

    # --- Relacionamentos (Opcional, mas muito recomendado) ---
    # Isso permite que você acesse, por exemplo, 'registro.usuario.username'
    
    usuario: Mapped["User"] = relationship(init=False)
    vaga: Mapped["Estacionamento"] = relationship(init=False)