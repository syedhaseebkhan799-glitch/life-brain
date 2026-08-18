"""
Life Brain — a private chatbot about one person's own life documents.

Three screens, in the order they have to happen:

  1. Privacy policy and the do-not-share warning. Shown before a file picker
     exists, because consent after the upload is not consent.
  2. Dashboard — build the life profile two ways: upload files in whatever form
     they are kept (markdown, text, PDF, Word, CSV, JSON), or paste text
     straight in. Most of what a person wants to ask about is a paragraph they
     can paste, not a file they have lying around.
  3. Chat — ask questions, grounded only in what was provided, answered as the
     words arrive, with the whole conversation downloadable as a file.

Nothing is stored. The profile lives in the browser session and is gone when the
tab closes. See src/privacy.py.
"""
import hashlib

import streamlit as st

from src import brain, config, documents, privacy, theme

st.set_page_config(page_title="Life Brain", page_icon="🧬", layout="wide")
theme.inject()

PROFILE_KEY = "life_profile"
REPORT_KEY = "life_report"
HISTORY_KEY = "life_history"
FILENAMES_KEY = "life_filenames"
PASTED_KEY = "life_pasted"
SIGNATURE_KEY = "life_signature"
PENDING_KEY = "life_pending_question"
MODEL_KEY = "life_model"
STYLE_KEY = "life_style"

# Carries a suffix because it goes through the same reader as an uploaded file,
# and that reader refuses anything it does not recognise by extension.
PASTED_NAME = "pasted-text.md"

for key, default in ((HISTORY_KEY, []), (PROFILE_KEY, ""), (PASTED_KEY, ""),
                     (FILENAMES_KEY, []), (SIGNATURE_KEY, ())):
    st.session_state.setdefault(key, default)


# --- Gate: nothing else renders until the policy is accepted ----------------

if not privacy.gate():
    st.stop()


def _clear_profile():
    """Forget the built profile. Deliberately does not touch the paste box.

    Streamlit refuses a write to a widget's key once that widget has been drawn,
    and this is called from below the paste box as well as from the rail above
    it. The box is emptied by its own buttons, which both run first.
    """
    for key in (PROFILE_KEY, REPORT_KEY, FILENAMES_KEY, SIGNATURE_KEY):
        st.session_state.pop(key, None)
    st.session_state[PROFILE_KEY] = ""
    st.session_state[FILENAMES_KEY] = []
    st.session_state[SIGNATURE_KEY] = ()


def _plural(count: int, word: str = "source") -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def _signature(sources) -> tuple:
    """What the profile was built from, as something comparable.

    Names alone are not enough: editing the pasted text, or re-uploading a
    corrected file under the same name, has to count as a change or the person
    keeps getting answers from the version they replaced.
    """
    return tuple(
        (name, hashlib.sha256(data).hexdigest()) for name, data in sources
    )


# --- Rail --------------------------------------------------------------------

with st.sidebar:
    theme.brand("Life Brain", "PRIVATE ASSISTANT")

    profile = st.session_state.get(PROFILE_KEY, "")
    filenames = st.session_state.get(FILENAMES_KEY, [])

    theme.section("Your life profile")
    if profile:
        st.caption(f"{_plural(len(filenames))} · {len(profile):,} characters")
        for name in filenames:
            st.caption(f"· {'Pasted text' if name == PASTED_NAME else name}")
        # The whole profile rides along with every question, so its size is the
        # one number that decides whether the app keeps working. Shown as a bar
        # because "320,000 characters" means nothing without the ceiling.
        used = min(len(profile) / config.MAX_PROFILE_CHARS, 1.0)
        st.progress(used, text=f"{used:.0%} of the size limit")
    else:
        st.caption("Nothing added yet.")

    st.divider()

    theme.section("Answer style")
    st.segmented_control(
        "Answer style",
        list(config.ANSWER_STYLES),
        key=STYLE_KEY,
        default=config.DEFAULT_ANSWER_STYLE,
        required=True,
        label_visibility="collapsed",
        width="stretch",
        help=(
            "How much you want back. **Full detail** is the one for “lay out my "
            "whole life” — it answers under headings, section by section, "
            "instead of in a paragraph."
        ),
    )

    st.divider()

    theme.section("Model")
    st.selectbox(
        "Model",
        list(config.MODEL_CHOICES),
        key=MODEL_KEY,
        format_func=lambda m: config.MODEL_CHOICES.get(m, m),
        label_visibility="collapsed",
        help=(
            "Flash is the free tier's workhorse. Switch to Pro for a question "
            "that needs joining up across a lot of documents — it is slower and "
            "uses the daily quota faster."
        ),
    )

    st.divider()

    theme.section("Session")
    if st.button("Clear the conversation", use_container_width=True):
        st.session_state[HISTORY_KEY] = []
        st.rerun()
    if st.button("Clear everything", use_container_width=True):
        _clear_profile()
        # The rail is drawn before the paste box, so this write lands.
        st.session_state[PASTED_KEY] = ""
        st.session_state[HISTORY_KEY] = []
        st.rerun()
    st.caption(
        "Your files are held in this tab only. Closing or refreshing it "
        "erases them."
    )

    st.divider()
    theme.section("Appearance")
    theme.switch()


# --- Dashboard ---------------------------------------------------------------

theme.page_header("Life Brain", "Dashboard",
                  "Add what you have, then ask it anything.")

theme.note(privacy.WARNING, kind="bad")
st.write("")

upload_tab, paste_tab = st.tabs([":material/upload_file: Upload files",
                                 ":material/edit_note: Paste text"])

with upload_tab:
    uploaded = st.file_uploader(
        "Upload your life profile",
        type=[s.lstrip(".") for s in sorted(config.SUPPORTED_SUFFIXES)],
        accept_multiple_files=True,
        help=(
            "Markdown, text, PDF, Word, CSV or JSON. Add as many files as you "
            "like — a journal, a CV, notes, exported chats."
        ),
    )

with paste_tab:
    # The fastest route in, and often the only one: a person who wants to ask
    # about their own life usually has to write it down first, and telling them
    # to save a .txt file before they can start is a step for nothing.
    #
    # No "use this text" button, on purpose. Streamlit does not send a text
    # area's contents until the box loses focus, so a button beside it reads the
    # value from *before* the typing on the very run it is clicked -- the person
    # types, clicks, and nothing happens. The widget's own commit is the only
    # event that is reliably in step with what is on screen, so that is what the
    # profile is built from.
    st.text_area(
        "Paste anything about yourself",
        key=PASTED_KEY,
        height=220,
        placeholder=(
            "Born in 1996 in Karachi. Studied computer science...\n\n"
            "Anything at all: a bio, a CV pasted in, notes from a journal, a "
            "list of what happened this year."
        ),
        help="Held in this tab like everything else. Nothing is saved to disk.",
    )
    st.caption(
        "Press **Ctrl+Enter**, or click outside the box, to add this to your "
        "profile."
    )
    if st.button("Remove pasted text", use_container_width=True,
                 disabled=not st.session_state.get(PASTED_KEY, "").strip()):
        # Safe to write a widget's own key here: the rerun happens before the
        # text area is drawn again, so it picks the empty value up as its value.
        st.session_state[PASTED_KEY] = ""
        st.rerun()

# Files and pasted text are the same thing once they are text, so they go
# through one pipeline and are reported together.
sources = [(f.name, f.getvalue()) for f in (uploaded or [])]
pasted = st.session_state.get(PASTED_KEY, "").strip()
if pasted:
    sources.append((PASTED_NAME, pasted.encode("utf-8")))

signature = _signature(sources)
if signature != st.session_state.get(SIGNATURE_KEY):
    if sources:
        with st.spinner("Reading what you added..."):
            profile_text, report = documents.build_profile(sources)
        st.session_state[PROFILE_KEY] = profile_text
        st.session_state[REPORT_KEY] = report
        st.session_state[FILENAMES_KEY] = [n for n, _ in sources]
    else:
        _clear_profile()
    st.session_state[SIGNATURE_KEY] = signature
    st.rerun()

report = st.session_state.get(REPORT_KEY)
if report:
    good = [f for f in report["files"] if f["ok"]]
    bad = [f for f in report["files"] if not f["ok"]]

    if good:
        st.success(
            f"Read {_plural(len(good))} — {report['chars']:,} characters of "
            f"life profile."
        )
    for f in bad:
        # Named individually: one unreadable file among five should not look
        # like a general failure, and the person needs to know which one.
        st.error(f"**{f['filename']}** — {f['detail']}")
    if report["truncated"]:
        st.warning(
            f"Your profile is longer than the {config.MAX_PROFILE_CHARS:,} "
            f"character limit, so only the first part is being used. Split it "
            f"or upload the most important files on their own."
        )

st.divider()


# --- Chat --------------------------------------------------------------------

history = st.session_state[HISTORY_KEY]
profile = st.session_state.get(PROFILE_KEY, "")

if not profile:
    theme.note(
        "Add a file or paste some text above, and the chat opens underneath it."
    )
    st.stop()

st.subheader("Ask about your life")

for role, text in history:
    with st.chat_message("user" if role == "You" else "assistant"):
        st.markdown(text)

if not history:
    # Buttons rather than a line of example text: the hardest part of a blank
    # chat box is thinking of the first question, and these ask it for you.
    st.caption("Not sure where to start?")
    # Two columns, not one per starter: these are sentences, and four of them
    # across a desktop width wraps each to four lines of two words.
    for row in range(0, len(config.STARTERS), 2):
        for column, starter in zip(st.columns(2), config.STARTERS[row:row + 2]):
            with column:
                if st.button(starter, use_container_width=True,
                             key=f"starter_{row}_{starter[:20]}"):
                    st.session_state[PENDING_KEY] = starter
                    st.rerun()

typed = st.chat_input("Ask a question about your life profile")
# A starter click and a typed question are the same event from here on. The pop
# is unconditional: `typed or pop(...)` would short-circuit and leave a pending
# starter in state, to fire by itself on some later rerun.
pending = st.session_state.pop(PENDING_KEY, None)
question = typed or pending

if question:
    question = question.strip()[:config.MAX_QUESTION_CHARS]
    with st.chat_message("user"):
        st.markdown(question)

    answer = None
    with st.chat_message("assistant"):
        slot = st.empty()
        pieces = []
        try:
            for piece in brain.stream(
                    profile, question, history=history,
                    model=st.session_state.get(MODEL_KEY),
                    style=st.session_state.get(STYLE_KEY)):
                pieces.append(piece)
                # The block cursor is the only sign that more is coming.
                slot.markdown("".join(pieces) + " ▌")
            answer = "".join(pieces).strip()
            slot.markdown(answer)
        except brain.BrainError as e:
            # Whatever arrived before the failure is kept: half an answer plus
            # the reason it stopped beats losing both.
            if pieces:
                slot.markdown("".join(pieces))
            st.error(str(e))

    if answer:
        history.append(("You", question))
        history.append(("Life Brain", answer))
        st.session_state[HISTORY_KEY] = history[-40:]
        # Redrawn from history on the next run, so the streamed bubble is not
        # left sitting outside the transcript it belongs to.
        st.rerun()

if history:
    st.divider()
    st.download_button(
        ":material/download: Download these questions and answers",
        data=brain.transcript(history),
        file_name="life-brain-answers.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.caption(
        "The download is about you. Keep it as private as the profile itself."
    )
