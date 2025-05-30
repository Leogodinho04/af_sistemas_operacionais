
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage

def iniciar_interface():

    OUTPUT_PATH = Path(__file__).parent
    ASSETS_PATH = OUTPUT_PATH / "build" / "assets" / "frame0"

    def relative_to_assets(path: str) -> Path:
        return ASSETS_PATH / Path(path)


    window = Tk()

    window.title("ThunderCSV - Processador de Arquivos")
    window.iconbitmap(relative_to_assets("thunder_csv.ico"))
    window.geometry("666x470")
    window.configure(bg = "#1E1E1E")

    # Fundo da interface
    canvas = Canvas(
        window,
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

    # 
    canvas.create_text(
        24.0,
        240.0,
        anchor="nw",
        text="Método de detecção de outliers",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    

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

    canvas.create_text(
        39.0,
        269.0,
        anchor="nw",
        text="IQR",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        410.0,
        381.0,
        607.0,
        395.0,
        fill="#CCCCCC",
        outline="")

    canvas.create_rectangle(
        24.0,
        269.0,
        39.0,
        284.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        119.0,
        269.0,
        anchor="nw",
        text="Z-Score",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        104.0,
        269.0,
        119.0,
        284.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        24.0,
        316.0,
        anchor="nw",
        text="Escolha os tipos de relatório a gerar",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    canvas.create_text(
        39.0,
        344.0,
        anchor="nw",
        text="CSV",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        24.0,
        344.0,
        39.0,
        359.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        122.0,
        344.0,
        anchor="nw",
        text="Excel (.xlsx)",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        104.0,
        344.0,
        119.0,
        359.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        24.0,
        316.0,
        anchor="nw",
        text="Escolha os tipos de relatório a gerar",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    canvas.create_text(
        39.0,
        344.0,
        anchor="nw",
        text="CSV",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        24.0,
        344.0,
        39.0,
        359.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        122.0,
        344.0,
        anchor="nw",
        text="Excel (.xlsx)",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        104.0,
        344.0,
        119.0,
        359.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        223.0,
        344.0,
        anchor="nw",
        text="PDF c/ gráficos",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        208.0,
        344.0,
        223.0,
        359.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        24.0,
        380.0,
        anchor="nw",
        text="Gerar gráficos",
        fill="#FFFFFF",
        font=("Jersey 20", 16 * -1)
    )

    canvas.create_text(
        42.0,
        408.0,
        anchor="nw",
        text="Boxplot",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_text(
        122.0,
        407.0,
        anchor="nw",
        text="Histograma",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        24.0,
        408.0,
        39.0,
        423.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_rectangle(
        104.0,
        408.0,
        119.0,
        423.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_rectangle(
        24.0,
        408.0,
        39.0,
        423.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_rectangle(
        104.0,
        408.0,
        119.0,
        423.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        433.0,
        313.0,
        anchor="nw",
        text="Ativar logging de execução",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        422.0,
        314.0,
        437.0,
        329.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_rectangle(
        422.0,
        314.0,
        437.0,
        329.0,
        fill="#D9D9D9",
        outline="")

    canvas.create_text(
        223.0,
        408.0,
        anchor="nw",
        text="Barras",
        fill="#E1E6ED",
        font=("Jersey 10", 16 * -1)
    )

    canvas.create_rectangle(
        208.0,
        408.0,
        223.0,
        423.0,
        fill="#D9D9D9",
        outline="")
    window.resizable(False, False)
    window.mainloop()

if __name__ == "__main__":
    iniciar_interface()