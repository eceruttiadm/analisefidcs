import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

    # Taxas negociação
    tx_med = getf(root, "TX_MEDIO")
    tx_min = getf(root, "TX_MIN")
    tx_max = getf(root, "TX_MAXIMO")

    # Índices calculados
    inad_rate_cred = (cred_inad_venc / cred_adimpl * 100) if cred_adimpl > 0 else 0
    inad_rate_dicred = (dicred_inad_venc / dicred_total * 100) if dicred_total > 0 else 0
    cobertura_cred = (cred_provis / cred_inad * 100) if cred_inad > 0 else 0
    cobertura_dicred = (dicred_provis / dicred_inad * 100) if dicred_inad > 0 else 0
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Resumo", "📉 Inadimplência", "📅 Vencimentos", "🧩 Carteira", "💼 Cotas & Negócios"
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

    if d["tx_med"] or d["tx_min"] or d["tx_max"]:
        st.markdown("---")
        st.subheader("Taxas de Negociação")
        c1, c2, c3 = st.columns(3)
        c1.metric("Taxa Mínima", fmt_pct(d["tx_min"]) if d["tx_min"] else "—")
        c2.metric("Taxa Média", fmt_pct(d["tx_med"]) if d["tx_med"] else "—")
        c3.metric("Taxa Máxima", fmt_pct(d["tx_max"]) if d["tx_max"] else "—")

# ─── footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Dados extraídos do Informe Periódico de FIDC — CVM. Versão do layout: " + d["info"]["versao"])
