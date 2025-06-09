import pandas as pd
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from thunder_csv import detectar_outliers 

def gerar_dataframe_teste(linhas: int, colunas: int) -> pd.DataFrame:
    dados = {f"col{i}": np.random.normal(100, 20, linhas) for i in range(colunas)}
    return pd.DataFrame(dados)

def processar_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    # Simula processamento pesado com cálculo extra
    resultado, _ = detectar_outliers(chunk, metodo="IQR")
    for col in chunk.select_dtypes(include='number').columns:
        _ = chunk[col].apply(lambda x: np.sqrt(x ** 2 + 1))  # Simulação de carga, forçar processamento pesado
    return resultado

def dividir_em_chunks(df: pd.DataFrame, n_chunks: int):
    tamanho = len(df) // n_chunks
    return [df.iloc[i:i + tamanho] for i in range(0, len(df), tamanho)]

def sequencial(df: pd.DataFrame):
    return processar_chunk(df)

def multithreading(df: pd.DataFrame, n_threads=4):
    chunks = dividir_em_chunks(df, n_threads)
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        resultados = list(executor.map(processar_chunk, chunks))
    return pd.concat(resultados)

def multiprocessing_mode(df: pd.DataFrame, n_processes=4):
    chunks = dividir_em_chunks(df, n_processes)
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        resultados = list(executor.map(processar_chunk, chunks))
    return pd.concat(resultados)

def testar_tempo(funcao, *args):
    inicio = time.perf_counter()
    resultado = funcao(*args)
    fim = time.perf_counter()
    return fim - inicio, resultado

def executar_teste(nome: str, df: pd.DataFrame):
    print(f"\n==== {nome} ====")
    tempo_seq, _ = testar_tempo(sequencial, df)
    print(f"[Sequencial] Tempo: {tempo_seq:.2f}s")

    for n in [1, 2, 4]:
        tempo_thread, _ = testar_tempo(multithreading, df, n)
        print(f"[Multithreading ({n} threads)] Tempo: {tempo_thread:.2f}s")

    for n in [1, 2, 4]:
        tempo_proc, _ = testar_tempo(multiprocessing_mode, df, n)
        print(f"[Multiprocessing ({n} processos)] Tempo: {tempo_proc:.2f}s")

def main():
    df_pequeno = gerar_dataframe_teste(linhas=5_000, colunas=5)
    df_medio = gerar_dataframe_teste(linhas=400_000, colunas=5)
    df_grande = gerar_dataframe_teste(linhas=2_000_000, colunas=5)

    executar_teste("Arquivo Pequeno (5mil linhas)", df_pequeno)
    executar_teste("Arquivo Médio (400mil linhas)", df_medio)
    executar_teste("Arquivo Grande (2mi linhas)", df_grande)

if __name__ == "__main__":
    main()
