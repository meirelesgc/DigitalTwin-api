import pandas as pd
import random
import datetime

print("Iniciando a geração de dados para o Desafio Logístico...\n")

# --- 1. Constantes e Definições Base ---
TOTAL_VEICULOS = 175
DATA_EVENTO = "15/11/2025"

# Define o intervalo de tempo
# (Usamos data e hora para calcular timestamps aleatórios de forma segura)
data_base = datetime.date(2025, 11, 15)
INICIO_EXPEDIENTE = datetime.datetime.combine(data_base, datetime.time(7, 30, 0))
FIM_EXPEDIENTE = datetime.datetime.combine(data_base, datetime.time(9, 0, 0))

# Converte para timestamps (segundos) para facilitar a aleatorização
ts_inicio = INICIO_EXPEDIENTE.timestamp()
ts_fim = FIM_EXPEDIENTE.timestamp()

# --- 2. Geração dos Tipos de Veículo (Counts exatos) ---
print(f"Gerando {TOTAL_VEICULOS} veículos...")

num_motos = 18
num_eletricos = 10
num_pcd = 12 # "Carros especiais"
num_carros = TOTAL_VEICULOS - (num_motos + num_eletricos + num_pcd) # 135

lista_tipos = (
    ['Moto'] * num_motos +
    ['Elétrico'] * num_eletricos +
    ['PCD/Especial'] * num_pcd +
    ['Carro'] * num_carros
)

# Embaralha a lista de tipos
random.shuffle(lista_tipos)

print(f"Tipos de veículos gerados: {len(lista_tipos)} (Carros: {num_carros}, Motos: {num_motos}, Elétricos: {num_eletricos}, PCD: {num_pcd})")


# --- 3. Geração dos Locais de Trabalho (Porcentagens) ---
# Usamos round() para garantir números inteiros e ajustamos o último para bater 175
num_est_1 = round(TOTAL_VEICULOS * 0.60) # 105
num_est_2 = round(TOTAL_VEICULOS * 0.25) # 44
num_dist = TOTAL_VEICULOS - num_est_1 - num_est_2 # 175 - 105 - 44 = 26

lista_locais = (
    ['Próximo Estacionamento #1'] * num_est_1 +
    ['Próximo Estacionamento #2'] * num_est_2 +
    ['Distante de Ambos'] * num_dist
)

# Embaralha a lista de locais
random.shuffle(lista_locais)

print(f"Locais de trabalho gerados: {len(lista_locais)} (Estac. #1: {num_est_1}, Estac. #2: {num_est_2}, Distante: {num_dist})")


# --- 4. Geração dos Horários de Chegada ---

def gerar_horario_aleatorio(ts_inicio, ts_fim):
    """Gera um timestamp aleatório no intervalo e formata como H:M:S."""
    rand_ts = random.uniform(ts_inicio, ts_fim)
    horario_obj = datetime.datetime.fromtimestamp(rand_ts)
    return horario_obj.strftime("%H:%M:%S")

# Gera 175 horários aleatórios
lista_horarios = [gerar_horario_aleatorio(ts_inicio, ts_fim) for _ in range(TOTAL_VEICULOS)]

print(f"Horários de chegada aleatórios gerados: {len(lista_horarios)}")


# --- 5. Montagem do Banco de Dados (DataFrame) ---
print("\nMontando o DataFrame final...")

df_veiculos = pd.DataFrame({
    'id_veiculo': range(1, TOTAL_VEICULOS + 1),
    'data': DATA_EVENTO,
    'horario_chegada': lista_horarios,
    'tipo_veiculo': lista_tipos,
    'local_trabalho': lista_locais
})

# Reordenar colunas para melhor visualização
df_veiculos = df_veiculos[['id_veiculo', 'data', 'horario_chegada', 'tipo_veiculo', 'local_trabalho']]

# --- 6. Verificação e Exportação ---

print("\n--- Amostra do Banco de Dados (Primeiras 10 linhas) ---")
print(df_veiculos.head(10))

print("\n--- Verificação das Distribuições ---")
print("\nContagem por Tipo de Veículo:")
print(df_veiculos['tipo_veiculo'].value_counts())

print("\nContagem por Local de Trabalho:")
print(df_veiculos['local_trabalho'].value_counts())

# Exporta os dados para um arquivo que a aplicação possa ler
try:
    df_veiculos.to_csv('dados_hackathon_veiculos.csv', index=False)
    df_veiculos.to_excel('dados_hackathon_veiculos.xlsx', index=False)
    print("\n--- SUCESSO! ---")
    print("Dados salvos em 'dados_hackathon_veiculos.csv' e 'dados_hackathon_veiculos.xlsx'")
except Exception as e:
    print(f"\nErro ao salvar arquivos: {e}")