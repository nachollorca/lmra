"""Chat page — talk to the lmra agent with live signal feedback."""

import streamlit as st
from base import Base
from lmdk import AssistantMessage, UserMessage

from lmra.agent import Output, Signal, run

SIGNAL_LABELS = {
    Signal.COMPLETION: ":material/lightbulb: Thinking…",
    Signal.VALIDATION: ":material/approval: Validating code…",
    Signal.EXECUTION: ":material/bolt: Executing code…",
    Signal.EXCEEDED: ":material/warning: Loop limit reached",
}

AVATARS = {
    "user": ":material/person:",
    "assistant": ":material/robot_2:",
    "system": ":material/settings:",
}


def _render_and_log(kind: str, text: str) -> None:
    chat_log.append({"kind": kind, "text": text})
    st.chat_message(kind, avatar=AVATARS.get(kind)).markdown(text)


st.header(":material/chat: Chat")
chat_log: list[dict] = st.session_state.chat_log
state = st.session_state.state
model = st.session_state.model

for entry in chat_log:
    st.chat_message(entry["kind"], avatar=AVATARS.get(entry["kind"])).markdown(entry["text"])

if prompt := st.chat_input("Message the agent…"):
    _render_and_log("user", prompt)
    state.messages.append(UserMessage(prompt))

    status = st.empty()
    status.info(":material/lightbulb: Thinking…")

    gen = run(state=state, base=Base, model=model)
    try:
        while True:
            event = next(gen)

            if isinstance(event, Signal):
                status.info(SIGNAL_LABELS[event])

            elif isinstance(event, AssistantMessage):
                output = Output.model_validate_json(event.content)
                md = output.message
                if output.code:
                    md += f"\n\n```python\n{output.code}\n```"
                status.empty()
                _render_and_log("assistant", md)
                status = st.empty()

            elif isinstance(event, UserMessage):
                status.empty()
                _render_and_log("system", f"```\n{event.content}\n```")
                status = st.empty()

    except StopIteration as exc:
        st.session_state.state = exc.value

    status.empty()
