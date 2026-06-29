import os
from pathlib import Path

import streamlit as st

from lumen.generate import answer
from lumen.ingest import run_ingest

STORAGE_DIR = Path(__file__).resolve().parent / "storage"
DOCS_DIR = Path(__file__).resolve().parent / "docs"

st.set_page_config(page_title="Lumen", page_icon="✨", layout="centered")

# --- Styling -----------------------------------------------------------------
st.markdown(
    """
    <style>
      /* Hide default Streamlit chrome */
      #MainMenu, footer, header {visibility: hidden;}

      .block-container {padding-top: 2.5rem; max-width: 820px;}

      /* Hero */
      .lumen-hero {
        text-align: center;
        margin-bottom: 1.8rem;
      }
      .lumen-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7c5cff 0%, #4dd0e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
      }
      .lumen-subtitle {
        color: #9aa0b4;
        font-size: 1.02rem;
      }

      /* Answer card */
      .answer-card {
        background: #1a1d29;
        border: 1px solid #2a2e3e;
        border-left: 4px solid #7c5cff;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-top: 0.4rem;
        line-height: 1.6;
      }

      /* Source chips */
      .source-chip {
        display: inline-block;
        background: rgba(124, 92, 255, 0.14);
        color: #b9a8ff;
        border: 1px solid rgba(124, 92, 255, 0.35);
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
        font-size: 0.82rem;
        font-family: ui-monospace, monospace;
      }

      .section-label {
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.75rem;
        color: #7c8099;
        margin: 1.1rem 0 0.3rem 0;
      }

      /* Primary button */
      .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7c5cff 0%, #6a4dff 100%);
        border: none;
        font-weight: 600;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Hero --------------------------------------------------------------------
st.markdown(
    """
    <div class="lumen-hero">
      <div class="lumen-title">Lumen ✨</div>
      <div class="lumen-subtitle">
        Busca semântica na sua documentação técnica — respostas fundamentadas, com as fontes.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar: index management ----------------------------------------------
with st.sidebar:
    st.markdown("### 📚 Base de conhecimento")

    indexed = STORAGE_DIR.exists()
    if indexed:
        st.success("Índice pronto")
    else:
        st.warning("Ainda não indexado")

    if DOCS_DIR.exists():
        files = sorted(
            p.name
            for p in DOCS_DIR.rglob("*")
            if p.suffix.lower() in {".md", ".txt", ".pdf", ".docx"}
        )
        st.caption(f"{len(files)} arquivo(s) em docs/")
        for name in files:
            st.markdown(f"<span class='source-chip'>{name}</span>", unsafe_allow_html=True)

    st.divider()
    if st.button("🔄 Reindexar documentação", use_container_width=True):
        with st.spinner("Indexando docs/ no vector store..."):
            run_ingest()
        st.success("Documentação reindexada.")
        st.rerun()

    k = st.slider("Trechos a recuperar (k)", min_value=1, max_value=8, value=4)
    st.caption("Poucos = pode faltar contexto · Muitos = mais ruído e custo")

# --- Main: ask ---------------------------------------------------------------
with st.form("ask-form", clear_on_submit=False):
    question = st.text_input(
        "Sua pergunta",
        placeholder="Ex.: Como funciona a autenticação no SDK da NexaPay?",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Perguntar", type="primary", use_container_width=True)

if submitted and question:
    if not STORAGE_DIR.exists():
        st.error("A documentação ainda não foi indexada. Use 'Reindexar' na barra lateral.")
    else:
        with st.spinner("Buscando na documentação e gerando a resposta..."):
            text, sources = answer(question, k=k)

        st.markdown("<div class='section-label'>Resposta</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='answer-card'>{text}</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-label'>Fontes</div>", unsafe_allow_html=True)
        if sources:
            chips = "".join(
                f"<span class='source-chip'>{os.path.basename(s)}</span>" for s in sources
            )
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.info("Nenhuma fonte citada — a resposta não foi encontrada na documentação.")
elif submitted:
    st.warning("Digite uma pergunta primeiro.")
