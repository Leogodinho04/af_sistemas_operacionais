
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage

arquivo_teste = "exemplo_thundercsv.xlsx"

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

def iniciar_interface():
    global entry_1

    OUTPUT_PATH = Path(__file__).parent
    ASSETS_PATH = OUTPUT_PATH / "build" / "assets" / "frame0"

    def relative_to_assets(path: str) -> Path:
        return ASSETS_PATH / Path(path)


    root = Tk()

    root.title("ThunderCSV - Processador de Arquivos")
    root.iconbitmap(relative_to_assets("thunder_csv.ico"))
    root.geometry("666x470")
    root.configure(bg = "#1E1E1E")

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
        text="Selecione os arquivos CSV",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_1 clicked"),
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
        command=lambda: print("button_3 clicked"),
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
        command=lambda: print("button_2 clicked"),
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