"""
The consent gate.

This is the first screen, and it exists because of what the app asks for. A
"life profile" is the single most sensitive document most people own, and the
person uploading it deserves to know where it goes before they choose a file --
not in a footer afterwards.

The warning the brief asks for is here too, and it is the one that matters
most: never send this profile, or the answers built from it, to a stranger. The
risk is not the app. It is someone asking for the file.
"""
import streamlit as st

from . import config, theme

ACCEPTED_KEY = "privacy_accepted"

WARNING = (
    "<b>Never share your life profile — or these answers — with anyone you do "
    "not know.</b><br><br>"
    "A file like this is enough to impersonate you, guess your passwords and "
    "security answers, or convince someone who trusts you that a stranger is "
    "you. Nobody legitimate will ever ask you to send it: not support staff, "
    "not a recruiter, not an app, not someone helpful in a chat. If you are "
    "asked for it, that is the warning sign."
)

POLICY = f"""
### What this app does with your files

**Your files stay in this browser session.** They are held in memory while the
tab is open and are gone the moment you close or refresh it. Nothing is written
to disk, no database, no account, no log of what you uploaded.

**There is no "my documents" to come back to.** That is deliberate. A profile
like this one is safer to re-upload than to leave sitting somewhere.

### What is sent, and where

When you ask a question, your profile text and that question are sent to
**Google's Gemini API** ({config.GEMINI_MODEL}) so it can answer. That is the one
place your data leaves this machine, and it happens only when you ask something.

Google processes it under their API terms. **Free-tier API usage may be reviewed
by humans and used to improve their models** — this matters, so read Google's
current terms before uploading anything you would not want seen. A paid key has
different, stricter terms.

### What is never sent

Your files are never shared with anyone else, never sold, never published, and
never sent anywhere except Google's API to answer your own question.

### Downloads

You can download your questions and answers as a file. Once downloaded it is an
ordinary file on your device — its safety is then in your hands.

### Your responsibility

- Do not upload other people's private information without their agreement.
- Do not use a shared or public computer for this.
- Treat the downloaded transcript as you would the profile itself.
"""


def gate() -> bool:
    """Show the policy until it is accepted. True once the person may proceed.

    Acceptance lives in session state, so it is asked once per session and
    again on every fresh visit -- someone returning to a shared machine should
    see the warning, not a logged-in dashboard.
    """
    if st.session_state.get(ACCEPTED_KEY):
        return True

    theme.brand("Life Brain", "PRIVATE ASSISTANT")
    st.write("")
    st.subheader("Before you upload anything")

    theme.note(WARNING)
    st.write("")
    st.markdown(POLICY)
    st.divider()

    agreed = st.checkbox(
        "I have read this. I understand my profile is sent to Google's Gemini "
        "API to answer my questions, and I will not share it with anyone."
    )
    if st.button("Continue to the dashboard", type="primary", disabled=not agreed):
        st.session_state[ACCEPTED_KEY] = True
        st.rerun()

    if not agreed:
        st.caption("Tick the box to continue.")
    return False
