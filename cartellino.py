
import streamlit as st
import pandas as pd
from datetime import datetime, time
import io

st.set_page_config(page_title="Controllo Timbrature - Cartellino PL", layout="wide")

st.title("📋 Controllo Timbrature - Cartellino PL")
st.markdown("Form per controllo timbrature giornaliere con calcolo automatico ore contratto e buono pasto")

# CONFIGURAZIONE CONTRATTO
st.sidebar.header("⚙️ Configurazione Contratto")
ore_contratto_str = st.sidebar.text_input("Ore da contratto giornaliere (HH:MM)", "08:00")
soglia_bp_str = st.sidebar.text_input("Soglia buono pasto (HH:MM)", "06:00")
valore_bp = st.sidebar.number_input("Valore buono pasto €", value=8.0, step=0.5)
pausa_min = st.sidebar.number_input("Pausa pranzo (min)", value=0, min_value=0, max_value=120, step=15)
auto_bp = st.sidebar.checkbox("Calcola Buono Pasto automatico", value=True)

def parse_hhmm(s):
    try:
        if not s or s.strip()=="":
            return 0
        s=s.strip()
        if ":" in s:
            h,m = map(int, s.split(":"))
            return h*60+m
        else:
            return int(s)*60
    except:
        return 0

def format_hhmm(minutes):
    if minutes is None:
        return "00:00"
    sign = ""
    if minutes <0:
        sign="-"
        minutes = -minutes
    h = minutes//60
    m = minutes%60
    return f"{sign}{h:02d}:{m:02d}"

ore_contratto_min = parse_hhmm(ore_contratto_str)
soglia_bp_min = parse_hhmm(soglia_bp_str)

# Tabella giorni
giorni = ["01 G","02 V","03 S","04 D","05 L","06 M","07 M","08 G","09 V","10 S","11 D","12 L","13 M","14 M","15 G","16 V","17 S","18 D","19 L","20 M","21 M","22 G","23 V","24 S","25 D","26 L","27 M","28 M","29 G","30 V","31 S"]

# Stato
if "df" not in st.session_state:
    data = []
    for g in giorni:
        mod = "PMFSNL" if "D" in g.split()[1] else "PM001"
        data.append({"GIO":g, "MOD":mod, "E1":"","U1":"","E2":"","U2":"","DOV":format_hhmm(ore_contratto_min) if mod=="PM001" else "00:00", "EFF":"00:00", "DIFF":"00:00", "STR":"00:00", "BP":0, "GIUST":""})
    st.session_state.df = pd.DataFrame(data)

# Aggiorna DOV se cambia contratto
if st.sidebar.button("Applica ore contratto a tutto il mese"):
    for i in range(len(st.session_state.df)):
        mod = st.session_state.df.at[i,"MOD"]
        if mod=="PM001":
            st.session_state.df.at[i,"DOV"]=format_hhmm(ore_contratto_min)
        else:
            st.session_state.df.at[i,"DOV"]="00:00"

st.subheader("📝 Inserisci Entrata/Uscita (formato HH:MM es. 06:52)")

edited = st.data_editor(
    st.session_state.df,
    column_config={
        "GIO": st.column_config.TextColumn("GIO.", disabled=True),
        "MOD": st.column_config.SelectboxColumn("MOD.", options=["PM001","PMFSNL"], required=True),
        "E1": st.column_config.TextColumn("E1"),
        "U1": st.column_config.TextColumn("U1"),
        "E2": st.column_config.TextColumn("E2"),
        "U2": st.column_config.TextColumn("U2"),
        "DOV": st.column_config.TextColumn("DOV (dovuto)"),
        "EFF": st.column_config.TextColumn("EFF (effettivo)", disabled=True),
        "DIFF": st.column_config.TextColumn("-/+", disabled=True),
        "STR": st.column_config.TextColumn("STR", disabled=True),
        "BP": st.column_config.NumberColumn("B.P.", min_value=0, max_value=1, step=1),
        "GIUST": st.column_config.TextColumn("GIUSTIFICATIVI")
    },
    hide_index=True,
    num_rows="fixed",
    height=800,
    key="editor"
)

# Calcolo automatico
def calc_row(row):
    e1 = parse_hhmm(row["E1"])
    u1 = parse_hhmm(row["U1"])
    e2 = parse_hhmm(row["E2"])
    u2 = parse_hhmm(row["U2"])
    eff = 0
    if e1 and u1 and u1>e1:
        eff += u1-e1
    if e2 and u2 and u2>e2:
        eff += u2-e2
    eff = max(0, eff - pausa_min)
    dov = parse_hhmm(row["DOV"])
    diff = eff - dov
    str_min = diff if diff>0 else 0
    
    # Buono pasto
    bp = row["BP"]
    if auto_bp:
        giust = str(row["GIUST"]).lower()
        if "ferie" in giust or "malattia" in giust or "permesso" in giust:
            bp=0
        elif dov==0:
            bp=0
        elif eff >= soglia_bp_min:
            bp=1
        else:
            bp=0
    
    return format_hhmm(eff), format_hhmm(diff) if diff>=0 else f"-{format_hhmm(-diff)}", format_hhmm(str_min), bp

# Applica calcoli
for i in range(len(edited)):
    eff, diff, str_min, bp = calc_row(edited.iloc[i])
    edited.at[i,"EFF"]=eff
    edited.at[i,"DIFF"]=diff
    edited.at[i,"STR"]=str_min
    edited.at[i,"BP"]=bp

st.session_state.df = edited

# Riepilogo
st.divider()
col1,col2,col3,col4,col5 = st.columns(5)
tot_dov = sum(parse_hhmm(x) for x in edited["DOV"])
tot_eff = sum(parse_hhmm(x) for x in edited["EFF"])
tot_str = sum(parse_hhmm(x) for x in edited["STR"])
tot_bp = int(edited["BP"].sum())

with col1:
    st.metric("Totale Dovuto", format_hhmm(tot_dov))
with col2:
    st.metric("Totale Effettivo", format_hhmm(tot_eff))
with col3:
    saldo = tot_eff - tot_dov
    st.metric("Saldo Mese", format_hhmm(saldo) if saldo>=0 else f"-{format_hhmm(-saldo)}")
with col4:
    st.metric("Tot. Straordinari", format_hhmm(tot_str))
with col5:
    st.metric("Buoni Pasto", f"{tot_bp} ( {tot_bp*valore_bp:.2f} € )")

# Export
st.divider()
c1,c2 = st.columns(2)
with c1:
    # Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited.to_excel(writer, index=False, sheet_name="Cartellino")
    st.download_button("📥 Scarica Excel", output.getvalue(), "Cartellino-PL.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with c2:
    csv = edited.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica CSV", csv, "Cartellino-PL.csv", "text/csv")

st.caption("Configura ore contratto a sinistra e inserisci E/U. Il sistema calcola automatico EFF, DIFF, STR e Buono Pasto.")
