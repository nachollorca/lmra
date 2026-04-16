"""Entry point: navigation, sidebar, session_state init."""

import streamlit as st
from base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from lmra.agent import State

MODELS = [
    "vertex:gemini-3-flash-preview",
    "vertex:gemini-2.5-flash",
    "mistral:mistral-large-2512",
    "mistral:mistral-small-2603",
    "anthropic:claude-opus-4-6",
    "anthropic:claude-haiku-4-5",
]

# ── Session state defaults ──────────────────────────────────────────────────

if "state" not in st.session_state:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    state = State(session=Session(engine))
    st.session_state.state = state

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

if "model" not in st.session_state:
    st.session_state.model = MODELS[0]

# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.session_state.model = st.selectbox(
        "Model", MODELS, index=MODELS.index(st.session_state.model)
    )

    if st.button("New Chat", width="stretch"):
        st.session_state.state.messages.clear()
        st.session_state.state.namespace.clear()
        st.session_state.chat_log.clear()
        st.rerun()

# ── Navigation ──────────────────────────────────────────────────────────────

chat_page = st.Page("chat.py", title="Chat", icon=":material/chat:", default=True)
db_page = st.Page("viewer.py", title="Viewer", icon=":material/database:")

pg = st.navigation([chat_page, db_page])
pg.run()
