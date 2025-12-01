#---------------------------------- STREAMLIT APP ----------------------------------#
import streamlit as st
import pandas as pd
import random
import os

# ====== ESTILOS GLOBALES ======
st.markdown(
    """
<style>
h1, h2, h3, h4 {
    color: #0066FF !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================================
# ===================== CLASE JOB SHOP / GREEDY ECT ========================
# ==========================================================================


class JobShopGreedyECT:
    """
    Simula un sistema Job-Shop donde cada trabajo consta de 'elementos_por_trabajo'
    elementos.

    MODO "Greedy ECT":
        Cada elemento se asigna a la máquina donde TERMINA antes.

    MODO "FIFO aleatorio":
        Cada elemento se asigna a una máquina aleatoria.

    rate_mode:
        - "Aleatorio"  -> cada rate(i,j) es 5, 10 o 15 elegido al azar
        - "Fijo 5"     -> todos los rate(i,j) = 5 u/hr
        - "Fijo 10"    -> todos los rate(i,j) = 10 u/hr
        - "Fijo 15"    -> todos los rate(i,j) = 15 u/hr
    """

    def __init__(
        self,
        num_jobs: int,
        num_machines: int,
        elementos_por_trabajo: int,
        rate_mode: str = "Aleatorio",
        sequencing_mode: str = "Greedy ECT",
    ):
        self.num_jobs = num_jobs
        self.num_machines = num_machines
        self.elementos_por_trabajo = elementos_por_trabajo
        self.rate_mode = rate_mode
        self.sequencing_mode = sequencing_mode

        self.rates = None
        self.makespan = None
        self.traza = None

    # ---------------------- generación de rates ---------------------- #
    def _generar_matriz_rates(self) -> pd.DataFrame:
        if self.rate_mode == "Aleatorio":
            def gen_val():
                return random.choice([5.0, 10.0, 15.0])
        elif self.rate_mode == "Fijo 5":
            def gen_val():
                return 5.0
        elif self.rate_mode == "Fijo 10":
            def gen_val():
                return 10.0
        elif self.rate_mode == "Fijo 15":
            def gen_val():
                return 15.0
        else:
            def gen_val():
                return 5.0

        data = [
            [gen_val() for _ in range(self.num_machines)]
            for _ in range(self.num_jobs)
        ]
        cols = [f"M{k+1}" for k in range(self.num_machines)]
        idx = [f"J{j+1}" for j in range(self.num_jobs)]
        return pd.DataFrame(data, index=idx, columns=cols)

    # ---------------------- simulación job-shop ---------------------- #
    def run(self):
        rates = self._generar_matriz_rates()
        carga_maquinas = [0.0 for _ in range(self.num_machines)]
        registros = []
        orden_global = 1

        for j in range(self.num_jobs):
            for e in range(self.elementos_por_trabajo):

                tiempos_fin = []
                tiempos_proc = []
                for m in range(self.num_machines):
                    r = rates.iat[j, m]   # u/hr
                    proc_time = float("inf") if r <= 0 else 1.0 / r
                    tiempos_proc.append(proc_time)
                    tiempos_fin.append(carga_maquinas[m] + proc_time)

                if self.sequencing_mode == "Greedy ECT":
                    mejor_maquina = min(range(self.num_machines),
                                        key=lambda mm: tiempos_fin[mm])
                else:  # FIFO aleatorio
                    mejor_maquina = random.randint(0, self.num_machines - 1)

                inicio = carga_maquinas[mejor_maquina]
                fin = inicio + tiempos_proc[mejor_maquina]
                carga_maquinas[mejor_maquina] = fin

                registros.append(
                    {
                        "Maquina": mejor_maquina + 1,
                        "idTrabajo": j + 1,
                        "idElemento": e + 1,
                        "HoraInicio": round(inicio, 3),
                        "HoraFin": round(fin, 3),
                        "OrdenSecuenciacion": orden_global,
                    }
                )
                orden_global += 1

        makespan = max(carga_maquinas)
        self.makespan = makespan
        self.traza = pd.DataFrame(registros)
        self.rates = rates
        return makespan, self.traza, rates


# ==========================================================================
# ============================= FUNCIONES AUX ==============================
# ==========================================================================


def correr_experimentos(
    n_simulaciones: int,
    usar_aleatorio: bool,
    trabajos_manual: int,
    maquinas_manual: int,
    elementos_fijo: int,
    rate_mode: str,
    carpeta_salida: str,
    sequencing_mode: str,
):

    os.makedirs(carpeta_salida, exist_ok=True)

    makespans = []
    descripciones = []

    for s in range(1, n_simulaciones + 1):

        if usar_aleatorio:
            n_jobs = random.randint(20, 30)
            n_machines = random.randint(3, 5)
            elementos = random.choice([10, 20, 30])
        else:
            n_jobs = trabajos_manual
            n_machines = maquinas_manual
            elementos = elementos_fijo

        simulador = JobShopGreedyECT(
            num_jobs=n_jobs,
            num_machines=n_machines,
            elementos_por_trabajo=elementos,
            rate_mode=rate_mode,
            sequencing_mode=sequencing_mode,
        )

        mk, traza, rates = simulador.run()
        makespans.append(mk)

        ruta = os.path.join(carpeta_salida, f"Sim_{s:02d}.csv")
        traza.to_csv(ruta, index=False)

        descripciones.append(
            f"Sim {s:02d} | Trabajos={n_jobs}, Máquinas={n_machines}, Elem={elementos}, "
            f"Rates={rate_mode}, Regla={sequencing_mode} → Makespan={mk:.3f} h"
        )

    return makespans, descripciones


# ==========================================================================
# ================================ STREAMLIT UI ============================
# ==========================================================================

# 🔵 SOLO CAMBIÉ ESTA LÍNEA
st.title("20 Simulaciones Estocásticas de un Sistema Job-Shop (Monte Carlo)")

st.header("Parámetros")

if "n_trabajos" not in st.session_state:
    st.session_state["n_trabajos"] = 26
if "n_maquinas" not in st.session_state:
    st.session_state["n_maquinas"] = 5
if "n_elementos" not in st.session_state:
    st.session_state["n_elementos"] = 10

col_param, col_resultados = st.columns([2, 3])

with col_param:

    usar_aleatorio = st.checkbox(
        "Usar aleatorio (trabajos, máquinas y elementos)",
        value=False,
    )

    if st.button("Randomizar ahora"):
        st.session_state["n_trabajos"] = random.randint(20, 30)
        st.session_state["n_maquinas"] = random.randint(3, 5)
        st.session_state["n_elementos"] = random.choice([10, 20, 30])

    n_trabajos = st.number_input(
        "N° Trabajos (20–30)",
        min_value=20,
        max_value=30,
        key="n_trabajos",
    )

    opciones_elem = [10, 20, 30]
    valor_actual = st.session_state.get("n_elementos", 10)
    if valor_actual not in opciones_elem:
        valor_actual = 10

    elementos_por_trabajo = st.selectbox(
        "Elementos por trabajo",
        options=opciones_elem,
        index=opciones_elem.index(valor_actual),
    )
    st.session_state["n_elementos"] = elementos_por_trabajo

    n_maquinas = st.number_input(
        "N° Máquinas (3–5)",
        min_value=3,
        max_value=5,
        key="n_maquinas",
    )

    rate_mode = st.selectbox(
        "Rates (u/hr)",
        ["Aleatorio", "Fijo 5", "Fijo 10", "Fijo 15"],
    )

    modo_seq = st.selectbox(
        "Modo de secuenciación",
        ["Greedy ECT", "FIFO aleatorio"],
        index=0,
        help=(
            "Greedy ECT: asigna a la máquina donde termina antes.\n"
            "FIFO aleatorio: asigna cada elemento a una máquina aleatoria."
        ),
    )

    col_b1, col_b2 = st.columns(2)
    ejecutar = col_b1.button("▶ Correr 20 simulaciones")
    limpiar = col_b2.button("Limpiar")

CARPETA_SALIDA = os.path.join(os.getcwd(), "ExamenSims")

if limpiar:
    if "resultados_sim" in st.session_state:
        del st.session_state["resultados_sim"]

if ejecutar:
    makespans, descripciones = correr_experimentos(
        n_simulaciones=20,
        usar_aleatorio=usar_aleatorio,
        trabajos_manual=int(n_trabajos),
        maquinas_manual=int(n_maquinas),
        elementos_fijo=int(elementos_por_trabajo),
        rate_mode=rate_mode,
        carpeta_salida=CARPETA_SALIDA,
        sequencing_mode=modo_seq,
    )

    prom = sum(makespans) / len(makespans)
    mn = min(makespans)
    mx = max(makespans)

    st.session_state["resultados_sim"] = {
        "makespans": makespans,
        "descripciones": descripciones,
        "promedio": prom,
        "min": mn,
        "max": mx,
        "carpeta": CARPETA_SALIDA,
    }

if "resultados_sim" in st.session_state:
    res = st.session_state["resultados_sim"]

    with col_resultados:
        st.subheader("Resultados por simulación")
        for linea in res["descripciones"]:
            st.write(linea)

    st.markdown("---")
    st.write(
        f"**20 simulaciones completadas.**  \n"
        f"**Makespan (horas)** → Prom: {res['promedio']:.3f} | "
        f"Min: {res['min']:.3f} | Máx: {res['max']:.3f}"
    )
    st.write(f"CSVs guardados en: `{res['carpeta']}`")


