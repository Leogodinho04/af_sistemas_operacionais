
from typing import List, Tuple
import pandas as pd
from functools import partial
import numpy as np
import logging
import matplotlib.pyplot as plt
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from tempfile import NamedTemporaryFile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, messagebox, filedialog

arquivo_teste = "exemplo_thundercsv.xlsx"
caminho_arquivo_csv = ""
caminho_diretorio_saida = ""
N_CHUNKS = 4

def gerar_csv_teste():
    # Gerar pequeno
    df_pequeno = pd.DataFrame({
        'coluna1': np.random.randint(1, 100, size=30000),
        'coluna2': np.random.normal(50, 10, size=30000),
        'coluna3': np.random.randint(1, 100, size=30000)
    })

    df_pequeno.to_csv('arquivo_pequeno.csv', index=False)
    print("Arquivo pequeno gerado.")

    # Gerar médio
    df_medio = pd.DataFrame({
        'coluna1': np.random.randint(1, 100, size=400000),
        'coluna2': np.random.normal(50, 10, size=400000),
        'coluna3': np.random.randint(1, 100, size=400000)
    })

    df_medio.to_csv('arquivo_medio.csv', index=False)
    print("Arquivo medio gerado.")

    # Gerar grande
    df_grande = pd.DataFrame({
        'coluna1': np.random.randint(1, 100, size=2000000),
        'coluna2': np.random.normal(50, 10, size=2000000),
        'coluna3': np.random.randint(1, 100, size=2000000)
    })

    df_grande.to_csv('arquivo_grande.csv', index=False)
    print("Arquivo grande gerado.")

def configurar_logging():
    """
    Configura o sistema de logging do Python.
    Cria um arquivo 'execucao_thundercsv.log' com nível INFO e formato padrão.
    """

    logging.basicConfig(
        filename='execucao_thundercsv.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def selecionar_arquivo():
    """
    Abre um seletor de arquivos para escolher um arquivo CSV ou XLSX e salva o caminho globalmente.
    """
    global caminho_arquivo_csv
    caminho_arquivo_csv = filedialog.askopenfilename(
        filetypes=[("Arquivos CSV ou Excel", "*.csv *.xlsx"), ("Todos os arquivos", "*.*")]
    )
    if caminho_arquivo_csv:
        print(f"Arquivo selecionado: {caminho_arquivo_csv}")
    else:
        print("Nenhum arquivo selecionado.")

def arquivo_grande(caminho_arquivo: str, limite_mb: int = 10) -> bool:
    tamanho_mb = os.path.getsize(caminho_arquivo) / (1024 * 1024)
    return tamanho_mb > limite_mb

def selecionar_diretorio():
    """
    Abre um seletor de diretório e salva o caminho de saída globalmente.
    Isso define onde os relatórios exportados serão salvos.
    """
    global caminho_diretorio_saida
    caminho_diretorio_saida = filedialog.askdirectory()
    if caminho_diretorio_saida:
        print(f"Diretório selecionado: {caminho_diretorio_saida}")
    else:
        print("Nenhum diretório selecionado.")

def carregar_arquivo_csv(file_path: str) -> pd.DataFrame | None:
    """
    Carrega um arquivo .csv ou .xlsx e retorna um DataFrame pandas.
    Detecta a extensão e tenta diferentes codificações para evitar erros.
    """
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo não foi encontrado em '{file_path}'.")
        return None

    if not os.path.isfile(file_path):
        print(f"Erro: O caminho '{file_path}' não aponta para um arquivo válido.")
        return None

    extensao = Path(file_path).suffix.lower()

    try:
        if extensao == ".csv":
            try:
                return pd.read_csv(file_path, encoding='utf-8', sep=',', on_bad_lines='skip')
            except UnicodeDecodeError:
                print("UTF-8 falhou. Tentando latin1...")
                try:
                    return pd.read_csv(file_path, encoding='latin1', sep=',', on_bad_lines='skip')
                except Exception:
                    print("latin1 falhou. Tentando windows-1252...")
                    return pd.read_csv(file_path, encoding='windows-1252', sep=',', on_bad_lines='skip')
        elif extensao == ".xlsx":
            return pd.read_excel(file_path)
        else:
            messagebox.showerror("Erro", "Formato de arquivo não suportado. Use CSV ou XLSX.")
            return None
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")
        return None

def validar_estrutura_dados(df: pd.DataFrame, colunas_numericas_esperadas: List[str] = None, interromper_em_erro: bool = False) -> Tuple[bool, pd.DataFrame]:
    """
    Valida a estrutura de um DataFrame, verificando tipos de dados, valores nulos e inconsistências.
    Pode, opcionalmente, interromper o processo ou tentar converter colunas.

    Args:
        df (pd.DataFrame): O DataFrame a ser validado.
        colunas_numericas_esperadas (List[str], opcional): Uma lista de nomes de colunas que se espera que sejam numéricas.
                                                         Se None, todas as colunas serão verificadas quanto a nulos/tipos.
        interromper_em_erro (bool): Se True, a função retorna (False, None) e imprime uma mensagem de erro
                                     se houver alguma inconsistência grave (nulos em colunas esperadas como numéricas
                                     ou falha na conversão). Se False, tenta prosseguir e corrigir.

    Returns:
        Tuple[bool, pd.DataFrame]: Uma tupla contendo:
                                   - bool: True se a validação passar (ou se erros forem tratados), False caso contrário.
                                   - pd.DataFrame: O DataFrame potencialmente limpo ou modificado, ou None se a validação falhar e 'interromper_em_erro' for True.
    """
    print("\n--- Iniciando validação da estrutura dos dados ---")
    valido = True
    df_copia = df.copy() # Trabalha em uma cópia para não alterar o DataFrame original diretamente
    
    # 1. Verifica a presença de colunas numéricas esperadas
    if colunas_numericas_esperadas:
        for col in colunas_numericas_esperadas:
            if col not in df_copia.columns:
                print(f"Aviso: Coluna numérica esperada '{col}' não encontrada no DataFrame.")
                if interromper_em_erro:
                    print("Processo interrompido devido à coluna numérica esperada não encontrada.")
                    return False, None
                continue # Pula para a próxima coluna se não encontrada

            # Tenta converter a coluna para tipo numérico
            # 'coerce' transforma valores não numéricos em NaN (Not a Number)
            df_copia[col] = pd.to_numeric(df_copia[col], errors='coerce')
            
            # Verifica se a conversão resultou em muitos NaNs (indicando valores não numéricos)
            # Um limite razoável para a proporção de NaNs para considerar a coluna numérica corrompida.
            # Aqui, consideramos que se mais de 20% da coluna se tornou NaN após a coerção, há um problema.
            na_count = df_copia[col].isnull().sum()
            if na_count > 0:
                total_rows = len(df_copia[col])
                if total_rows > 0:
                    na_percentage = (na_count / total_rows) * 100
                    print(f"Alerta: Coluna '{col}' contém {na_count} ({na_percentage:.2f}%) valores não numéricos que foram convertidos para NaN.")
                else:
                     print(f"Alerta: Coluna '{col}' contém {na_count} valores não numéricos que foram convertidos para NaN (DataFrame vazio).")

                if na_percentage > 20 and interromper_em_erro: # Exemplo: se mais de 20% for NaN
                    print(f"Erro: Coluna '{col}' tem alta proporção de valores não numéricos. Interrompendo processo.")
                    return False, None
                
                # Opcional: preencher NaNs com a média ou 0, ou remover as linhas
                # df_copia[col].fillna(df_copia[col].mean(), inplace=True) # Preenche com a média
                # df_copia.dropna(subset=[col], inplace=True) # Remove linhas com NaN nessa coluna
    
    # 2. Verifica valores nulos em todas as colunas
    nulos_por_coluna = df_copia.isnull().sum()
    colunas_com_nulos = nulos_por_coluna[nulos_por_coluna > 0]

    if not colunas_com_nulos.empty:
        print("\nColunas com valores nulos:")
        print(colunas_com_nulos)
        valido = False # Há nulos, então a validação não é perfeita
        
        # Estratégia de tratamento de nulos:
        # Você pode optar por:
        # a) Remover linhas com nulos: df_copia.dropna(inplace=True)
        # b) Preencher nulos: df_copia.fillna(value=0, inplace=True) ou df_copia.fillna(df_copia.mean(), inplace=True)
        # c) Interromper se for crítico
        
        # Exemplo: Se há nulos em colunas que eram esperadas como numéricas e a flag de interrupção está ativada
        if interromper_em_erro and colunas_numericas_esperadas:
             for col_num_esperada in colunas_numericas_esperadas:
                 if col_num_esperada in colunas_com_nulos.index:
                     print(f"Erro: Valores nulos encontrados na coluna numérica esperada '{col_num_esperada}'. Interrompendo processo.")
                     return False, None
        
        print("Aviso: Valores nulos detectados. Considere tratá-los (remoção, preenchimento, etc.) antes da análise.")
    else:
        print("Nenhum valor nulo encontrado em todo o DataFrame.")

    # 3. Verifica tipos inconsistentes (após a coerção para numéricos)
    print("\nTipos de dados atuais das colunas:")
    print(df_copia.dtypes)

    # Verifica se há 'object' dtypes em colunas que deveriam ser numéricas
    if colunas_numericas_esperadas:
        for col in colunas_numericas_esperadas:
            if col in df_copia.columns and not pd.api.types.is_numeric_dtype(df_copia[col]):
                print(f"Erro: Coluna '{col}' ainda não é numérica após tentativa de conversão. Tipo atual: {df_copia[col].dtype}")
                valido = False
                if interromper_em_erro:
                    print("Processo interrompido devido a tipo de dado inconsistente em coluna numérica esperada.")
                    return False, None
    
    if valido:
        print("\nValidação da estrutura dos dados concluída: OK.")
        messagebox.showinfo("Sucesso", "Validação da estrutura dos dados concluída")
    else:
        print("\nValidação da estrutura dos dados concluída: COM AVISOS/ERROS. Verifique as mensagens acima.")
    
    return valido, df_copia

def filtrar_colunas(df: pd.DataFrame, colunas_escolhidas: List[str]) -> pd.DataFrame | None:
    """
    Filtra um DataFrame, mantendo apenas as colunas especificadas.
    Gera uma mensagem de erro se alguma coluna não existir no DataFrame.

    Args:
        df (pd.DataFrame): O DataFrame original.
        colunas_escolhidas (List[str]): Uma lista com os nomes das colunas a serem selecionadas.

    Returns:
        pd.DataFrame | None: Um novo DataFrame contendo apenas as colunas escolhidas,
                             ou None se alguma coluna especificada não for encontrada.
    """
    if not colunas_escolhidas:
        print("Aviso: Nenhuma coluna foi escolhida para filtragem. O DataFrame original será retornado.")
        return df

    # Verifica se todas as colunas escolhidas existem no DataFrame
    colunas_existentes = df.columns.tolist()
    colunas_nao_encontradas = [col for col in colunas_escolhidas if col not in colunas_existentes]

    if colunas_nao_encontradas:
        print(f"Erro: As seguintes colunas não foram encontradas no arquivo: {', '.join(colunas_nao_encontradas)}")
        print(f"Colunas disponíveis no arquivo: {', '.join(colunas_existentes)}")
        return None
    
    # Seleciona apenas as colunas escolhidas
    df_filtrado = df[colunas_escolhidas]
    print(f"Colunas '{', '.join(colunas_escolhidas)}' selecionadas com sucesso.")
    return df_filtrado

def detectar_outliers(df: pd.DataFrame, metodo: str = "IQR", colunas: list = None) -> pd.DataFrame:
    """
    Detecta outliers nas colunas numéricas de um DataFrame usando IQR ou Z-Score,
    e retorna também estatísticas resumidas dos outliers.

    Parâmetros:
        df (pd.DataFrame): DataFrame com os dados.
        metodo (str): "IQR" ou "Z-Score".
        colunas (list): Lista de colunas a analisar (opcional).

    Retorno:
        tuple:
            - pd.DataFrame: DataFrame com colunas extras indicando outliers.
            - dict: Estatísticas dos outliers por coluna (quantidade e percentual).
    """
    df_out = df.copy()
    if colunas is None:
        colunas = df.select_dtypes(include='number').columns 

    estatisticas_outliers = {}

    for coluna in colunas:
        if coluna not in df.columns:
            continue 

        if metodo == "IQR":
            # Define como outlier qualquer valor muito abaixo do primeiro quartil (Q1) ou muito acima do terceiro quartil (Q3)
            q1 = df[coluna].quantile(0.25)
            q3 = df[coluna].quantile(0.75)
            iqr = q3 - q1
            lim_inf = q1 - 1.5 * iqr
            lim_sup = q3 + 1.5 * iqr
            outliers = (df[coluna] < lim_inf) | (df[coluna] > lim_sup)

        elif metodo == "Z-Score":
            # Define como outlier qualquer valor muito distante da média
            media = df[coluna].mean()
            desvio = df[coluna].std()
            z_score = (df[coluna] - media) / desvio
            outliers = z_score.abs() > 3

        else:
            raise ValueError("Método inválido. Use 'IQR' ou 'Z-Score'.")

        # Marca no DataFrame
        df_out[f"{coluna}_outlier"] = outliers

        # Salva estatísticas
        quantidade = outliers.sum()
        percentual = round(quantidade / len(df) * 100, 2)
        estatisticas_outliers[coluna] = {
            "quantidade_outliers": int(quantidade),
            "percentual_outliers": percentual
        }

    return df_out, estatisticas_outliers

def calcular_estatisticas(df: pd.DataFrame) -> dict:
    """
    Calcula estatísticas básicas (média, soma, mínimo, máximo, contagem)
    para cada coluna numérica do DataFrame.

    Parâmetros:
        df (pd.DataFrame): DataFrame com os dados filtrados.

    Retorno:
        dict: Dicionário contendo as estatísticas por coluna.
    """
    estatisticas = {}
    colunas_numericas = df.select_dtypes(include='number').columns

    for coluna in colunas_numericas:
        dados = df[coluna]
        estatisticas[coluna] = {
            'media': dados.mean(),
            'soma': dados.sum(),
            'minimo': dados.min(),
            'maximo': dados.max(),
            'contagem': dados.count()
        }

    return estatisticas

def gerar_graficos_pdf(df: pd.DataFrame, opcoes: dict, pasta_saida: str, nome_pdf: str = "relatorio_graficos.pdf"):
    """
    Gera gráficos com base nas opções e insere todos em um PDF salvo na pasta de saída.

    Parâmetros:
        df (pd.DataFrame): Dados a serem usados nos gráficos.
        opcoes (dict): Dicionário com opções de gráfico (ex: {"boxplot": True, "hist": False}).
        pasta_saida (str): Caminho onde o PDF será salvo.
        nome_pdf (str): Nome do arquivo PDF de saída.

    Retorno:
        None
    """
    colunas_numericas = df.select_dtypes(include='number').columns
    pdf_path = os.path.join(pasta_saida, nome_pdf)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elementos = []
    styles = getSampleStyleSheet()

    for coluna in colunas_numericas:
        if coluna.endswith("_outlier"):
            continue

        elementos.append(Paragraph(f"Gráficos da coluna: {coluna}", styles['Heading2']))
        elementos.append(Spacer(1, 12))

        if opcoes.get("boxplot"):
            with NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                plt.figure()
                plt.boxplot(df[coluna].dropna(), vert=False, labels=[coluna])
                plt.title(f"Boxplot - {coluna}")
                plt.xlabel(coluna)
                plt.savefig(tmp.name)
                plt.close()
                elementos.append(RLImage(tmp.name, width=400, height=300))
                elementos.append(Spacer(1, 12))

        if opcoes.get("hist"):
            with NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                plt.figure()
                plt.hist(df[coluna].dropna(), bins=10, color="skyblue", edgecolor="black")
                plt.title(f"Histograma - {coluna}")
                plt.savefig(tmp.name)
                plt.close()
                elementos.append(RLImage(tmp.name, width=400, height=300))
                elementos.append(Spacer(1, 12))

        if opcoes.get("bar") and df[coluna].nunique() <= 20:
            with NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                plt.figure()
                df[coluna].value_counts().sort_index().plot(kind="bar", color="lightgreen", edgecolor="black")
                plt.title(f"Gráfico de Barras - {coluna}")
                plt.tight_layout()
                plt.savefig(tmp.name)
                plt.close()
                elementos.append(RLImage(tmp.name, width=400, height=300))
                elementos.append(Spacer(1, 12))

    doc.build(elementos)
    print(f"PDF com gráficos salvo em: {pdf_path}")

def exportar_excel(df: pd.DataFrame, caminho: str):

    """
    Exporta um DataFrame como arquivo Excel (.xlsx) para o caminho fornecido.
    Inclui mensagens de sucesso ou erro e logging.
    """

    try:
        df.to_excel(caminho, index=False)
        print(f"Excel salvo em: {caminho}")
        logging.info(f"Relatório Excel exportado para: {caminho}")
        messagebox.showinfo("Sucesso", "Excel salvo com sucesso!")
        
    except Exception as e:
        logging.error(f"Erro ao exportar Excel: {e}")
        messagebox.showerror("Erro", f"Erro ao salvar Excel: {e}")

def exportar_csv(df: pd.DataFrame, caminho: str):

    """
    Exporta um DataFrame como arquivo CSV para o caminho fornecido.
    Inclui mensagens de sucesso ou erro e logging.
    """

    try:
        df.to_csv(caminho, index=False)
        print(f"CSV salvo em: {caminho}")
        logging.info(f"Relatório CSV exportado para: {caminho}")
        messagebox.showinfo("Sucesso", "CSV salvo com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao exportar CSV: {e}")
        messagebox.showerror("Erro", f"Erro ao salvar CSV: {e}")

def dividir_em_chunks(df: pd.DataFrame, n_chunks: int) -> List[pd.DataFrame]:
    return np.array_split(df, n_chunks)

def processar_chunk(chunk: pd.DataFrame, metodo: str, colunas: list) -> pd.DataFrame:
    chunk, _ = detectar_outliers(chunk, metodo, colunas)
    return chunk

def processar_em_threads(df: pd.DataFrame, funcao_processamento, n_threads=4):
    chunks = dividir_em_chunks(df, n_threads)
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        resultados = list(executor.map(funcao_processamento, chunks))
    return pd.concat(resultados)

def processar_em_processos(df: pd.DataFrame, funcao_processamento, n_chunks=4):
    chunks = dividir_em_chunks(df, n_chunks)
    with ProcessPoolExecutor(max_workers=n_chunks) as executor:
        resultados = list(executor.map(funcao_processamento, chunks))
    return pd.concat(resultados)

def funcao_processamento_outliers(chunk: pd.DataFrame, metodo: str, colunas: list) -> pd.DataFrame:
    return detectar_outliers(chunk, metodo, colunas)[0]

def iniciar_processamento():

    """
    Função principal que executa o pipeline de análise de dados.
    - Coleta os caminhos de entrada e saída definidos pelo usuário.
    - Lê o arquivo CSV ou XLSX e valida a estrutura das colunas.
    - Aplica o método de detecção de outliers selecionado.
    - Calcula estatísticas descritivas e gera relatórios em CSV, Excel e PDF.
    - Registra logs e exibe mensagens de conclusão ou erro.
    """

    global entry_1, var_csv, var_excel, var_pdf, var_boxplot, var_histograma, var_barras, var_logging, metodo_outlier
    global caminho_arquivo_csv, caminho_diretorio_saida

    caminho_csv = caminho_arquivo_csv
    caminho_saida = caminho_diretorio_saida

    if not caminho_csv or not caminho_saida:
        messagebox.showwarning("Aviso", "Por favor, selecione o arquivo CSV e o diretório de saída.")
        return
    
    colunas = entry_1.get().split(",")
    metodo = metodo_outlier.get()
    opcoes_graficos = {
        "boxplot": var_boxplot.get(),
        "hist": var_histograma.get(),
        "bar": var_barras.get()
    }

    if var_logging.get():
        configurar_logging()
        logging.info("Execução iniciada.")

    df = carregar_arquivo_csv(caminho_csv)
    if df is None:
        return

    valido, df = validar_estrutura_dados(df, colunas, interromper_em_erro=True)
    if not valido:
        return

    df = filtrar_colunas(df, colunas)
    if df is None:
        return

    n_linhas = len(df)

    if len(df) < 50_000:
        print("Usando processamento sequencial (arquivo pequeno)...")
        df = processar_em_threads(df, partial(funcao_processamento_outliers, metodo=metodo, colunas=colunas), n_threads=1)

    elif len(df) < 500_000:
        print("Usando multithreading (arquivo médio)...")
        df = processar_em_threads(df, partial(funcao_processamento_outliers, metodo=metodo, colunas=colunas), n_threads=4)

    else:
        print("Usando multiprocessing (arquivo grande)...")
        df = processar_em_processos(df, partial(funcao_processamento_outliers, metodo=metodo, colunas=colunas), n_chunks=4)

    stats = calcular_estatisticas(df)

    if var_csv.get():
        exportar_csv(df, os.path.join(caminho_saida, "relatorio.csv"))
    if var_excel.get():
        exportar_excel(df, os.path.join(caminho_saida, "relatorio.xlsx"))
    if var_pdf.get():
        gerar_graficos_pdf(df, opcoes_graficos, caminho_saida)

    messagebox.showinfo("Concluído", "Processamento finalizado com sucesso!")
    logging.info("Processamento finalizado.")

def iniciar_interface():
    global entry_1, var_csv, var_excel, var_pdf, var_boxplot, var_histograma, var_barras, var_logging

    OUTPUT_PATH = Path(__file__).parent
    ASSETS_PATH = OUTPUT_PATH / "build" / "assets" / "frame0"

    def relative_to_assets(path: str) -> Path:
        return ASSETS_PATH / Path(path)


    root = Tk()

    root.title("ThunderCSV - Processador de Arquivos")
    try:
        root.iconbitmap(relative_to_assets("thunder_csv.ico"))
    except tk.TclError:
        print("Aviso: Ícone não encontrado ou inválido. Continuando sem ícone.")

    root.geometry("666x470")
    root.configure(bg = "#1E1E1E")

    gerar_csv_teste()

    # Fundo da interface
    canvas = Canvas(
        root,
        bg = "#1E1E1E",
        height = 470,
        width = 666,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    

    canvas.place(x = 0, y = 0)

    # Cabeçalho
    canvas.create_rectangle(
        0.0,
        0.0,
        666.0,
        90.0,
        fill="#0061A2",
        outline="")

    # Titulo
    canvas.create_text(
        23.0,
        13.0,
        anchor="nw",
        text="ThunderCSV",
        fill="#FFD700",
        font=("Jersey 10", 64 * -1)
    )

    # Subtitulo
    canvas.create_text(
        381.0,
        40.0,
        anchor="nw",
        text="Processador de CSVs",
        fill="#FFD700",
        font=("Jersey 20", 32 * -1)
    )

    # Selecionar o arquivos
    canvas.create_text(
        24.0,
        125.0,
        anchor="nw",
        text="Selecione o arquivo CSV",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=selecionar_arquivo,
        relief="flat"
    )

    button_1.place(
        x=192.0,
        y=124.0,
        width=58.0,
        height=17.0
    )

    # Diretório p/ salvar
    canvas.create_text(
        385.0,
        125.0,
        anchor="nw",
        text="Diretório para salvar relatórios",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    button_image_3 = PhotoImage(
        file=relative_to_assets("button_3.png"))
    button_3 = Button(
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=selecionar_diretorio,
        relief="flat"
    )
    button_3.place(
        x=585.0,
        y=124.0,
        width=58.0,
        height=17.0
    )

    # Campo texto para escolher as colunas
    canvas.create_text(
        24.0,
        166.0,
        anchor="nw",
        text="Escolha as colunas por análise (separe por vírgula)",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )
    
    entry_image_1 = PhotoImage(
        file=relative_to_assets("entry_1.png"))
    entry_bg_1 = canvas.create_image(
        184.0,
        205.0,
        image=entry_image_1
    )
    entry_1 = Entry(
        bd=0,
        bg="#CCCCCC",
        fg="#000716",
        highlightthickness=0,
        font=("Jersey 20", 15 * -1)
    )
    entry_1.place(
        x=29.0,
        y=195.0,
        width=310.0,
        height=18.0
    )

    # Detecção de outliers
    canvas.create_text(
        24.0,
        240.0,
        anchor="nw",
        text="Método de detecção de outliers",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    global metodo_outlier
    metodo_outlier = tk.StringVar(value="")


    radio_iqr = tk.Radiobutton(
        root,
        text="IQR",
        variable=metodo_outlier,
        value="IQR",
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        fg="#E1E6ED",
        selectcolor="#1E1E1E",
        font=("Jersey 10", 16 * -1),
        highlightthickness=0
    )
    radio_iqr.place(x=20, y=269)

    radio_z = tk.Radiobutton(
        root,
        text="Z-Score",
        variable=metodo_outlier,
        value="Z-Score",
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        fg="#E1E6ED",
        selectcolor="#1E1E1E",
        font=("Jersey 10", 16 * -1),
        highlightthickness=0
    )
    radio_z.place(x=100, y=269)

    # Tipos de relatórios
    canvas.create_text(
        24.0,
        316.0,
        anchor="nw",
        text="Escolha os tipos de relatório a gerar",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    canvas.create_text(
        46.0,
        343.0,
        anchor="nw",
        text="CSV",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )
    var_csv = tk.BooleanVar(value=False)
    checkbox_csv = tk.Checkbutton(
        root,
        variable=var_csv,
        onvalue=True,
        offvalue=False,
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        highlightthickness=0,
        relief="flat"
    )
    checkbox_csv.place(x=20, y=340)

    canvas.create_text(
        126.0,
        343.0,
        anchor="nw",
        text="Excel (.xlsx)",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )
    var_excel = tk.BooleanVar(value=False)
    checkbox_excel = tk.Checkbutton(
        root,
        variable=var_excel,
        onvalue=True,
        offvalue=False,
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        highlightthickness=0,
        relief="flat"
    )
    checkbox_excel.place(x=100, y=340)

    canvas.create_text(
        234.0,
        343.0,
        anchor="nw",
        text="PDF c/ gráficos",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )
    var_pdf = tk.BooleanVar(value=False)
    checkbox_pdf = tk.Checkbutton(
        root,
        variable=var_pdf,
        onvalue=True,
        offvalue=False,
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        highlightthickness=0,
        relief="flat"
    )
    checkbox_pdf.place(x=208, y=340)

    # Gerar gráficos
    canvas.create_text(
        24.0,
        380.0,
        anchor="nw",
        text="Gerar gráficos",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    canvas.create_text(
        46.0,
        406.0,
        anchor="nw",
        text="Boxplot",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )
    var_boxplot = tk.BooleanVar(value=False)
    checkbox_boxplot = tk.Checkbutton(
        root,
        variable=var_boxplot,
        onvalue=True,
        offvalue=False,
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        highlightthickness=0,
        relief="flat"
    )
    checkbox_boxplot.place(x=20, y=403)

    canvas.create_text(
        126.0,
        406.0,
        anchor="nw",
        text="Histograma",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )
    var_histograma = tk.BooleanVar(value=False)
    checkbox_histograma = tk.Checkbutton(
        root,
        variable=var_histograma,
        onvalue=True,
        offvalue=False,
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        highlightthickness=0,
        relief="flat"
    )
    checkbox_histograma.place(x=100, y=403)

    canvas.create_text(
        234.0,
        406.0,
        anchor="nw",
        text="Barras",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )
    var_barras = tk.BooleanVar(value=False)
    checkbox_barras = tk.Checkbutton(
        root,
        variable=var_barras,
        onvalue=True,
        offvalue=False,
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        highlightthickness=0,
        relief="flat"
    )
    checkbox_barras.place(x=208, y=403)

    # Ativar logging de execução
    canvas.create_text(
        455.0,
        318.0,
        anchor="nw",
        text="Ativar logging de execução",
        fill="#E1E6ED",
        font=("Jersey 10", 14 * -1)
    )
    var_logging = tk.BooleanVar(value=False)
    checkbox_logging = tk.Checkbutton(
        root,
        variable=var_logging,
        onvalue=True,
        offvalue=False,
        bg="#1E1E1E",
        activebackground="#1E1E1E",
        highlightthickness=0,
        relief="flat"
    )
    checkbox_logging.place(x=429, y=314)
    
    # Iniciar processamento
    button_image_2 = PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=iniciar_processamento,
        relief="flat"
    )
    button_2.place(
        x=422.0,
        y=347.0,
        width=174.0,
        height=23.0
    )

    # Cancelar
    button_image_4 = PhotoImage(
        file=relative_to_assets("button_4.png"))
    button_4 = Button(
        image=button_image_4,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_4 clicked"),
        relief="flat"
    )
    button_4.place(
        x=475.0,
        y=405.0,
        width=67.0,
        height=17.0
    )

    # Barra de progresso
    canvas.create_rectangle(
        410.0,
        381.0,
        607.0,
        395.0,
        fill="#CCCCCC",
        outline="")
    
    root.resizable(False, False)
    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()