

import streamlit as st
import random
from collections import Counter

st.set_page_config(
    page_title="Poker",
    page_icon="🃏",
    layout="centered"
)

PALOS = ["♠", "♥", "♦", "♣"]
VALORES = range(2, 15)


# ==============================
# FUNCIONES DEL JUEGO
# ==============================

def crear_mazo():
    mazo = [(v, p) for p in PALOS for v in VALORES]
    random.shuffle(mazo)
    return mazo


def nombre_carta(carta):
    valor, palo = carta
    figuras = {11: "J", 12: "Q", 13: "K", 14: "A"}
    return f"{figuras.get(valor, valor)}{palo}"


def evaluar(mano):
    valores = sorted((c[0] for c in mano), reverse=True)
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
        return (7, grupos[0][1], grupos[1][1]), "Poker"

    if [g[0] for g in grupos] == [3, 2]:
        return (6, grupos[0][1], grupos[1][1]), "Full House"

    if color:
        return (5, *valores), "Color"

    if escalera:
        return (4, escalera), "Escalera"

    if grupos[0][0] == 3:
        trio = grupos[0][1]
        resto = sorted(
            (v for v in valores if v != trio),
            reverse=True
        )
        return (3, trio, *resto), "Trío"

    pares = sorted(
        (valor for valor, n in conteo.items() if n == 2),
        reverse=True
    )

    if len(pares) == 2:
        otro = next(v for v, n in conteo.items() if n == 1)
        return (2, *pares, otro), "Doble pareja"

    if len(pares) == 1:
        par = pares[0]
        resto = sorted(
            (v for v in valores if v != par),
            reverse=True
        )
        return (1, par, *resto), "Pareja"

    return (0, *valores), "Carta alta"


# ==============================
# ESTADO DE LA PARTIDA
# ==============================

def nueva_partida():
    mazo = crear_mazo()

    jugador = [mazo.pop() for _ in range(5)]
    computadora = [mazo.pop() for _ in range(5)]

    st.session_state.mazo = mazo
    st.session_state.jugador = jugador
    st.session_state.computadora = computadora
    st.session_state.terminado = False
    st.session_state.resultado = ""
    st.session_state.ronda += 1


if "victorias" not in st.session_state:
    st.session_state.victorias = 0
    st.session_state.derrotas = 0
    st.session_state.empates = 0
    st.session_state.ronda = 0
    nueva_partida()


# ==============================
# TURNO DE LA COMPUTADORA
# ==============================

def jugar_computadora():
    mano = st.session_state.computadora
    mazo = st.session_state.mazo

    puntuacion, _ = evaluar(mano)
    categoria = puntuacion[0]

    if categoria >= 4:
        return

    conteo = Counter(c[0] for c in mano)

    if categoria in (1, 2, 3):
        conservar = {
            valor for valor, cantidad in conteo.items()
            if cantidad >= 2
        }

        cambiar = [
            i for i, carta in enumerate(mano)
            if carta[0] not in conservar
        ]

    else:
        conteo_palos = Counter(c[1] for c in mano)
        palo, cantidad = conteo_palos.most_common(1)[0]

        if cantidad == 4:
            cambiar = [
                i for i, carta in enumerate(mano)
                if carta[1] != palo
            ]
        else:
            mejores = sorted(
                range(5),
                key=lambda i: mano[i][0],
                reverse=True
            )[:2]

            cambiar = [
                i for i in range(5)
                if i not in mejores
            ]

    for i in cambiar:
        mano[i] = mazo.pop()


# ==============================
# FINALIZAR RONDA
# ==============================

def finalizar_ronda():
    if st.session_state.terminado:
        return

    ronda = st.session_state.ronda

    for i in range(5):
        clave = f"seleccion_{ronda}_{i}"

        if st.session_state.get(clave, False):
            st.session_state.jugador[i] = (
                st.session_state.mazo.pop()
            )

    jugar_computadora()

    puntos_jugador, _ = evaluar(
        st.session_state.jugador
    )

    puntos_cpu, _ = evaluar(
        st.session_state.computadora
    )

    if puntos_jugador > puntos_cpu:
        st.session_state.victorias += 1
        st.session_state.resultado = "🏆 ¡GANASTE!"

    elif puntos_jugador < puntos_cpu:
        st.session_state.derrotas += 1
        st.session_state.resultado = "❌ PERDISTE"

    else:
        st.session_state.empates += 1
        st.session_state.resultado = "🤝 EMPATE"

    st.session_state.terminado = True


# ==============================
# DISEÑO DE CARTAS
# ==============================

def carta_html(carta=None, oculta=False):
    if oculta:
        return """
        <div class="carta reverso">
            ★
        </div>
        """

    valor = nombre_carta(carta)

    if carta[1] in ["♥", "♦"]:
        color = "#dc2626"
    else:
        color = "#111827"

    return f"""
    <div class="carta" style="color:{color};">
        {valor}
    </div>
    """


st.markdown("""
<style>

.stApp {
    background: #0c542e;
}

h1, h2, h3, p {
    color: white;
}

.carta {
    background: white;
    border: 2px solid #dddddd;
    border-radius: 12px;
    height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 31px;
    font-weight: bold;
    box-shadow: 0 4px 8px #08351c;
}

.reverso {
    background: #223b87;
    color: white;
    border: 3px solid #d9e0ff;
}

div[data-testid="stCheckbox"] label {
    color: white !important;
}

div[data-testid="stButton"] button {
    width: 100%;
    border-radius: 10px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ==============================
# INTERFAZ PRINCIPAL
# ==============================

st.title("♠ PÓKER ONLINE ♥")

st.write("Juega contra la computadora.")

col1, col2, col3 = st.columns(3)

col1.metric(
    "🏆 Victorias",
    st.session_state.victorias
)

col2.metric(
    "❌ Derrotas",
    st.session_state.derrotas
)

col3.metric(
    "🤝 Empates",
    st.session_state.empates
)

st.divider()


# ==============================
# CARTAS DE LA COMPUTADORA
# ==============================

st.subheader("🤖 Computadora")

columnas = st.columns(5)

for i, columna in enumerate(columnas):
    with columna:
        st.markdown(
            carta_html(
                st.session_state.computadora[i],
                oculta=not st.session_state.terminado
            ),
            unsafe_allow_html=True
        )

if st.session_state.terminado:
    _, nombre_cpu = evaluar(
        st.session_state.computadora
    )
    st.write(f"Mano rival: **{nombre_cpu}**")
else:
    st.write("Cartas ocultas")

st.divider()


# ==============================
# CARTAS DEL JUGADOR
# ==============================

st.subheader("🧑 Tus cartas")

columnas = st.columns(5)

for i, columna in enumerate(columnas):
    with columna:
        st.markdown(
            carta_html(st.session_state.jugador[i]),
            unsafe_allow_html=True
        )

        st.checkbox(
            "Cambiar",
            key=f"seleccion_{st.session_state.ronda}_{i}",
            disabled=st.session_state.terminado
        )

_, nombre_jugador = evaluar(
    st.session_state.jugador
)

st.write(f"Tu mano: **{nombre_jugador}**")

st.divider()


# ==============================
# CONTROLES DEL JUEGO
# ==============================

if not st.session_state.terminado:

    st.info(
        "Selecciona las cartas que deseas cambiar. "
        "También puedes jugar sin cambiar ninguna."
    )

    if st.button(
        "🔄 CAMBIAR CARTAS Y JUGAR",
        use_container_width=True,
        type="primary"
    ):
        finalizar_ronda()
        st.rerun()

else:

    resultado = st.session_state.resultado

    if "GANASTE" in resultado:
        st.success(resultado)

    elif "PERDISTE" in resultado:
        st.error(resultado)

    else:
        st.warning(resultado)

if st.button(
    "🃏 NUEVA PARTIDA",
    use_container_width=True
):
    nueva_partida()
    st.rerun()




