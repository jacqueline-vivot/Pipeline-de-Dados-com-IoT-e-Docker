"""Dashboard que consulta exclusivamente as três views no PostgreSQL."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text
from src.database import get_engine

st.set_page_config(page_title="Observatório IoT", page_icon="🌡️", layout="wide")
st.title("Observatório IoT")
st.caption("Temperatura • ambiente interno e externo • dados históricos do Kaggle")


@st.cache_data(ttl=60)
def load_data():
    engine = get_engine()
    with engine.connect() as conn:
        return tuple(pd.read_sql(text(f"SELECT * FROM {view}"), conn) for view in (
            "avg_temp_por_dispositivo", "leituras_por_hora", "temp_max_min_por_dia"))


try:
    avg, hourly, daily = load_data()
except Exception:
    st.error("Não foi possível consultar o PostgreSQL. Confira a configuração e execute o pipeline primeiro.")
    st.stop()
if avg.empty:
    st.info("Nenhuma leitura disponível. Execute o pipeline com o CSV do Kaggle.")
    st.stop()
locations = st.sidebar.multiselect("Ambiente", ["In", "Out"], default=["In", "Out"])
st.sidebar.caption("In = interno · Out = externo. Os filtros afetam todos os gráficos.")
if st.sidebar.button("Atualizar dados"):
    st.cache_data.clear()
    st.rerun()
avg, hourly, daily = [df[df.location.isin(locations)].copy() for df in (avg, hourly, daily)]
if avg.empty:
    st.info("Selecione pelo menos um ambiente.")
    st.stop()
a, b, c = st.columns(3)
a.metric("Leituras", f"{avg.leituras.sum():,}".replace(",", "."))
b.metric("Temperatura média", f"{(avg.avg_temp * avg.leituras).sum() / avg.leituras.sum():.1f} °C")
c.metric("Faixa observada", f"{daily.temp_min.min():.0f} a {daily.temp_max.max():.0f} °C")
colors = {"In": "#2563eb", "Out": "#f97316"}
st.subheader("01 · Média por identificador de ambiente")
st.caption("room_id/id é o identificador disponível; a base não fornece um ID físico de sensor.")
st.plotly_chart(px.bar(avg, x="device_id", y="avg_temp", color="location", barmode="group",
    color_discrete_map=colors, labels={"device_id": "Identificador", "avg_temp": "Média (°C)", "location": "Ambiente"}), width="stretch")
st.subheader("02 · Volume de leituras por hora do dia")
st.caption("Contagem acumulada em todo o período; não representa uma série de 24 horas consecutivas.")
st.plotly_chart(px.line(hourly.sort_values("hora"), x="hora", y="contagem", color="location", markers=True,
    color_discrete_map=colors, labels={"hora": "Hora do dia", "contagem": "Leituras", "location": "Ambiente"}), width="stretch")
st.subheader("03 · Variação diária da temperatura")
long = daily.sort_values("data").melt(id_vars=["data", "location"], value_vars=["temp_max", "temp_min"], var_name="Medida", value_name="Temperatura (°C)")
st.plotly_chart(px.line(long, x="data", y="Temperatura (°C)", color="location", line_dash="Medida",
    color_discrete_map=colors, labels={"data": "Data", "location": "Ambiente"}), width="stretch")
with st.expander("Consultar os dados agregados"):
    st.dataframe(daily, hide_index=True)
    st.download_button("Baixar resumo diário", daily.to_csv(index=False), "resumo_diario.csv", "text/csv")
st.caption("Análise descritiva de dados históricos. Não há predição por IA nem coleta ao vivo nesta versão.")
