# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

"""Shared layout helpers and visual styling for Streamlit pages."""

from __future__ import annotations

from html import escape
from typing import Sequence

import streamlit as st


def inject_global_styles() -> None:
    """Apply a consistent visual theme across the application."""

    if st.session_state.get("_chemease_global_styles_loaded"):
        return

    st.markdown(
        """
        <style>
        :root {
            --chemease-accent: #176b61;
            --chemease-accent-soft: #e7f4f1;
            --chemease-accent-strong: #0f4d46;
            --chemease-surface: rgba(255, 255, 255, 0.86);
            --chemease-surface-strong: #ffffff;
            --chemease-surface-soft: rgba(255, 248, 237, 0.92);
            --chemease-border: #d5e2dd;
            --chemease-border-strong: #bdd3cc;
            --chemease-text: #18332e;
            --chemease-muted: #61746f;
            --chemease-info: #edf7ff;
            --chemease-warn: #fff4df;
            --chemease-danger: #fff0ed;
        }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(23, 107, 97, 0.10), transparent 26%),
                linear-gradient(180deg, #f4efe7 0%, #f8fbfa 28%, #ffffff 100%);
            color: var(--chemease-text);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #193934 0%, #204742 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #eef6f3;
        }

        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p {
            color: #eef6f3;
        }

        div[data-testid="stMetric"] {
            background: var(--chemease-surface);
            border: 1px solid var(--chemease-border);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 12px 30px rgba(24, 51, 46, 0.05);
        }

        div[data-testid="stExpander"] {
            border: 1px solid var(--chemease-border);
            border-radius: 16px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.7);
        }

        div[data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
        }

        div.stButton > button,
        div.stDownloadButton > button {
            border-radius: 999px;
            border: 1px solid var(--chemease-border-strong);
            background: var(--chemease-surface-strong);
            color: var(--chemease-text);
            font-weight: 600;
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--chemease-accent) 0%, var(--chemease-accent-strong) 100%);
            color: #ffffff;
            border-color: transparent;
        }

        .chemease-hero {
            padding: 1.35rem 1.5rem;
            margin-bottom: 1rem;
            border-radius: 24px;
            border: 1px solid rgba(23, 107, 97, 0.14);
            background:
                linear-gradient(140deg, rgba(255, 255, 255, 0.94) 0%, rgba(231, 244, 241, 0.96) 55%, rgba(255, 246, 230, 0.96) 100%);
            box-shadow: 0 16px 38px rgba(24, 51, 46, 0.08);
        }

        .chemease-eyebrow {
            display: inline-block;
            margin-bottom: 0.55rem;
            padding: 0.28rem 0.68rem;
            border-radius: 999px;
            background: rgba(23, 107, 97, 0.1);
            color: var(--chemease-accent-strong);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        .chemease-hero h1 {
            margin: 0;
            color: var(--chemease-text);
            font-size: 2rem;
            line-height: 1.2;
        }

        .chemease-hero p {
            margin: 0.75rem 0 0;
            max-width: 56rem;
            color: var(--chemease-muted);
            font-size: 1rem;
            line-height: 1.7;
        }

        .chemease-card {
            min-height: 100%;
            padding: 1rem 1.05rem;
            border-radius: 20px;
            border: 1px solid var(--chemease-border);
            background: var(--chemease-surface);
            box-shadow: 0 14px 32px rgba(24, 51, 46, 0.05);
        }

        .chemease-card h3 {
            margin: 0 0 0.45rem;
            font-size: 1.02rem;
            color: var(--chemease-text);
        }

        .chemease-card p {
            margin: 0;
            color: var(--chemease-muted);
            line-height: 1.65;
        }

        .chemease-section-title {
            margin: 1.25rem 0 0.4rem;
            color: var(--chemease-text);
            font-size: 1.22rem;
            font-weight: 700;
        }

        .chemease-section-copy {
            margin: 0 0 0.75rem;
            color: var(--chemease-muted);
            line-height: 1.7;
        }

        .chemease-note {
            margin: 0.75rem 0;
            padding: 0.95rem 1rem;
            border-radius: 18px;
            border: 1px solid var(--chemease-border);
            background: var(--chemease-surface);
        }

        .chemease-note h4 {
            margin: 0 0 0.35rem;
            font-size: 0.96rem;
            color: var(--chemease-text);
        }

        .chemease-note p {
            margin: 0;
            color: var(--chemease-muted);
            line-height: 1.7;
        }

        .chemease-note ul {
            margin: 0.45rem 0 0 1.1rem;
            color: var(--chemease-muted);
            line-height: 1.7;
        }

        .chemease-note--info {
            background: var(--chemease-info);
            border-color: #cfe5fb;
        }

        .chemease-note--warn {
            background: var(--chemease-warn);
            border-color: #f0dab3;
        }

        .chemease-note--danger {
            background: var(--chemease-danger);
            border-color: #f0c8c0;
        }

        .chemease-empty {
            margin: 0.8rem 0;
            padding: 1rem 1.1rem;
            border-radius: 18px;
            border: 1px dashed var(--chemease-border-strong);
            background: rgba(255, 255, 255, 0.72);
            color: var(--chemease-muted);
        }

        .chemease-empty strong {
            display: block;
            margin-bottom: 0.3rem;
            color: var(--chemease-text);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["_chemease_global_styles_loaded"] = True


def render_page_header(
    title: str,
    description: str,
    *,
    eyebrow: str = "Chemease",
    steps: Sequence[tuple[str, str]] | None = None,
) -> None:
    """Render a consistent introductory banner for a page."""

    st.markdown(
        (
            '<div class="chemease-hero">'
            f'<div class="chemease-eyebrow">{escape(eyebrow)}</div>'
            f"<h1>{escape(title)}</h1>"
            f"<p>{escape(description)}</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if not steps:
        return

    columns = st.columns(len(steps))
    for column, (step_title, step_description) in zip(columns, steps):
        with column:
            st.markdown(
                (
                    '<div class="chemease-card">'
                    f"<h3>{escape(step_title)}</h3>"
                    f"<p>{escape(step_description)}</p>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


def render_section_header(title: str, description: str | None = None) -> None:
    """Render a section title with optional explanatory copy."""

    st.markdown(f'<div class="chemease-section-title">{escape(title)}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(f'<div class="chemease-section-copy">{escape(description)}</div>', unsafe_allow_html=True)


def render_note(title: str, description: str, *, tone: str = "info", bullets: Sequence[str] | None = None) -> None:
    """Render a concise note box."""

    allowed_tones = {"info", "warn", "danger"}
    note_tone = tone if tone in allowed_tones else "info"
    bullet_html = ""
    if bullets:
        items = "".join(f"<li>{escape(item)}</li>" for item in bullets)
        bullet_html = f"<ul>{items}</ul>"

    st.markdown(
        (
            f'<div class="chemease-note chemease-note--{note_tone}">'
            f"<h4>{escape(title)}</h4>"
            f"<p>{escape(description)}</p>"
            f"{bullet_html}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_metric_cards(cards: Sequence[tuple[str, str, str]]) -> None:
    """Render a row of descriptive metric cards."""

    if not cards:
        return

    columns = st.columns(len(cards))
    for column, (label, value, description) in zip(columns, cards):
        with column:
            st.markdown(
                (
                    '<div class="chemease-card">'
                    f"<h3>{escape(label)}</h3>"
                    f"<p><strong>{escape(value)}</strong></p>"
                    f"<p>{escape(description)}</p>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


def render_empty_state(title: str, description: str) -> None:
    """Render a gentle empty-state message."""

    st.markdown(
        (
            '<div class="chemease-empty">'
            f"<strong>{escape(title)}</strong>"
            f"{escape(description)}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
