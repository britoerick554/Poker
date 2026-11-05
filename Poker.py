
import tkinter as tk
from collections import Counter
import random

PALOS = ["♠", "♥", "♦", "♣"]
VALORES = list(range(2, 15))


def nombre_carta(carta):
    valor, palo = carta
    nombres = {11: "J", 12: "Q", 13: "K", 14: "A"}
    return f"{nombres.get(valor, valor)}{palo}"


def evaluar(mano):
    valores = sorted([c[0] for c in mano], reverse=True)
    palos = [c[1] for c in mano]
    conteo = Counter(valores)

    grupos = sorted(
        ((cantidad, valor) for valor, cantidad in conteo.items()),
        reverse=True
    )

    color = len(set(palos)) == 1
    unicos = sorted(set(valores))

    escalera = 0
    if len(unicos) == 5:
        if unicos[-1] - unicos[0] == 4:
            escalera = unicos[-1]
        elif unicos == [2, 3, 4, 5, 14]:
            escalera = 5

    if color and escalera:
        return (8, escalera), "Escalera de color"
    if grupos[0][0] == 4:
        return (7, grupos[0][1], grupos[1][1]), "Póker"
    if [g[0] for g in grupos] == [3, 2]:
        return (6, grupos[0][1], grupos[1][1]), "Full house"
    if color:
        return (5, *valores), "Color"
    if escalera:
        return (4, escalera), "Escalera"
    if grupos[0][0] == 3:
        restantes = sorted(
            [v for v in valores if v != grupos[0][1]],
            reverse=True
        )
        return (3, grupos[0][1], *restantes), "Trío"
    if [g[0] for g in grupos][:2] == [2, 2]:
        pares = sorted(
            [v for v, n in conteo.items() if n == 2],
            reverse=True
        )
        otro = next(v for v, n in conteo.items() if n == 1)
        return (2, *pares, otro), "Doble pareja"
    if grupos[0][0] == 2:
        par = grupos[0][1]
        restantes = sorted(
            [v for v in valores if v != par],
            reverse=True
        )
        return (1, par, *restantes), "Pareja"

    return (0, *valores), "Carta alta"


class Poker:
    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("PÓKER - Python")
        ventana.geometry("800x620")
        ventana.configure(bg="#116530")
        ventana.resizable(False, False)

        self.victorias = 0
        self.derrotas = 0
        self.empates = 0
        self.seleccionadas = set()
        self.terminado = False

        tk.Label(
            ventana, text="♠  PÓKER  ♥",
            font=("Arial", 30, "bold"),
            fg="white", bg="#116530"
        ).pack(pady=15)

        self.marcador = tk.Label(
            ventana, font=("Arial", 13),
            fg="white", bg="#116530"
        )
        self.marcador.pack()

        tk.Label(
            ventana, text="COMPUTADORA",
            font=("Arial", 17, "bold"),
            fg="white", bg="#116530"
        ).pack(pady=(25, 5))

        self.frame_cpu = tk.Frame(ventana, bg="#116530")
        self.frame_cpu.pack()

        self.cartas_cpu = []
        for i in range(5):
            carta = tk.Label(
                self.frame_cpu, text="★",
                width=5, height=3,
                font=("Arial", 19, "bold"),
                bg="#183b78", fg="white",
                relief="raised", bd=3
            )
            carta.pack(side="left", padx=5)
            self.cartas_cpu.append(carta)

        self.info_cpu = tk.Label(
            ventana, text="Cartas ocultas",
            font=("Arial", 12), fg="white", bg="#116530"
        )
        self.info_cpu.pack(pady=6)

        tk.Label(
            ventana, text="TUS CARTAS",
            font=("Arial", 17, "bold"),
            fg="white", bg="#116530"
        ).pack(pady=(20, 5))

        self.frame_jugador = tk.Frame(ventana, bg="#116530")
        self.frame_jugador.pack()

        self.cartas_jugador = []
        for i in range(5):
            boton = tk.Button(
                self.frame_jugador,
                width=5, height=2,
                font=("Arial", 19, "bold"),
                bg="white",
                relief="raised", bd=3,
                command=lambda x=i: self.seleccionar(x)
            )
            boton.pack(side="left", padx=5)
            self.cartas_jugador.append(boton)

        self.info_jugador = tk.Label(
            ventana, text="",
            font=("Arial", 12), fg="white", bg="#116530"
        )
        self.info_jugador.pack(pady=7)

        self.resultado = tk.Label(
            ventana,
            text="Selecciona las cartas que quieres cambiar",
            font=("Arial", 14, "bold"),
            fg="#ffec80", bg="#116530"
        )
        self.resultado.pack(pady=15)

        controles = tk.Frame(ventana, bg="#116530")
        controles.pack()

        self.boton_cambiar = tk.Button(
            controles, text="CAMBIAR CARTAS",
            font=("Arial", 12, "bold"),
            bg="#f4c542", width=18,
            command=self.cambiar_cartas
        )
        self.boton_cambiar.pack(side="left", padx=10)

        tk.Button(
            controles, text="NUEVA PARTIDA",
            font=("Arial", 12, "bold"),
            bg="#dddddd", width=18,
            command=self.nueva_partida
        ).pack(side="left", padx=10)

        self.nueva_partida()

    def nueva_partida(self):
        self.mazo = [
            (valor, palo)
            for palo in PALOS
            for valor in VALORES
        ]
        random.shuffle(self.mazo)

        self.jugador = [self.mazo.pop() for _ in range(5)]
        self.cpu = [self.mazo.pop() for _ in range(5)]

        self.seleccionadas.clear()
        self.terminado = False
        self.boton_cambiar.config(state="normal")

        self.resultado.config(
            text="Selecciona las cartas que quieres cambiar"
        )
        self.info_cpu.config(text="Cartas ocultas")
        self.actualizar_cartas()
        self.actualizar_marcador()

    def seleccionar(self, indice):
        if self.terminado:
            return

        if indice in self.seleccionadas:
            self.seleccionadas.remove(indice)
        else:
            self.seleccionadas.add(indice)

        self.actualizar_cartas()

    def actualizar_cartas(self):
        for i, carta in enumerate(self.jugador):
            texto = nombre_carta(carta)
            color = "red" if carta[1] in ["♥", "♦"] else "black"
            fondo = "#ffda7b" if i in self.seleccionadas else "white"

            self.cartas_jugador[i].config(
                text=texto, fg=color, bg=fondo
            )

        _, nombre = evaluar(self.jugador)
        self.info_jugador.config(text=f"Tu mano: {nombre}")

        for i, carta in enumerate(self.cpu):
            if self.terminado:
                color = "red" if carta[1] in ["♥", "♦"] else "black"
                self.cartas_cpu[i].config(
                    text=nombre_carta(carta),
                    bg="white", fg=color
                )
            else:
                self.cartas_cpu[i].config(
                    text="★", bg="#183b78", fg="white"
                )

    def jugar_cpu(self):
        puntuacion, _ = evaluar(self.cpu)
        categoria = puntuacion[0]
        conteo = Counter(c[0] for c in self.cpu)

        if categoria in [8, 6, 5, 4]:
            return

        if categoria in [7, 3, 2, 1]:
            conservar = {
                valor for valor, cantidad in conteo.items()
                if cantidad >= 2
            }
            indices = [
                i for i, carta in enumerate(self.cpu)
                if carta[0] not in conservar
            ]
        else:
            conteo_palos = Counter(c[1] for c in self.cpu)
            palo, cantidad = conteo_palos.most_common(1)[0]

            if cantidad == 4:
                indices = [
                    i for i, carta in enumerate(self.cpu)
                    if carta[1] != palo
                ]
            else:
                altos = sorted(
                    range(5),
                    key=lambda i: self.cpu[i][0],
                    reverse=True
                )[:2]
                indices = [
                    i for i in range(5) if i not in altos
                ]

        for i in indices:
            self.cpu[i] = self.mazo.pop()

    def cambiar_cartas(self):
        if self.terminado:
            return

        for i in self.seleccionadas:
            self.jugador[i] = self.mazo.pop()

        self.jugar_cpu()
        self.terminado = True
        self.seleccionadas.clear()

        puntos_jugador, nombre_jugador = evaluar(self.jugador)
        puntos_cpu, nombre_cpu = evaluar(self.cpu)

        self.info_cpu.config(text=f"Mano rival: {nombre_cpu}")

        if puntos_jugador > puntos_cpu:
            self.victorias += 1
            mensaje = "¡GANASTE! 🏆"
        elif puntos_jugador < puntos_cpu:
            self.derrotas += 1
            mensaje = "PERDISTE"
        else:
            self.empates += 1
            mensaje = "¡EMPATE!"

        self.resultado.config(text=mensaje)
        self.boton_cambiar.config(state="disabled")
        self.actualizar_cartas()
        self.actualizar_marcador()

    def actualizar_marcador(self):
        self.marcador.config(
            text=(
                f"Victorias: {self.victorias}     "
                f"Derrotas: {self.derrotas}     "
                f"Empates: {self.empates}"
            )
        )


if __name__ == "__main__":
    ventana = tk.Tk()
    Poker(ventana)
    ventana.mainloop()
