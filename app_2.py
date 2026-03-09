import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

st.set_page_config(
    page_title="Análise de FIDC",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Análise de FIDC — CVM")
st.markdown("Faça upload do arquivo XML do informe periódico de FIDC da CVM para visualizar os dados.")

# ─── helpers ──────────────────────────────────────────────────────────────────

def parse_val(v):
    if v is None:
        return 0.0
    try:
        return float(v.replace(".", "").replace(",", "."))
    except:
        return 0.0

def get(root, *tags):
    for tag in tags:
        el = root.find(".//" + tag)
        if el is not None and el.text:
            return el.text.strip()
    return "—"

def getf(root, *tags):
    return parse_val(get(root, *tags))

def fmt_brl(v):
    if v == 0:
        return "R$ 0,00"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(v):
    return f"{v:.2f}%"

# ─── parse ────────────────────────────────────────────────────────────────────

def parse_xml(content):
    root = ET.fromstring(content)

    info = {
        "fundo": get(root, "NM_CLASSE"),
        "cnpj_fundo": get(root, "NR_CNPJ_FUNDO"),
        "cnpj_adm": get(root, "NR_CNPJ_ADM"),
        "competencia": get(root, "DT_COMPT"),
        "condominio": get(root, "TP_CONDOMINIO"),
        "versao": get(root, "VERSAO"),
    }

    # Patrimônio
    patrliq = getf(root, "VL_PATRIM_LIQ")
    patrliq_medio = getf(root, "VL_PATRIM_LIQ_MEDIO")
    carteira = getf(root, "VL_CARTEIRA")
    disponib = getf(root, "VL_DISPONIB")
    passivo = getf(root, "VL_SOM_PASSIV")
    ativo_total = getf(root, "VL_SOM_APLIC_ATIVO")

    # Créditos existentes
    cred_adimpl = getf(root, "VL_CRED_EXISTE_VENC_ADIMPL")
    cred_inad_venc = getf(root, "VL_CRED_EXISTE_VENC_INAD")
    cred_inad = getf(root, "VL_CRED_EXISTE_INAD")
    cred_provis = getf(root, "VL_PROVIS_REDUC_RECUP")
    cred_total_aquis = getf(root, "VL_SOM_DICRED_AQUIS")

    # DICRED (sem aquisição)
    dicred_total = getf(root, "VL_DICRED")
    dicred_cedent = getf(root, "VL_DICRED_CEDENT")
    dicred_inad_venc = getf(root, "VL_DICRED_EXISTE_VENC_INAD")
    dicred_inad = getf(root, "VL_DICRED_EXISTE_INAD")
    dicred_provis = getf(root, "VL_DICRED_PROVIS_REDUC_RECUP")

    # Outros ativos
    titpub = getf(root, "VL_TITPUB_FED")
    valores_mob = getf(root, "VL_SOM_VALORES_MOB")
    aplic_oper = getf(root, "VL_APLIC_OPER_COMPSS")
    outros_ativos = getf(root, "VL_SOM_OUTROS_ATIVOS")

    # Liquidez
    liq_30 = getf(root, "VL_ATIV_LIQDEZ_30")
    liq_60 = getf(root, "VL_ATIV_LIQDEZ_60")
    liq_90 = getf(root, "VL_ATIV_LIQDEZ_90")
    liq_180 = getf(root, "VL_ATIV_LIQDEZ_180")
    liq_360 = getf(root, "VL_ATIV_LIQDEZ_360")
    liq_mais360 = getf(root, "VL_ATIV_LIQDEZ_MAIS_360")

    # Vencimento DICRED sem aquisição
    prazo_sem = {
        "≤30d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_30"),
        "31-60d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_31_60"),
        "61-90d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_61_90"),
        "91-120d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_91_120"),
        "121-150d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_121_150"),
        "151-180d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_151_180"),
        "181-360d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_181_360"),
        ">360d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_361_720"),
    }

    # Inadimplência por faixa - sem aquisição
    inad_sem = {
        "≤30d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_INAD_VENC_30"),
        "31-60d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_INAD_VENC_31_60"),
        "61-90d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_INAD_VENC_61_90"),
        "91-120d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_INAD_VENC_91_120"),
        "121-150d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_INAD_VENC_121_150"),
        "151-180d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_INAD_VENC_151_180"),
        "181-360d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_INAD_VENC_181_360"),
        ">360d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_INAD_VENC_361_720"),
    }

    # Segmento
    segmt = {
        "Comercial": getf(root, "VL_SOM_SEGMT_COMERC"),
        "Serviços": getf(root, "VL_SOM_SEGMT_SERV"),
        "Financeiro": getf(root, "VL_SOM_SEGMT_FINANC"),
        "Agronegócio": getf(root, "VL_AGRONEG"),
        "Setor Público": getf(root, "VL_SOM_SEGMT_SETOR_PUBLIC"),
        "Factoring": getf(root, "VL_SOM_SEGMT_FACT"),
    }

    # Cotas / Cotistas
    qt_cotas = getf(root, "QT_COTAS")
    qt_cotistas = getf(root, "QT_COTISTAS")
    vl_cota = getf(root, "VL_COTA")
    rent_mes = getf(root, "RENT_MES")

    # Captação/Resgate
    capt = getf(root, "CAPT_MES")
    resg = getf(root, "RESG_MES")

    # Aquisições / Alienações DICRED
    qt_aquis = getf(root, "QT_DICRED_AQUIS")
    vl_aquis = getf(root, "VL_DICRED_AQUIS")
    qt_alien = getf(root, "QT_DICRED_ALIEN")
    vl_alien = getf(root, "VL_DICRED_ALIEN")

    # Volume total dos DCs e Recompras
    vl_dc_total     = cred_total_aquis + dicred_total
    qt_recompra     = getf(root, "QT_DICRED_RECOMPRA", "QT_RECOMPRA")
    vl_recompra     = getf(root, "VL_DICRED_RECOMPRA", "VL_RECOMPRA")
    recompra_pct_pl = (vl_recompra / patrliq * 100) if patrliq > 0 else 0
    recompra_pct_dc = (vl_recompra / vl_dc_total * 100) if vl_dc_total > 0 else 0
    # Taxas negociação
    tx_med = getf(root, "TX_MEDIO")
    tx_min = getf(root, "TX_MIN")
    tx_max = getf(root, "TX_MAXIMO")

    # ── Estrutura de Capital ──────────────────────────────────
    # Cotas sênior e subordinada
    vl_cota_senior     = getf(root, "VL_PATRIM_LIQ_SENIOR", "VL_SOM_COTAS_SENIOR")
    vl_cota_mezanino   = getf(root, "VL_PATRIM_LIQ_MEZANINO", "VL_SOM_COTAS_MEZANINO")
    vl_cota_subord     = getf(root, "VL_PATRIM_LIQ_SUBORD", "VL_SOM_COTAS_SUBORD")
    # Alavancagem e cobertura
    alavancagem        = (passivo / patrliq) if patrliq > 0 else 0
    razao_cobertura    = (carteira / passivo) if passivo > 0 else 0
    indice_subord      = (vl_cota_subord / patrliq * 100) if patrliq > 0 else 0

    # ── PDD detalhado ─────────────────────────────────────────
    # PDD total = provisão créditos c/ aquisição + provisão DICRED
    pdd_total          = cred_provis + dicred_provis
    pdd_pct_carteira   = (pdd_total / carteira * 100) if carteira > 0 else 0

    # Vencidos totais (créditos + DICRED, inadimplentes com e sem atraso)
    vencidos_cred      = cred_inad_venc   # vencidos inadimplentes - créditos c/ aquis.
    vencidos_dicred    = dicred_inad_venc  # vencidos inadimplentes - DICRED s/ aquis.
    vencidos_total     = vencidos_cred + vencidos_dicred
    vencidos_pct       = (vencidos_total / carteira * 100) if carteira > 0 else 0

    # Inadimplência líquida (vencidos - PDD) / carteira
    inad_liquida       = max(vencidos_total - pdd_total, 0)
    inad_liquida_pct   = (inad_liquida / carteira * 100) if carteira > 0 else 0

    # Cobertura PDD sobre vencidos
    pdd_cobertura_venc = (pdd_total / vencidos_total * 100) if vencidos_total > 0 else 0

    # ── Cedente: Vencidos + A Vencer ─────────────────────────
    # A vencer do cedente principal = DICRED cedente total - vencidos do cedente
    # O XML reporta o total do cedente; subtraímos vencidos para estimar a vencer
    dicred_cedent_avencer = max(dicred_cedent - dicred_inad_venc, 0)
    cedente_total_exposto = dicred_cedent  # vencidos já estão dentro do dicred_cedent
    cedente_exposto_pct   = (cedente_total_exposto / carteira * 100) if carteira > 0 else 0

    # Vencidos por faixa - com aquisição (COMPMT_DICRED_COM_AQUIS)
    inad_com = {
        "≤30d":    getf(root, "COMPMT_DICRED_COM_AQUIS/VL_INAD_VENC_30"),
        "31-60d":  getf(root, "COMPMT_DICRED_COM_AQUIS/VL_INAD_VENC_31_60"),
        "61-90d":  getf(root, "COMPMT_DICRED_COM_AQUIS/VL_INAD_VENC_61_90"),
        "91-120d": getf(root, "COMPMT_DICRED_COM_AQUIS/VL_INAD_VENC_91_120"),
        "121-150d":getf(root, "COMPMT_DICRED_COM_AQUIS/VL_INAD_VENC_121_150"),
        "151-180d":getf(root, "COMPMT_DICRED_COM_AQUIS/VL_INAD_VENC_151_180"),
        "181-360d":getf(root, "COMPMT_DICRED_COM_AQUIS/VL_INAD_VENC_181_360"),
        ">360d":   getf(root, "COMPMT_DICRED_COM_AQUIS/VL_INAD_VENC_361_720"),
    }

    # A vencer por faixa - sem aquisição
    avencer_sem = {
        "≤30d":    getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_30"),
        "31-60d":  getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_31_60"),
        "61-90d":  getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_61_90"),
        "91-120d": getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_91_120"),
        "121-150d":getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_121_150"),
        "151-180d":getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_151_180"),
        "181-360d":getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_181_360"),
        ">360d":   getf(root, "COMPMT_DICRED_SEM_AQUIS/VL_PRAZO_VENC_361_720"),
    }

    # Prazo médio ponderado estimado (ponto médio de cada faixa em dias)
    pontos_medios = {"≤30d": 15, "31-60d": 45, "61-90d": 75, "91-120d": 105,
                     "121-150d": 135, "151-180d": 165, "181-360d": 270, ">360d": 540}
    soma_ponderada = sum(avencer_sem[f] * pontos_medios[f] for f in avencer_sem)
    soma_total_av  = sum(avencer_sem.values())
    prazo_medio_pond = (soma_ponderada / soma_total_av) if soma_total_av > 0 else 0

    # Giro da carteira = aquisições no mês / saldo médio da carteira
    giro_carteira = (vl_aquis / patrliq_medio) if patrliq_medio > 0 else 0

    # ── Índices calculados (originais) ───────────────────────
    inad_rate_cred     = (cred_inad_venc / cred_adimpl * 100) if cred_adimpl > 0 else 0
    inad_rate_dicred   = (dicred_inad_venc / dicred_total * 100) if dicred_total > 0 else 0
    cobertura_cred     = (cred_provis / cred_inad * 100) if cred_inad > 0 else 0
    cobertura_dicred   = (dicred_provis / dicred_inad * 100) if dicred_inad > 0 else 0
    concentracao_cedente = (dicred_cedent / dicred_total * 100) if dicred_total > 0 else 0

    return {
        "info": info,
        "patrliq": patrliq, "patrliq_medio": patrliq_medio,
        "carteira": carteira, "disponib": disponib,
        "passivo": passivo, "ativo_total": ativo_total,
        "cred_adimpl": cred_adimpl, "cred_inad_venc": cred_inad_venc,
        "cred_inad": cred_inad, "cred_provis": cred_provis,
        "cred_total_aquis": cred_total_aquis,
        "dicred_total": dicred_total, "dicred_cedent": dicred_cedent,
        "dicred_inad_venc": dicred_inad_venc, "dicred_inad": dicred_inad,
        "dicred_provis": dicred_provis,
        "titpub": titpub, "valores_mob": valores_mob,
        "aplic_oper": aplic_oper, "outros_ativos": outros_ativos,
        "liq_30": liq_30, "liq_60": liq_60, "liq_90": liq_90,
        "liq_180": liq_180, "liq_360": liq_360, "liq_mais360": liq_mais360,
        "prazo_sem": prazo_sem, "inad_sem": inad_sem, "segmt": segmt,
        "qt_cotas": qt_cotas, "qt_cotistas": qt_cotistas,
        "vl_cota": vl_cota, "rent_mes": rent_mes,
        "capt": capt, "resg": resg,
        "qt_aquis": qt_aquis, "vl_aquis": vl_aquis,
        "qt_alien": qt_alien, "vl_alien": vl_alien,
        "tx_med": tx_med, "tx_min": tx_min, "tx_max": tx_max,
        "inad_rate_cred": inad_rate_cred, "inad_rate_dicred": inad_rate_dicred,
        "cobertura_cred": cobertura_cred, "cobertura_dicred": cobertura_dicred,
        "concentracao_cedente": concentracao_cedente,
        # novos
        "vl_dc_total": vl_dc_total,
        "qt_recompra": qt_recompra, "vl_recompra": vl_recompra,
        "recompra_pct_pl": recompra_pct_pl, "recompra_pct_dc": recompra_pct_dc,
        "vl_cota_senior": vl_cota_senior, "vl_cota_mezanino": vl_cota_mezanino,
        "vl_cota_subord": vl_cota_subord,
        "alavancagem": alavancagem, "razao_cobertura": razao_cobertura,
        "indice_subord": indice_subord,
        "pdd_total": pdd_total, "pdd_pct_carteira": pdd_pct_carteira,
        "vencidos_cred": vencidos_cred, "vencidos_dicred": vencidos_dicred,
        "vencidos_total": vencidos_total, "vencidos_pct": vencidos_pct,
        "inad_liquida": inad_liquida, "inad_liquida_pct": inad_liquida_pct,
        "pdd_cobertura_venc": pdd_cobertura_venc,
        "dicred_cedent_avencer": dicred_cedent_avencer,
        "cedente_total_exposto": cedente_total_exposto,
        "cedente_exposto_pct": cedente_exposto_pct,
        "inad_com": inad_com, "avencer_sem": avencer_sem,
        "prazo_medio_pond": prazo_medio_pond, "giro_carteira": giro_carteira,
    }


# ─── Upload ───────────────────────────────────────────────────────────────────

uploaded = st.file_uploader(
    "📁 Selecione o arquivo XML do informe periódico (CVM)",
    type=["xml"],
    accept_multiple_files=True,
)

if not uploaded:
    st.info("Aguardando upload do arquivo XML...")
    st.stop()

# Parse todos os arquivos
fundos = []
for f in uploaded:
    try:
        content = f.read()
        d = parse_xml(content)
        d["filename"] = f.name
        fundos.append(d)
    except Exception as e:
        st.error(f"Erro ao processar {f.name}: {e}")

if not fundos:
    st.stop()

# Seletor de fundo se mais de 1
if len(fundos) == 1:
    d = fundos[0]
else:
    nomes = [f["info"]["fundo"] for f in fundos]
    sel = st.selectbox("Selecione o FIDC para análise:", nomes)
    d = next(f for f in fundos if f["info"]["fundo"] == sel)

# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("---")
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown(f"## 🏦 {d['info']['fundo']}")
    st.caption(f"CNPJ: {d['info']['cnpj_fundo']} | Competência: {d['info']['competencia']} | Condomínio: {d['info']['condominio']}")
with col2:
    st.metric("PL do Fundo", fmt_brl(d["patrliq"]))
with col3:
    st.metric("PL Médio", fmt_brl(d["patrliq_medio"]))

# ─── Tabs ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📋 Resumo", "📉 Inadimplência", "📅 Vencimentos", "🧩 Carteira", "💼 Cotas & Negócios",
    "📈 Evolução Temporal", "🔀 Comparativo CMLs", "📥 Importar Excel",
    "🛡️ PDD & Vencidos", "🏗️ Estrutura de Capital"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — RESUMO
# ══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Indicadores Principais")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Carteira Total", fmt_brl(d["carteira"]))
    c2.metric("Ativo Total", fmt_brl(d["ativo_total"]))
    c3.metric("Passivo", fmt_brl(d["passivo"]))
    c4.metric("Disponibilidade", fmt_brl(d["disponib"]))

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Taxa Inad. Créditos", fmt_pct(d["inad_rate_cred"]),
              delta=None, delta_color="inverse")
    c2.metric("Taxa Inad. DICRED", fmt_pct(d["inad_rate_dicred"]),
              delta=None, delta_color="inverse")
    c3.metric("Cobertura Provisão (Créd.)", fmt_pct(d["cobertura_cred"]))
    c4.metric("Cobertura Provisão (DICRED)", fmt_pct(d["cobertura_dicred"]))

    st.markdown("---")
    st.subheader("Composição do Ativo")

    ativo_items = {
        "Créditos c/ Aquisição": d["cred_total_aquis"],
        "DICRED s/ Aquisição": d["dicred_total"],
        "Valores Mobiliários": d["valores_mob"],
        "Títulos Públicos Fed.": d["titpub"],
        "Aplic. Op. Compromissadas": d["aplic_oper"],
        "Outros Ativos": d["outros_ativos"],
    }
    ativo_items = {k: v for k, v in ativo_items.items() if v > 0}

    if ativo_items:
        fig = px.pie(
            names=list(ativo_items.keys()),
            values=list(ativo_items.values()),
            title="Composição do Ativo Total",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    # tabela resumo
    st.subheader("Detalhamento de Créditos")
    rows = [
        ("Créditos c/ Aquisição (total)", fmt_brl(d["cred_total_aquis"])),
        ("  → Adimplentes (vencidos)", fmt_brl(d["cred_adimpl"])),
        ("  → Inadimplentes vencidos", fmt_brl(d["cred_inad_venc"])),
        ("  → Inadimplentes totais", fmt_brl(d["cred_inad"])),
        ("  → Provisão p/ Perdas", fmt_brl(d["cred_provis"])),
        ("DICRED s/ Aquisição (total)", fmt_brl(d["dicred_total"])),
        ("  → Cedente principal", fmt_brl(d["dicred_cedent"])),
        ("  → Inadimplentes vencidos", fmt_brl(d["dicred_inad_venc"])),
        ("  → Inadimplentes totais", fmt_brl(d["dicred_inad"])),
        ("  → Provisão p/ Perdas", fmt_brl(d["dicred_provis"])),
    ]
    df_res = pd.DataFrame(rows, columns=["Item", "Valor"])
    st.dataframe(df_res, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — INADIMPLÊNCIA
# ══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Inadimplência por Faixa de Atraso — DICRED s/ Aquisição")

    inad_df = pd.DataFrame({
        "Faixa": list(d["inad_sem"].keys()),
        "Valor (R$)": list(d["inad_sem"].values()),
    })
    inad_df = inad_df[inad_df["Valor (R$)"] > 0]

    if not inad_df.empty:
        fig = px.bar(
            inad_df, x="Faixa", y="Valor (R$)",
            title="Inadimplência por Faixa de Atraso",
            color="Valor (R$)",
            color_continuous_scale="Reds",
            text_auto=".2s",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        total_inad = inad_df["Valor (R$)"].sum()
        inad_df["% do Total"] = (inad_df["Valor (R$)"] / total_inad * 100).round(2)
        inad_df["Valor (R$)"] = inad_df["Valor (R$)"].apply(fmt_brl)
        inad_df["% do Total"] = inad_df["% do Total"].apply(fmt_pct)
        st.dataframe(inad_df, use_container_width=True, hide_index=True)
    else:
        st.success("Nenhuma inadimplência registrada nesta faixa.")

    st.markdown("---")
    st.subheader("Comparativo: Inadimplência vs Provisão")
    comp = pd.DataFrame({
        "Categoria": ["Créditos c/ Aquisição", "DICRED s/ Aquisição"],
        "Inadimplência Total (R$)": [d["cred_inad"], d["dicred_inad"]],
        "Provisão Constituída (R$)": [d["cred_provis"], d["dicred_provis"]],
    })

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Inadimplência Total", x=comp["Categoria"],
                          y=comp["Inadimplência Total (R$)"], marker_color="#EF4444"))
    fig2.add_trace(go.Bar(name="Provisão Constituída", x=comp["Categoria"],
                          y=comp["Provisão Constituída (R$)"], marker_color="#3B82F6"))
    fig2.update_layout(barmode="group", title="Inadimplência x Provisão")
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — VENCIMENTOS
# ══════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Perfil de Vencimentos — DICRED s/ Aquisição")

    prazo_df = pd.DataFrame({
        "Faixa": list(d["prazo_sem"].keys()),
        "Valor a Vencer (R$)": list(d["prazo_sem"].values()),
    })
    prazo_df = prazo_df[prazo_df["Valor a Vencer (R$)"] > 0]

    if not prazo_df.empty:
        fig = px.bar(
            prazo_df, x="Faixa", y="Valor a Vencer (R$)",
            title="Distribuição de Vencimentos por Prazo",
            color="Valor a Vencer (R$)",
            color_continuous_scale="Blues",
            text_auto=".2s",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        total_venc = prazo_df["Valor a Vencer (R$)"].sum()
        prazo_df["% do Total"] = (prazo_df["Valor a Vencer (R$)"] / total_venc * 100).round(2)
        prazo_df["Valor a Vencer (R$)"] = prazo_df["Valor a Vencer (R$)"].apply(fmt_brl)
        prazo_df["% do Total"] = prazo_df["% do Total"].apply(fmt_pct)
        st.dataframe(prazo_df, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de vencimento disponíveis.")

    st.markdown("---")
    st.subheader("Liquidez dos Ativos")

    liq_data = {
        "≤30d": d["liq_30"], "≤60d": d["liq_60"], "≤90d": d["liq_90"],
        "≤180d": d["liq_180"], "≤360d": d["liq_360"], ">360d": d["liq_mais360"],
    }
    liq_df = pd.DataFrame({
        "Horizonte": list(liq_data.keys()),
        "Valor (R$)": list(liq_data.values()),
    })
    liq_df = liq_df[liq_df["Valor (R$)"] > 0]

    if not liq_df.empty:
        fig_liq = px.line(
            liq_df, x="Horizonte", y="Valor (R$)",
            title="Curva de Liquidez Acumulada", markers=True,
            color_discrete_sequence=["#10B981"],
        )
        st.plotly_chart(fig_liq, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — CARTEIRA
# ══════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Carteira por Segmento")

    segmt_df = pd.DataFrame({
        "Segmento": list(d["segmt"].keys()),
        "Valor (R$)": list(d["segmt"].values()),
    })
    segmt_df = segmt_df[segmt_df["Valor (R$)"] > 0]

    if not segmt_df.empty:
        fig = px.pie(
            segmt_df, names="Segmento", values="Valor (R$)",
            title="Concentração por Segmento da Carteira",
            hole=0.35,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

        total_seg = segmt_df["Valor (R$)"].sum()
        segmt_df["% do Total"] = (segmt_df["Valor (R$)"] / total_seg * 100).round(2)
        segmt_df["Valor (R$)"] = segmt_df["Valor (R$)"].apply(fmt_brl)
        segmt_df["% do Total"] = segmt_df["% do Total"].apply(fmt_pct)
        st.dataframe(segmt_df, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de segmento disponíveis.")

    st.markdown("---")
    st.subheader("Concentração por Cedente Principal")
    c1, c2 = st.columns(2)
    c1.metric("DICRED do Cedente Principal", fmt_brl(d["dicred_cedent"]))
    c2.metric("Concentração no Cedente", fmt_pct(d["concentracao_cedente"]))

    if d["concentracao_cedente"] > 50:
        st.warning("⚠️ Alta concentração no cedente principal (>50%). Risco de concentração elevado.")
    elif d["concentracao_cedente"] > 30:
        st.info("ℹ️ Concentração moderada no cedente principal (>30%).")

# ══════════════════════════════════════════════════════════════
# TAB 5 — COTAS & NEGÓCIOS
# ══════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Cotas e Cotistas")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Qtd. Cotas", f"{d['qt_cotas']:,.0f}" if d['qt_cotas'] else "—")
    c2.metric("Qtd. Cotistas", f"{d['qt_cotistas']:.0f}" if d['qt_cotistas'] else "—")
    c3.metric("Valor da Cota", fmt_brl(d["vl_cota"]) if d["vl_cota"] else "—")
    c4.metric("Rentab. no Mês", fmt_pct(d["rent_mes"]) if d["rent_mes"] else "—")

    st.markdown("---")
    st.subheader("Captação e Resgate no Mês")
    c1, c2 = st.columns(2)
    c1.metric("Captação (R$)", fmt_brl(d["capt"]))
    c2.metric("Resgate (R$)", fmt_brl(d["resg"]))

    net = d["capt"] - d["resg"]
    if net != 0:
        st.metric("Captação Líquida", fmt_brl(net),
                  delta="positivo" if net > 0 else "negativo",
                  delta_color="normal" if net > 0 else "inverse")

    st.markdown("---")
    st.subheader("Aquisições e Alienações de DICRED")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Qtd. Aquisições", f"{d['qt_aquis']:.0f}" if d['qt_aquis'] else "—")
    c2.metric("Vol. Aquisições", fmt_brl(d["vl_aquis"]))
    c3.metric("Qtd. Alienações", f"{d['qt_alien']:.0f}" if d['qt_alien'] else "—")
    c4.metric("Vol. Alienações", fmt_brl(d["vl_alien"]))

    st.markdown("---")
    st.subheader("📦 Volume Total de DCs & Recompras")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Volume Total de DCs", fmt_brl(d["vl_dc_total"]),
              help="Créditos c/ Aquisição + DICRED s/ Aquisição")
    c2.metric("Recompras no Mês (R$)", fmt_brl(d["vl_recompra"]))
    c3.metric("Recompras / PL", fmt_pct(d["recompra_pct_pl"]),
              help="Volume de recompras pelo cedente em relação ao PL do fundo")
    c4.metric("Recompras / DCs Totais", fmt_pct(d["recompra_pct_dc"]),
              help="Volume de recompras em relação ao total da carteira de DCs")

    if d["vl_recompra"] > 0:
        if d["recompra_pct_pl"] > 10:
            st.warning(f"⚠️ Recompras representam {d['recompra_pct_pl']:.1f}% do PL — volume relevante de devolução ao cedente.")
        else:
            st.info(f"ℹ️ Recompras no mês: {fmt_brl(d['vl_recompra'])} ({fmt_pct(d['recompra_pct_pl'])} do PL).")
    else:
        st.success("✅ Sem recompras registradas neste período.")

    if d["tx_med"] or d["tx_min"] or d["tx_max"]:
        st.markdown("---")
        st.subheader("Taxas de Negociação")
        c1, c2, c3 = st.columns(3)
        c1.metric("Taxa Mínima", fmt_pct(d["tx_min"]) if d["tx_min"] else "—")
        c2.metric("Taxa Média", fmt_pct(d["tx_med"]) if d["tx_med"] else "—")
        c3.metric("Taxa Máxima", fmt_pct(d["tx_max"]) if d["tx_max"] else "—")

# ══════════════════════════════════════════════════════════════
# TAB 6 — EVOLUÇÃO TEMPORAL (múltiplos meses via XML)
# ══════════════════════════════════════════════════════════════
with tab6:
    st.subheader("📈 Evolução Temporal — Múltiplos Meses")

    if len(fundos) < 2:
        st.info("💡 Faça upload de **múltiplos arquivos XML** (um por mês) para visualizar a evolução temporal. Cada arquivo representa uma competência diferente.")
    else:
        # Filtra fundos com o mesmo CNPJ (mesmo FIDC, meses diferentes)
        cnpj_atual = d["info"]["cnpj_fundo"]
        serie = [f for f in fundos if f["info"]["cnpj_fundo"] == cnpj_atual]
        serie_sorted = sorted(serie, key=lambda x: x["info"]["competencia"])

        if len(serie_sorted) < 2:
            st.warning("Todos os arquivos parecem ser de FIDCs diferentes. Para série temporal, envie múltiplos meses do mesmo fundo.")
        else:
            competencias = [s["info"]["competencia"] for s in serie_sorted]

            df_serie = pd.DataFrame({
                "Competência": competencias,
                "PL (R$)": [s["patrliq"] for s in serie_sorted],
                "Carteira (R$)": [s["carteira"] for s in serie_sorted],
                "Taxa Inad. Créditos (%)": [s["inad_rate_cred"] for s in serie_sorted],
                "Taxa Inad. DICRED (%)": [s["inad_rate_dicred"] for s in serie_sorted],
                "Cobertura Provisão Créd. (%)": [s["cobertura_cred"] for s in serie_sorted],
                "Cobertura Provisão DICRED (%)": [s["cobertura_dicred"] for s in serie_sorted],
                "Captação (R$)": [s["capt"] for s in serie_sorted],
                "Resgate (R$)": [s["resg"] for s in serie_sorted],
                "Rentabilidade (%)": [s["rent_mes"] for s in serie_sorted],
                "Conc. Cedente (%)": [s["concentracao_cedente"] for s in serie_sorted],
            })

            indicador = st.selectbox("Selecione o indicador para visualizar:", [
                "PL (R$)", "Carteira (R$)", "Taxa Inad. Créditos (%)", "Taxa Inad. DICRED (%)",
                "Cobertura Provisão Créd. (%)", "Cobertura Provisão DICRED (%)",
                "Captação (R$)", "Resgate (R$)", "Rentabilidade (%)", "Conc. Cedente (%)"
            ])

            is_pct = "(%)" in indicador
            fig_t = px.line(
                df_serie, x="Competência", y=indicador,
                title=f"Evolução: {indicador}",
                markers=True,
                color_discrete_sequence=["#3B82F6"],
            )
            fig_t.update_traces(line_width=2.5)
            st.plotly_chart(fig_t, use_container_width=True)

            st.markdown("---")
            st.subheader("Tabela Completa — Série Histórica")
            st.dataframe(df_serie, use_container_width=True, hide_index=True)

            # Download
            csv = df_serie.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar série histórica (.csv)", csv, "serie_historica.csv", "text/csv")

# ══════════════════════════════════════════════════════════════
# TAB 7 — COMPARATIVO CMLs (múltiplos FIDCs)
# ══════════════════════════════════════════════════════════════
with tab7:
    st.subheader("🔀 Comparativo entre CMLs / FIDCs")

    if len(fundos) < 2:
        st.info("💡 Faça upload de **múltiplos arquivos XML** de FIDCs diferentes para comparar indicadores entre eles.")
    else:
        # Agrupa por CNPJ, pega o mais recente de cada
        cnpjs_vistos = {}
        for f in fundos:
            cnpj = f["info"]["cnpj_fundo"]
            if cnpj not in cnpjs_vistos:
                cnpjs_vistos[cnpj] = f
            else:
                if f["info"]["competencia"] > cnpjs_vistos[cnpj]["info"]["competencia"]:
                    cnpjs_vistos[cnpj] = f

        lista_cmls = list(cnpjs_vistos.values())
        nomes_cmls = [f["info"]["fundo"] for f in lista_cmls]

        if len(lista_cmls) < 2:
            st.warning("Todos os arquivos são do mesmo FIDC. Envie XMLs de FIDCs distintos para comparar.")
        else:
            df_comp = pd.DataFrame({
                "FIDC / CML": nomes_cmls,
                "Competência": [f["info"]["competencia"] for f in lista_cmls],
                "PL (R$)": [f["patrliq"] for f in lista_cmls],
                "Carteira (R$)": [f["carteira"] for f in lista_cmls],
                "Taxa Inad. Créditos (%)": [round(f["inad_rate_cred"], 2) for f in lista_cmls],
                "Taxa Inad. DICRED (%)": [round(f["inad_rate_dicred"], 2) for f in lista_cmls],
                "Cobertura Provisão (%)": [round(f["cobertura_cred"], 2) for f in lista_cmls],
                "Rentabilidade (%)": [round(f["rent_mes"], 2) for f in lista_cmls],
                "Conc. Cedente (%)": [round(f["concentracao_cedente"], 2) for f in lista_cmls],
                "Captação Líquida (R$)": [f["capt"] - f["resg"] for f in lista_cmls],
            })

            indicador_comp = st.selectbox("Indicador para comparar:", [
                "PL (R$)", "Carteira (R$)", "Taxa Inad. Créditos (%)", "Taxa Inad. DICRED (%)",
                "Cobertura Provisão (%)", "Rentabilidade (%)", "Conc. Cedente (%)", "Captação Líquida (R$)"
            ], key="comp_indicador")

            fig_c = px.bar(
                df_comp, x="FIDC / CML", y=indicador_comp,
                title=f"Comparativo: {indicador_comp}",
                color="FIDC / CML",
                text_auto=".2s",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_c.update_layout(showlegend=False)
            st.plotly_chart(fig_c, use_container_width=True)

            st.markdown("---")
            st.subheader("Tabela Comparativa Completa")
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

            # Ranking
            st.markdown("---")
            st.subheader("🏆 Ranking por Indicador")
            rank_ind = st.selectbox("Ordenar por:", [
                "PL (R$)", "Rentabilidade (%)", "Taxa Inad. Créditos (%)", "Taxa Inad. DICRED (%)",
                "Cobertura Provisão (%)", "Captação Líquida (R$)"
            ], key="rank_ind")

            asc = "Inad" in rank_ind or "Conc" in rank_ind
            df_rank = df_comp[["FIDC / CML", rank_ind]].sort_values(rank_ind, ascending=asc).reset_index(drop=True)
            df_rank.index += 1
            df_rank.index.name = "Posição"
            st.dataframe(df_rank, use_container_width=True)

            csv_comp = df_comp.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar comparativo (.csv)", csv_comp, "comparativo_cmls.csv", "text/csv")

# ══════════════════════════════════════════════════════════════
# TAB 8 — IMPORTAR EXCEL
# ══════════════════════════════════════════════════════════════
with tab8:
    st.subheader("📥 Importar Dados Complementares via Excel")
    st.markdown("""
    Carregue uma planilha Excel com dados complementares (ex: indicadores internos, metas, benchmarks).
    
    **Formato esperado:** A primeira linha deve conter os cabeçalhos. Colunas sugeridas:
    - `CML` ou `FIDC` — nome do fundo/CML
    - `Mês` ou `Competência` — período de referência
    - Demais colunas = indicadores (valores numéricos)
    """)

    excel_file = st.file_uploader("📊 Selecione o arquivo Excel (.xlsx ou .xls)", type=["xlsx", "xls"], key="excel_upload")

    if excel_file:
        try:
            xl = pd.ExcelFile(excel_file)
            abas = xl.sheet_names
            aba_sel = st.selectbox("Selecione a aba da planilha:", abas)
            df_excel = xl.parse(aba_sel)

            st.success(f"✅ Planilha carregada: {df_excel.shape[0]} linhas × {df_excel.shape[1]} colunas")
            st.markdown("---")

            # Preview
            st.subheader("👁️ Preview dos Dados")
            st.dataframe(df_excel.head(20), use_container_width=True)

            colunas = df_excel.columns.tolist()
            col_numericas = df_excel.select_dtypes(include="number").columns.tolist()

            st.markdown("---")
            st.subheader("📊 Análise dos Indicadores")

            # Detecta coluna de CML/FIDC
            col_cml = st.selectbox("Coluna de CML / FIDC (agrupador):", ["(nenhuma)"] + colunas, key="col_cml")
            col_mes = st.selectbox("Coluna de Mês / Competência (eixo X):", ["(nenhuma)"] + colunas, key="col_mes")
            col_ind = st.selectbox("Indicador para visualizar:", col_numericas if col_numericas else colunas, key="col_ind")

            if col_ind:
                st.markdown("---")
                # Gráfico por mês (série temporal)
                if col_mes != "(nenhuma)" and col_cml != "(nenhuma)":
                    st.subheader(f"Evolução de '{col_ind}' por CML ao longo do tempo")
                    fig_xl = px.line(
                        df_excel, x=col_mes, y=col_ind, color=col_cml,
                        markers=True,
                        title=f"{col_ind} por {col_cml} ao longo do tempo",
                        color_discrete_sequence=px.colors.qualitative.Vivid,
                    )
                    st.plotly_chart(fig_xl, use_container_width=True)

                    # Comparativo entre CMLs (barras)
                    st.subheader(f"Comparativo entre CMLs — '{col_ind}'")
                    df_agg = df_excel.groupby(col_cml)[col_ind].mean().reset_index()
                    df_agg.columns = [col_cml, f"Média de {col_ind}"]
                    fig_bar = px.bar(
                        df_agg, x=col_cml, y=f"Média de {col_ind}",
                        color=col_cml,
                        title=f"Média de '{col_ind}' por CML",
                        text_auto=".2f",
                        color_discrete_sequence=px.colors.qualitative.Safe,
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)

                elif col_mes != "(nenhuma)":
                    st.subheader(f"Evolução de '{col_ind}' ao longo do tempo")
                    fig_xl = px.line(
                        df_excel, x=col_mes, y=col_ind,
                        markers=True,
                        title=f"Evolução: {col_ind}",
                        color_discrete_sequence=["#3B82F6"],
                    )
                    st.plotly_chart(fig_xl, use_container_width=True)

                elif col_cml != "(nenhuma)":
                    st.subheader(f"Comparativo de '{col_ind}' entre CMLs")
                    fig_xl = px.bar(
                        df_excel, x=col_cml, y=col_ind, color=col_cml,
                        title=f"{col_ind} por CML",
                        text_auto=".2f",
                        color_discrete_sequence=px.colors.qualitative.Safe,
                    )
                    fig_xl.update_layout(showlegend=False)
                    st.plotly_chart(fig_xl, use_container_width=True)

                else:
                    st.subheader(f"Distribuição de '{col_ind}'")
                    fig_xl = px.histogram(
                        df_excel, x=col_ind,
                        title=f"Distribuição: {col_ind}",
                        color_discrete_sequence=["#6366F1"],
                    )
                    st.plotly_chart(fig_xl, use_container_width=True)

                # Estatísticas descritivas
                st.markdown("---")
                st.subheader("📐 Estatísticas Descritivas")
                if col_numericas:
                    st.dataframe(df_excel[col_numericas].describe().T.round(2), use_container_width=True)

                # Múltiplos indicadores
                if len(col_numericas) > 1:
                    st.markdown("---")
                    st.subheader("📊 Múltiplos Indicadores — Visão Geral")
                    inds_sel = st.multiselect("Selecione indicadores para comparar:", col_numericas, default=col_numericas[:min(3, len(col_numericas))])
                    if inds_sel and col_mes != "(nenhuma)":
                        df_melt = df_excel[[col_mes] + inds_sel].melt(id_vars=col_mes, var_name="Indicador", value_name="Valor")
                        fig_multi = px.line(
                            df_melt, x=col_mes, y="Valor", color="Indicador",
                            title="Evolução de Múltiplos Indicadores",
                            markers=True,
                        )
                        st.plotly_chart(fig_multi, use_container_width=True)

            # Download como CSV
            st.markdown("---")
            csv_xl = df_excel.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar dados como CSV", csv_xl, "dados_excel.csv", "text/csv")

        except Exception as e:
            st.error(f"Erro ao ler o Excel: {e}")
    else:
        st.info("Aguardando upload do arquivo Excel...")

# ══════════════════════════════════════════════════════════════
# TAB 9 — PDD & VENCIDOS
# ══════════════════════════════════════════════════════════════
with tab9:
    st.subheader("🛡️ PDD — Provisão para Devedores Duvidosos")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PDD Total (Créd. + DICRED)", fmt_brl(d["pdd_total"]))
    c2.metric("PDD / Carteira", fmt_pct(d["pdd_pct_carteira"]))
    c3.metric("PDD Créditos c/ Aquis.", fmt_brl(d["cred_provis"]))
    c4.metric("PDD DICRED s/ Aquis.", fmt_brl(d["dicred_provis"]))

    st.markdown("---")
    st.subheader("📌 Vencidos Totais")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vencidos — Créd. c/ Aquis.", fmt_brl(d["vencidos_cred"]))
    c2.metric("Vencidos — DICRED s/ Aquis.", fmt_brl(d["vencidos_dicred"]))
    c3.metric("Vencidos Totais", fmt_brl(d["vencidos_total"]))
    c4.metric("Vencidos / Carteira", fmt_pct(d["vencidos_pct"]))

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Inadimplência Líquida (Vencidos − PDD)", fmt_brl(d["inad_liquida"]),
              help="Exposição residual após constituição de PDD")
    c2.metric("Inad. Líquida / Carteira", fmt_pct(d["inad_liquida_pct"]))
    c3.metric("Cobertura PDD / Vencidos", fmt_pct(d["pdd_cobertura_venc"]),
              help="Quanto do saldo vencido está coberto pela provisão")

    if d["pdd_cobertura_venc"] >= 100:
        st.success("✅ PDD cobre 100% dos vencidos — provisão adequada.")
    elif d["pdd_cobertura_venc"] >= 70:
        st.info(f"ℹ️ PDD cobre {d['pdd_cobertura_venc']:.1f}% dos vencidos.")
    elif d["pdd_cobertura_venc"] > 0:
        st.warning(f"⚠️ PDD cobre apenas {d['pdd_cobertura_venc']:.1f}% dos vencidos. Atenção ao risco residual.")

    # Gráfico comparativo PDD x Vencidos
    st.markdown("---")
    st.subheader("Comparativo: PDD vs Vencidos por Carteira")
    fig_pdd = go.Figure()
    categorias = ["Créditos c/ Aquisição", "DICRED s/ Aquisição", "Total Consolidado"]
    vencidos_vals = [d["vencidos_cred"], d["vencidos_dicred"], d["vencidos_total"]]
    pdd_vals      = [d["cred_provis"],    d["dicred_provis"],   d["pdd_total"]]
    fig_pdd.add_trace(go.Bar(name="Vencidos", x=categorias, y=vencidos_vals,
                             marker_color="#EF4444", text=[fmt_brl(v) for v in vencidos_vals],
                             textposition="outside"))
    fig_pdd.add_trace(go.Bar(name="PDD Constituída", x=categorias, y=pdd_vals,
                             marker_color="#3B82F6", text=[fmt_brl(v) for v in pdd_vals],
                             textposition="outside"))
    fig_pdd.update_layout(barmode="group", title="PDD vs Vencidos",
                          yaxis_title="R$", uniformtext_minsize=8)
    st.plotly_chart(fig_pdd, use_container_width=True)

    # Vencidos por faixa (sem aquisição) vs a vencer
    st.markdown("---")
    st.subheader("Vencidos vs A Vencer por Faixa — DICRED s/ Aquisição")
    faixas = list(d["inad_sem"].keys())
    df_faixas = pd.DataFrame({
        "Faixa": faixas,
        "Vencidos (R$)":  [d["inad_sem"][f] for f in faixas],
        "A Vencer (R$)":  [d["avencer_sem"][f] for f in faixas],
    })
    df_faixas_plot = df_faixas[(df_faixas["Vencidos (R$)"] > 0) | (df_faixas["A Vencer (R$)"] > 0)]
    if not df_faixas_plot.empty:
        fig_faixas = go.Figure()
        fig_faixas.add_trace(go.Bar(name="A Vencer", x=df_faixas_plot["Faixa"],
                                    y=df_faixas_plot["A Vencer (R$)"], marker_color="#10B981"))
        fig_faixas.add_trace(go.Bar(name="Vencidos", x=df_faixas_plot["Faixa"],
                                    y=df_faixas_plot["Vencidos (R$)"], marker_color="#EF4444"))
        fig_faixas.update_layout(barmode="stack", title="Composição por Faixa: A Vencer + Vencidos")
        st.plotly_chart(fig_faixas, use_container_width=True)

        df_faixas["Vencidos (R$)"] = df_faixas["Vencidos (R$)"].apply(fmt_brl)
        df_faixas["A Vencer (R$)"] = df_faixas["A Vencer (R$)"].apply(fmt_brl)
        st.dataframe(df_faixas, use_container_width=True, hide_index=True)

    # Cedente: Vencidos + A Vencer
    st.markdown("---")
    st.subheader("👤 Cedente Principal — Vencidos + A Vencer")
    c1, c2, c3 = st.columns(3)
    c1.metric("A Vencer (cedente principal)", fmt_brl(d["dicred_cedent_avencer"]))
    c2.metric("Total Exposto (cedente)", fmt_brl(d["cedente_total_exposto"]))
    c3.metric("Exposição / Carteira", fmt_pct(d["cedente_exposto_pct"]))

    df_cedente = pd.DataFrame({
        "Componente": ["A Vencer", "Vencidos (inadimpl.)"],
        "Valor (R$)": [d["dicred_cedent_avencer"], d["dicred_inad_venc"]],
    })
    df_cedente_plot = df_cedente[df_cedente["Valor (R$)"] > 0]
    if not df_cedente_plot.empty:
        fig_ced = px.pie(df_cedente_plot, names="Componente", values="Valor (R$)",
                         title="Composição da Exposição ao Cedente Principal",
                         color_discrete_map={"A Vencer": "#10B981", "Vencidos (inadimpl.)": "#EF4444"},
                         hole=0.4)
        fig_ced.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_ced, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 10 — ESTRUTURA DE CAPITAL
# ══════════════════════════════════════════════════════════════
with tab10:
    st.subheader("🏗️ Estrutura de Capital do FIDC")

    c1, c2, c3 = st.columns(3)
    c1.metric("Alavancagem (Passivo / PL)", f"{d['alavancagem']:.2f}x",
              help="Quanto de passivo existe para cada R$1 de PL")
    c2.metric("Razão de Cobertura (Carteira / Passivo)", f"{d['razao_cobertura']:.2f}x",
              help="Quanto a carteira cobre o passivo total")
    c3.metric("Índice de Subordinação", fmt_pct(d["indice_subord"]),
              help="% do PL representado pelas cotas subordinadas")

    if d["alavancagem"] > 3:
        st.warning("⚠️ Alavancagem elevada (>3x). Atenção ao risco estrutural.")
    elif d["alavancagem"] > 0:
        st.success(f"✅ Alavancagem em {d['alavancagem']:.2f}x — dentro de parâmetros normais.")

    st.markdown("---")
    st.subheader("Distribuição das Cotas por Classe")
    cotas_dist = {
        "Sênior":      d["vl_cota_senior"],
        "Mezanino":    d["vl_cota_mezanino"],
        "Subordinada": d["vl_cota_subord"],
    }
    cotas_dist = {k: v for k, v in cotas_dist.items() if v > 0}

    if cotas_dist:
        fig_cotas = px.pie(
            names=list(cotas_dist.keys()),
            values=list(cotas_dist.values()),
            title="Composição do PL por Classe de Cota",
            color_discrete_map={"Sênior": "#3B82F6", "Mezanino": "#F59E0B", "Subordinada": "#8B5CF6"},
            hole=0.4,
        )
        fig_cotas.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_cotas, use_container_width=True)

        df_cotas = pd.DataFrame({
            "Classe": list(cotas_dist.keys()),
            "Valor (R$)": list(cotas_dist.values()),
        })
        total_c = df_cotas["Valor (R$)"].sum()
        df_cotas["% do PL"] = (df_cotas["Valor (R$)"] / total_c * 100).round(2).apply(fmt_pct)
        df_cotas["Valor (R$)"] = df_cotas["Valor (R$)"].apply(fmt_brl)
        st.dataframe(df_cotas, use_container_width=True, hide_index=True)
    else:
        st.info("Dados de distribuição por classe de cota não disponíveis neste XML.")
        # Mostra só o PL total
        st.metric("PL Total do Fundo", fmt_brl(d["patrliq"]))

    st.markdown("---")
    st.subheader("Indicadores Operacionais")
    c1, c2, c3 = st.columns(3)
    c1.metric("Prazo Médio Ponderado (carteira)", f"{d['prazo_medio_pond']:.0f} dias",
              help="Estimado pelo ponto médio de cada faixa de vencimento, ponderado pelo saldo")
    c2.metric("Giro da Carteira no Mês", f"{d['giro_carteira']:.2f}x",
              help="Volume de aquisições / PL médio")
    c3.metric("Vol. Aquisições no Mês", fmt_brl(d["vl_aquis"]))

    st.markdown("---")
    st.subheader("Resumo Estrutural")
    resumo_est = [
        ("PL do Fundo", fmt_brl(d["patrliq"])),
        ("Passivo Total", fmt_brl(d["passivo"])),
        ("Carteira Total", fmt_brl(d["carteira"])),
        ("Alavancagem", f"{d['alavancagem']:.2f}x"),
        ("Razão de Cobertura", f"{d['razao_cobertura']:.2f}x"),
        ("Índice de Subordinação", fmt_pct(d["indice_subord"])),
        ("PDD Total", fmt_brl(d["pdd_total"])),
        ("PDD / Carteira", fmt_pct(d["pdd_pct_carteira"])),
        ("Vencidos Totais", fmt_brl(d["vencidos_total"])),
        ("Vencidos / Carteira", fmt_pct(d["vencidos_pct"])),
        ("Inad. Líquida (Venc. − PDD)", fmt_brl(d["inad_liquida"])),
        ("Prazo Médio Ponderado", f"{d['prazo_medio_pond']:.0f} dias"),
        ("Giro da Carteira", f"{d['giro_carteira']:.2f}x"),
        ("Volume Total de DCs", fmt_brl(d["vl_dc_total"])),
        ("Recompras no Mês (R$)", fmt_brl(d["vl_recompra"])),
        ("Recompras / PL", fmt_pct(d["recompra_pct_pl"])),
        ("Recompras / DCs Totais", fmt_pct(d["recompra_pct_dc"])),
    ]
    df_resumo_est = pd.DataFrame(resumo_est, columns=["Indicador", "Valor"])
    st.dataframe(df_resumo_est, use_container_width=True, hide_index=True)

    csv_est = df_resumo_est.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exportar resumo estrutural (.csv)", csv_est, "estrutura_capital.csv", "text/csv")

# ─── footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Dados extraídos do Informe Periódico de FIDC — CVM. Versão do layout: " + d["info"]["versao"])
