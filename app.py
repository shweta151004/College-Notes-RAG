import html
import os
import time

import streamlit as st

from src.pdf_loader import load_pdf
from src.chunker import chunk_documents
from src.vector_store import (
    create_vector_store,
    load_vector_store,
    vector_store_exists,
)
from src.retriever import get_retriever
from src.manifest import (
    add_document,
    already_indexed,
    load_manifest,
    save_manifest
)
from src.export_chat import (
    export_chat_pdf,
    export_chat_markdown
)

APP_TITLE = "College Notes RAG"
UPLOAD_DIR = "data/uploaded_pdfs"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="CN",
    layout="wide",
    initial_sidebar_state="expanded",
)


def escape(value):
    return html.escape(str(value))


def inject_styles():
    css_path = os.path.join("assets", "style.css")

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
            @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap");

            :root {
                --app-bg: #050914;
                --card-bg: rgba(15, 23, 42, 0.78);
                --card-bg-strong: rgba(17, 24, 39, 0.94);
                --line: rgba(148, 163, 184, 0.18);
                --line-strong: rgba(96, 165, 250, 0.45);
                --text: #f8fafc;
                --muted: #9ca3af;
                --soft: #cbd5e1;
                --cyan: #38bdf8;
                --blue: #60a5fa;
                --green: #5eead4;
                --pink: #f0abfc;
                --shadow: 0 24px 90px rgba(0, 0, 0, 0.38);
            }

            html, body, [class*="css"] {
                font-family: "Inter", sans-serif;
            }

            .stApp {
                color: var(--text);
                background:
                    radial-gradient(circle at 12% 4%, rgba(56, 189, 248, 0.18), transparent 24rem),
                    radial-gradient(circle at 88% 12%, rgba(240, 171, 252, 0.13), transparent 24rem),
                    radial-gradient(circle at 58% 100%, rgba(94, 234, 212, 0.1), transparent 28rem),
                    linear-gradient(135deg, #050914 0%, #0b1020 48%, #0f172a 100%);
            }
            
            /* Sidebar document cards */
            .stButton button {
                text-align: left;
                white-space: pre-line;
                line-height: 1.5;
            }

            #MainMenu,
            footer{
                visibility:hidden;
            }

            header{
                visibility:visible !important;
            }

            .block-container {
                max-width: 1220px;
                padding-top: .7rem;
                padding-bottom: .3rem;
            }

            div[data-testid="stVerticalBlock"] {
                gap: 0.45rem;
            }

            section[data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(2, 6, 23, 0.96), rgba(10, 15, 30, 0.96)),
                    radial-gradient(circle at top, rgba(56, 189, 248, 0.12), transparent 18rem);
                border-right: 1px solid rgba(148, 163, 184, 0.16);
                box-shadow: 22px 0 70px rgba(0, 0, 0, 0.34);
            }

            section[data-testid="stSidebar"] > div {
                padding-top: 1.4rem;
            }

            section[data-testid="stSidebar"] * {
                color: var(--text);
            }

            .sidebar-brand {
                display: flex;
                align-items: center;
                gap: 0.85rem;
                padding: 0.35rem 0 1.25rem;
            }

            .brand-mark {
                display: grid;
                width: 46px;
                height: 46px;
                place-items: center;
                border-radius: 14px;
                border: 1px solid rgba(56, 189, 248, 0.48);
                background: linear-gradient(135deg, rgba(56, 189, 248, 0.28), rgba(94, 234, 212, 0.14));
                color: #e0f2fe;
                font-weight: 900;
                letter-spacing: 0;
                box-shadow: 0 16px 36px rgba(56, 189, 248, 0.14);
            }

            .sidebar-title {
                font-size: 1.05rem;
                font-weight: 850;
                letter-spacing: 0;
            }

            .sidebar-subtitle {
                margin-top: 0.15rem;
                color: var(--muted);
                font-size: 0.82rem;
            }

            .sidebar-section-title {
                margin: 1rem 0 0.7rem;
                color: #bfdbfe;
                font-size: 0.72rem;
                font-weight: 850;
                letter-spacing: 0.1em;
                text-transform: uppercase;
            }

            .sidebar-mini-card {
                padding: 0.85rem 0.95rem;
                border: 1px solid var(--line);
                border-radius: 8px;
                background: rgba(15, 23, 42, 0.72);
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
            }

            .pdf-card {
                padding: 0.88rem 0.95rem;
                margin-bottom: 0.65rem;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 8px;
                background: rgba(15, 23, 42, 0.74);
                transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
            }

            .pdf-card:hover {
                transform: translateY(-2px);
                border-color: rgba(56, 189, 248, 0.48);
                background: rgba(30, 41, 59, 0.78);
            }

            .pdf-title {
                overflow: hidden;
                color: var(--text);
                font-size: 0.88rem;
                font-weight: 750;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .pdf-status {
                margin-top: 0.3rem;
                color: var(--muted);
                font-size: 0.76rem;
            }

            .hero {
                position: relative;
                overflow: hidden;
                margin-bottom: 8rem;
                padding: 28px 36px;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 8px;
                background:
                    linear-gradient(135deg, rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.48)),
                    radial-gradient(circle at 85% 18%, rgba(56, 189, 248, 0.18), transparent 18rem);
                box-shadow: var(--shadow);
                backdrop-filter: blur(18px);
            }

            .hero:after {
                content: "";
                position: absolute;
                inset: auto -8rem -12rem auto;
                width: 28rem;
                height: 28rem;
                background: radial-gradient(circle, rgba(94, 234, 212, 0.13), transparent 60%);
                pointer-events: none;
            }

            .hero-kicker {
                color: var(--green);
                font-size: 0.75rem;
                font-weight: 850;
                letter-spacing: 0.12em;
                text-transform: uppercase;
            }

            .gradient-title {
                max-width: 850px;
                margin: 0.25rem 0 0.5rem;
                background: linear-gradient(90deg, #f8fafc 0%, #bae6fd 36%, #c4b5fd 72%, #5eead4 100%);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                font-size: 2.3rem;
                font-weight: 900;
                line-height: 1.1;
                letter-spacing: 0;
            }

            .hero-copy {
                max-width: 760px;
                margin: 0;
                color: var(--soft);
                font-size: 1.04rem;
                line-height: 1.7;
            }

            .hero-actions {
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 1.2rem;
            }

            .pill {
                display: inline-flex;
                align-items: center;
                padding: 0.45rem 0.72rem;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 999px;
                background: rgba(15, 23, 42, 0.72);
                color: #dbeafe;
                font-size: 0.8rem;
                font-weight: 650;
            }

            .metric-card {
                min-height: 115px;
                padding: 1.15rem;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 8px;
                background: rgba(15, 23, 42, 0.74);
                box-shadow: 0 16px 46px rgba(0, 0, 0, 0.22);
                backdrop-filter: blur(18px);
                transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
            }

            .metric-card:hover {
                transform: translateY(-2px);
                border-color: rgba(56, 189, 248, 0.44);
                background: rgba(17, 24, 39, 0.92);
            }

            .metric-label {
                color: var(--muted);
                font-size: 0.76rem;
                font-weight: 850;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .metric-value {
                margin-top: 0.4rem;
                color: var(--text);
                font-size: 1.45rem;
                font-weight: 900;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .metric-caption {
                margin-top: 0.18rem;
                color: var(--soft);
                font-size: 0.84rem;
            }

            .section-heading {
                margin:16px 0 10px 0;
            }

            .section-heading span {
                color: var(--cyan);
                font-size: 0.72rem;
                font-weight: 850;
                letter-spacing: 0.1em;
                text-transform: uppercase;
            }

            .section-heading h2 {
                margin: 0.12rem 0 0;
                color: var(--text);
                font-size: 1.38rem;
                font-weight: 850;
                letter-spacing: 0;
            }

            .upload-shell,
            .empty-chat {
                padding: 1rem;
                margin-top: 8px;
                margin-bottom: 18px;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 8px;
                background:
                    linear-gradient(145deg, rgba(15, 23, 42, 0.78), rgba(15, 23, 42, 0.58)),
                    radial-gradient(circle at top right, rgba(96, 165, 250, 0.12), transparent 16rem);
                box-shadow: 0 16px 46px rgba(0, 0, 0, 0.22);
                backdrop-filter: blur(18px);
            }

            .upload-top {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                margin-bottom: 0.95rem;
            }

            .upload-title {
                color: var(--text);
                font-size: 1rem;
                font-weight: 800;
            }

            .upload-subtitle,
            .empty-chat p {
                margin: 0.25rem 0 0;
                color: var(--muted);
                font-size: 0.92rem;
            }

            .upload-badge {
                flex: 0 0 auto;
                padding: 0.44rem 0.66rem;
                border: 1px solid rgba(94, 234, 212, 0.3);
                border-radius: 999px;
                background: rgba(20, 184, 166, 0.1);
                color: #ccfbf1;
                font-size: 0.76rem;
                font-weight: 750;
            }

            [data-testid="stFileUploader"] {
                padding: 1.05rem;
                border: 1px dashed rgba(56, 189, 248, 0.52);
                border-radius: 8px;
                background: rgba(2, 6, 23, 0.26);
                transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
            }

            [data-testid="stFileUploader"]:hover {
                transform: translateY(-1px);
                border-color: rgba(94, 234, 212, 0.75);
                background: rgba(15, 23, 42, 0.58);
            }

            [data-testid="stFileUploaderDropzone"] {
                border-radius: 8px;
                background: transparent;
            }

            .selected-files {
                margin-top: 0.85rem;
                padding: 0.78rem 0.9rem;
                border: 1px solid rgba(148, 163, 184, 0.14);
                border-radius: 8px;
                background: rgba(15, 23, 42, 0.58);
                color: var(--soft);
                font-size: 0.86rem;
            }

            [data-testid="stChatMessage"] {
                padding: 1.05rem 1.12rem;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 8px;
                background: rgba(15, 23, 42, 0.72);
                box-shadow: 0 14px 44px rgba(0, 0, 0, 0.2);
                backdrop-filter: blur(16px);
            }

            [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
                margin-left: 5%;
                border-color: rgba(96, 165, 250, 0.34);
                background: linear-gradient(145deg, rgba(30, 64, 175, 0.32), rgba(8, 47, 73, 0.42));
            }

            [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
                margin-right: 5%;
                border-color: rgba(94, 234, 212, 0.24);
                background: linear-gradient(145deg, rgba(15, 23, 42, 0.86), rgba(17, 24, 39, 0.68));
            }

            [data-testid="stChatMessage"] p,
            [data-testid="stMarkdownContainer"] li {
                color: var(--text);
                line-height: 1.72;
            }

            /* ChatGPT/NoteGPT style typography spacing */
            [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] p {
                margin-bottom: 0.8rem;
                line-height: 1.7;
            }
            [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] ul,
            [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] ol {
                margin-top: 0.25rem;
                margin-bottom: 0.8rem;
                padding-left: 1.5rem;
            }
            [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] li {
                margin-bottom: 0.3rem;
                line-height: 1.6;
            }
            [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] h1,
            [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] h2,
            [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] h3 {
                margin-top: 1rem;
                margin-bottom: 0.5rem;
                font-weight: 700;
            }

            /* Sidebar delete button container styling */
            div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
                background: transparent !important;
                border: none !important;
                color: rgba(239, 68, 68, 0.7) !important;
                font-size: 1.1rem !important;
                padding: 0 !important;
                margin-top: 0.9rem !important;
                box-shadow: none !important;
                min-height: auto !important;
                cursor: pointer;
                transition: color 150ms ease, transform 150ms ease !important;
            }
            div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
                color: rgba(239, 68, 68, 1) !important;
                transform: scale(1.1) !important;
                background: transparent !important;
                box-shadow: none !important;
            }

            .empty-chat strong {
                color: var(--text);
                font-size: 1rem;
            }
            .empty-chat h3 {
                margin: 0;
                color: #ffffff;
                font-size: 1.3rem;
                font-weight: 700;
            }

            .welcome-suggestions {
                margin-top: 18px;
                display: grid;
                gap: 10px;
            }

            .suggestion-card {
                padding: 12px 16px;
                border-radius: 10px;
                border: 1px solid rgba(56,189,248,.18);
                background: rgba(15,23,42,.55);
                color: #dbeafe;
                transition: all .2s ease;
            }

            .suggestion-card:hover {
                transform: translateY(-2px);
                border-color: #38bdf8;
                background: rgba(30,41,59,.75);
            }

            .thinking-card {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem;
                border: 1px solid rgba(56, 189, 248, 0.22);
                border-radius: 8px;
                background: rgba(15, 23, 42, 0.76);
            }

            .loader-dot {
                width: 0.62rem;
                height: 0.62rem;
                border-radius: 999px;
                background: var(--green);
                box-shadow: 0 0 0 rgba(94, 234, 212, 0.5);
                animation: pulse 1.35s infinite;
            }

            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(94, 234, 212, 0.48); }
                70% { box-shadow: 0 0 0 12px rgba(94, 234, 212, 0); }
                100% { box-shadow: 0 0 0 0 rgba(94, 234, 212, 0); }
            }

            .stButton > button,
            [data-testid="stBaseButton-primary"],
            [data-testid="stBaseButton-secondary"] {
                min-height: 2.75rem;
                border: 1px solid rgba(56, 189, 248, 0.36);
                border-radius: 8px;
                background: linear-gradient(135deg, #38bdf8, #5eead4);
                color: #031019;
                font-weight: 850;
                transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
            }

            .stButton > button:hover,
            [data-testid="stBaseButton-primary"]:hover,
            [data-testid="stBaseButton-secondary"]:hover {
                transform: translateY(-1px);
                border-color: rgba(191, 219, 254, 0.7);
                box-shadow: 0 14px 32px rgba(56, 189, 248, 0.24);
            }

            .stAlert {
                border-radius: 8px;
                border-color: rgba(148, 163, 184, 0.16);
            }

            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, #38bdf8, #5eead4);
            }

            /* Sticky Chat Input */
            [data-testid="stChatInput"]{

                position:fixed;

                bottom:12px;

                left:50%;

                right:auto;

                transform:translateX(-50%);

                width:min(1000px,64vw);

                max-width:1100px;

                z-index:999;

                padding:12px;

                background:transparent;

                border:none;

            }

            [data-testid="stChatInput"] > div{

            background:#22232d;

            border-radius:18px;

            box-shadow:0 10px 35px rgba(0,0,0,.35);

            padding:10px;

            }

            hr {
                border-color: rgba(148, 163, 184, 0.14);
            }

            ::-webkit-scrollbar {
                width: 9px;
            }

            ::-webkit-scrollbar-track {
                background: #020617;
            }

            ::-webkit-scrollbar-thumb {
                border: 2px solid #020617;
                border-radius: 999px;
                background: #334155;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: #38bdf8;
            }

            @media (max-width: 900px){
                [data-testid="stChatInput"] {
                    left: 0;
                }
              
                .block-container {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }

                .hero {
                    padding: 1.5rem;
                }
                
                .gradient-title {
                    font-size: 2rem;
                }

                .upload-top {
                    flex-direction: column;
                    align-items: flex-start;
                }
            }

            @media (max-width: 640px) {
                .gradient-title {
                    font-size: 1.92rem;
                }

                .hero-copy {
                    font-size: 0.95rem;
                }

                [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
                [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
                    margin-left: 0;
                    margin-right: 0;
                }
            }

            /* Premium UI refresh override */
            :root {
                --surface-premium: rgba(12, 18, 35, 0.86);
                --surface-premium-strong: rgba(15, 23, 42, 0.94);
                --surface-premium-soft: rgba(15, 23, 42, 0.58);
                --border-premium: rgba(148, 163, 184, 0.16);
                --accent-border: rgba(56, 189, 248, 0.42);
                --shadow-premium: 0 22px 70px rgba(0, 0, 0, 0.34);
                --shadow-card: 0 12px 34px rgba(0, 0, 0, 0.24);
            }

            .block-container {
                max-width: 1280px;
                padding-top: 18px;
                padding-bottom: 112px;
            }

            div[data-testid="stVerticalBlock"] {
                gap: 0.75rem;
            }

            .sidebar-brand {
                margin-bottom: 1rem;
                padding: 1rem;
                border: 1px solid var(--border-premium);
                border-radius: 14px;
                background:
                    linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(8, 13, 28, 0.82)),
                    radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 12rem);
                box-shadow: var(--shadow-card);
            }

            .brand-mark {
                width: 42px;
                height: 42px;
                border-radius: 12px;
            }

            .sidebar-section-title {
                margin: 1rem 0 0.55rem;
            }

            .sidebar-mini-card {
                padding: 0.9rem 1rem;
                border-radius: 12px;
                background: rgba(15, 23, 42, 0.64);
                box-shadow: var(--shadow-card);
            }

            .pdf-card {
                margin: 0.1rem 0 0.42rem;
                padding: 0.86rem 0.9rem;
                border-radius: 12px;
                background: linear-gradient(145deg, rgba(15, 23, 42, 0.78), rgba(12, 18, 35, 0.66));
                box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16);
                transition: transform 160ms ease, border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
            }

            .pdf-card:hover {
                transform: translateY(-2px);
                border-color: rgba(56, 189, 248, 0.48);
                background: rgba(30, 41, 59, 0.78);
                box-shadow: 0 16px 34px rgba(0, 0, 0, 0.24);
            }

            .pdf-card-head {
                display: flex;
                align-items: flex-start;
                gap: 0.55rem;
            }

            .pdf-status {
                display: inline-flex;
                align-items: center;
                gap: 0.3rem;
                margin-top: 0.45rem;
                color: #99f6e4;
                font-weight: 760;
            }

            .pdf-meta {
                margin-top: 0.28rem;
                color: var(--muted);
                font-size: 0.76rem;
                line-height: 1.35;
            }

            .pdf-title {
                white-space: normal;
                overflow-wrap: anywhere;
            }

            .hero {
                margin-bottom: 20px;
                padding: 26px 34px;
                border-radius: 18px;
                background:
                    linear-gradient(135deg, rgba(15, 23, 42, 0.86), rgba(15, 23, 42, 0.48)),
                    radial-gradient(circle at 88% 20%, rgba(56, 189, 248, 0.2), transparent 19rem);
                box-shadow: var(--shadow-premium);
            }

            .gradient-title {
                margin: 0.42rem 0 0.7rem;
                background: linear-gradient(90deg, #f8fafc 0%, #bae6fd 34%, #c4b5fd 70%, #5eead4 100%);
                -webkit-background-clip: text;
                background-clip: text;
                font-size: clamp(2.3rem, 4.25vw, 3.65rem);
                line-height: 1.02;
            }

            .hero-copy {
                line-height: 1.58;
            }

            .hero-actions {
                gap: 0.6rem;
                margin-top: 1.25rem;
            }

            .pill {
                min-height: 34px;
                padding: 0.45rem 0.76rem;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
            }

            .metric-card {
                min-height: 136px;
                padding: 1.05rem 1.1rem;
                border-radius: 14px;
                background: linear-gradient(145deg, rgba(15, 23, 42, 0.78), rgba(12, 18, 35, 0.62));
                box-shadow: var(--shadow-card);
            }

            .metric-icon {
                display: grid;
                width: 32px;
                height: 32px;
                place-items: center;
                margin-bottom: 0.72rem;
                border: 1px solid rgba(56, 189, 248, 0.26);
                border-radius: 10px;
                background: rgba(56, 189, 248, 0.1);
                color: #bae6fd;
                font-size: 1rem;
            }

            .metric-value {
                font-size: 1.32rem;
                line-height: 1.18;
                white-space: normal;
                overflow-wrap: anywhere;
            }

            .section-heading {
                margin: 24px 0 10px;
            }

            .upload-shell,
            .empty-chat {
                margin-top: 0;
                margin-bottom: 0.55rem;
                padding: 1.05rem;
                border-radius: 14px;
            }

            [data-testid="stFileUploader"] {
                padding: 0.85rem;
                border-radius: 14px;
            }

            [data-testid="stFileUploaderDropzone"] {
                min-height: 104px;
                border-radius: 12px;
            }

            .selected-files,
            .thinking-card,
            .stAlert {
                border-radius: 12px;
            }

            .chat-compact-hint {
                display: inline-flex;
                align-items: center;
                gap: 0.55rem;
                margin: 0 0 0.2rem;
                padding: 0.68rem 0.85rem;
                border: 1px solid rgba(148, 163, 184, 0.14);
                border-radius: 999px;
                background: rgba(15, 23, 42, 0.54);
                color: var(--soft);
                font-size: 0.88rem;
            }

            [data-testid="stChatMessage"] {
                position: relative;
                padding: 1rem 1.08rem 1.45rem;
                border-radius: 16px;
                box-shadow: 0 12px 34px rgba(0, 0, 0, 0.18);
                animation: fadeUp 180ms ease both;
            }

            [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
                margin-left: 10%;
            }

            [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
                margin-right: 10%;
            }

            [data-testid="stChatMessage"]::after {
                content: "Just now";
                position: absolute;
                right: 1rem;
                bottom: 0.58rem;
                color: rgba(203, 213, 225, 0.56);
                font-size: 0.68rem;
                font-weight: 650;
            }

            @keyframes fadeUp {
                from { opacity: 0; transform: translateY(4px); }
                to { opacity: 1; transform: translateY(0); }
            }

            div[data-testid="stHorizontalBlock"] > div:nth-child(2) button,
            div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
                min-height: 2.35rem !important;
                margin-top: 0.1rem !important;
                border: 1px solid rgba(148, 163, 184, 0.12) !important;
                border-radius: 10px !important;
                background: transparent !important;
                color: rgba(203, 213, 225, 0.86) !important;
                box-shadow: none !important;
            }

            div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover,
            div[data-testid="stHorizontalBlock"] > div:nth-child(3) button:hover {
                transform: scale(1.08) !important;
                border-color: rgba(56, 189, 248, 0.42) !important;
                color: #e0f2fe !important;
                background: transparent !important;
                box-shadow: none !important;
            }

            .stButton > button,
            [data-testid="stBaseButton-primary"],
            [data-testid="stBaseButton-secondary"] {
                border-radius: 12px;
            }

            [data-testid="stChatInput"] {
                bottom: 18px;
                left: 50%;
                width: min(1000px, calc(100vw - 48px));
                padding: 10px;
                transform: translateX(-50%);
            }

            [data-testid="stChatInput"] > div {
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 22px;
                background: rgba(15, 23, 42, 0.94);
                box-shadow: 0 18px 50px rgba(0, 0, 0, 0.42), 0 0 0 1px rgba(56, 189, 248, 0.08);
                backdrop-filter: blur(18px);
            }

            [data-testid="stChatInput"] textarea {
                color: var(--text);
            }

            @media (max-width: 900px) {
                [data-testid="stChatInput"] {
                    left: 50%;
                    width: calc(100vw - 28px);
                }

                .hero {
                    padding: 1.45rem;
                }

                .gradient-title {
                    font-size: 2.25rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state():
    defaults = {
        "sidebar_open": True,
        "selected_pdf": None,
        "retriever": None,
        "chat_history": [],
        "uploaded_pdf_names": [],
        "last_process_summary": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_manifest_data():
    try:
        manifest = load_manifest()
    except Exception:
        manifest = {}

    pages = sum(item.get("pages", 0) for item in manifest.values())
    chunks = sum(item.get("chunks", 0) for item in manifest.values())

    return manifest, pages, chunks


def ensure_retriever():
    manifest, _, _ = get_manifest_data()
    if not manifest:
        st.session_state.retriever = None
        return False

    if st.session_state.retriever is not None:
        return True

    if not vector_store_exists():
        return False

    db = load_vector_store()
    st.session_state.retriever = get_retriever(db)

    return True


def get_last_updated_time(manifest):
    if not manifest:
        return "N/A"

    latest_time = 0
    for filename in manifest.keys():
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            mtime = os.path.getmtime(filepath)
            if mtime > latest_time:
                latest_time = mtime

    if latest_time == 0:
        return "N/A"

    return time.strftime("%Y-%m-%d %H:%M", time.localtime(latest_time))


def delete_document_from_rag(pdf_name):
    try:
        # 1. Remove PDF file from disk
        filepath = os.path.join(UPLOAD_DIR, pdf_name)
        if os.path.exists(filepath):
            os.remove(filepath)

        # 2. Update manifest.json
        manifest = load_manifest()
        if pdf_name in manifest:
            del manifest[pdf_name]
            save_manifest(manifest)

        # 3. Delete embeddings from ChromaDB
        if vector_store_exists():
            db = load_vector_store()

            # Formulate all possible source metadata structures (win/posix, abs/rel)
            rel_path_win = os.path.join(UPLOAD_DIR, pdf_name)
            rel_path_posix = rel_path_win.replace("\\", "/")
            abs_path_win = os.path.abspath(rel_path_win)
            abs_path_posix = abs_path_win.replace("\\", "/")

            db._collection.delete(where={"source": rel_path_win})
            db._collection.delete(where={"source": rel_path_posix})
            db._collection.delete(where={"source": abs_path_win})
            db._collection.delete(where={"source": abs_path_posix})

        # 4. Update session state
        if pdf_name in st.session_state.uploaded_pdf_names:
            st.session_state.uploaded_pdf_names.remove(pdf_name)

        # 5. Reload retriever
        if manifest:
            db = load_vector_store()
            st.session_state.retriever = get_retriever(db)
        else:
            st.session_state.retriever = None

        return True
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return False


@st.dialog("Delete Document?")
def show_delete_confirm_dialog(pdf_name):
    st.write(f"Delete **{pdf_name}**?")
    st.write("This will permanently remove the document and its embeddings from the database.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.confirm_delete = None
            st.rerun()
    with col2:
        if st.button("Delete", type="primary", use_container_width=True):
            success = delete_document_from_rag(pdf_name)
            if success:
                st.session_state.confirm_delete = None
                st.success(f"Deleted {pdf_name}")
                time.sleep(0.7)
                st.rerun()


def metric_card(label, value, caption, icon):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{escape(icon)}</div>
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(value)}</div>
            <div class="metric-caption">{escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_parts(source):
    if " - Page " not in source:
        return source, ""

    title, page = source.rsplit(" - Page ", 1)
    return title, f"Page {page}"


def render_sidebar(manifest):
    if "confirm_delete" in st.session_state and st.session_state.confirm_delete:
        show_delete_confirm_dialog(st.session_state.confirm_delete)

    c1, c2 = st.columns([8, 1])

    with c2:
        if st.button(
            "<" if st.session_state.sidebar_open else ">",
            key="collapse_sidebar"
        ):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            st.rerun()
    if not st.session_state.sidebar_open:
        return
    
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-mark">CN</div>
            <div>
                <div class="sidebar-title">College Notes</div>
                <div class="sidebar-subtitle">AI study workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        f"""
        <div class="sidebar-mini-card">
            <div class="pdf-title">Workspace status</div>
            <div class="pdf-status">{len(manifest)} indexed document(s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-title">Knowledge Base</div>', unsafe_allow_html=True)

    pdf_names = list(manifest.keys()) or st.session_state.uploaded_pdf_names

    if pdf_names:
        for pdf_name in pdf_names:
            meta = manifest.get(pdf_name, {})
            details = []

            if meta.get("pages"):
                details.append(f"{meta['pages']} Pages")

            if meta.get("chunks"):
                details.append(f"{meta['chunks']} Chunks")

            subtitle = " • ".join(details) if details else "Ready for retrieval"

            col_card, col_preview, col_del = st.columns([0.75, 0.10, 0.15])

            with col_card:
                filepath = os.path.join(UPLOAD_DIR, pdf_name)
                st.markdown(
                    f"""
                    <div class="pdf-card">
                        <div class="pdf-card-head">
                            <span>📄</span>
                            <div>
                                <div class="pdf-title">{escape(pdf_name)}</div>
                                <div class="pdf-status">✓ Indexed</div>
                                <div class="pdf-meta">{escape(subtitle)}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    "Open",
                    key=f"open_{pdf_name}",
                    use_container_width=True,
                    ):
                    st.session_state.selected_pdf = filepath
                    st.rerun()

            with col_del:
                if st.button("×", key=f"delete_btn_{pdf_name}", help=f"Delete {pdf_name}"):
                    st.session_state.confirm_delete = pdf_name
                    st.rerun()
            with col_preview:
                filepath = os.path.join(UPLOAD_DIR, pdf_name)

                if st.button(
                    "👁",
                    key=f"preview_{pdf_name}",
                    help="Preview PDF"
                ):

                    # Toggle preview
                    if st.session_state.selected_pdf == filepath:
                        st.session_state.selected_pdf = None
                    else:
                        st.session_state.selected_pdf = filepath

                    st.rerun()
    else:
        st.info("No PDFs uploaded yet.")

    st.divider()
    st.markdown('<div class="sidebar-section-title">Session</div>', unsafe_allow_html=True)
    st.caption(f"{len(st.session_state.chat_history)} chat turn(s)")

    if st.button("Clear chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


def render_hero():
    st.markdown(
        """
<div class="hero">

<div class="hero-kicker">
AI POWERED STUDY ASSISTANT
</div>

<h1 class="gradient-title">
Chat with your College PDFs.<br>
Study Smarter, Not Harder.
</h1>

<p class="hero-copy">
Upload lecture notes, scanned documents and handwritten PDFs.
Ask questions, summarize chapters, explain concepts and receive
accurate answers backed by your own study material.
</p>

<div class="hero-actions">
<span class="pill">📄 OCR Enabled</span>
<span class="pill">📊 Table Extraction</span>
<span class="pill">🧠 ChromaDB</span>
<span class="pill">📑 Source Citation</span>
<span class="pill">⚡ Fast Retrieval</span>
<span class="pill">💬 AI Chat</span>
</div>

</div>
        """,
        unsafe_allow_html=True,
    )

def render_metrics(manifest):
    docs_col, model_col, db_col, updated_col = st.columns(4)

    last_updated = get_last_updated_time(manifest)

    with docs_col:
        metric_card("Indexed Documents", str(len(manifest)), "Knowledge Base", "📚")

    with model_col:
        metric_card("AI Model", "Gemini 2.5 Flash", "Primary reasoning model", "✦")

    with db_col:
        metric_card("Vector Database", "ChromaDB", "Persistent embedding store", "▦")

    with updated_col:
        metric_card("Last Updated", last_updated, "Latest library sync", "↻")


def save_uploaded_pdf(uploaded_file):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

    with open(save_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return save_path


def process_uploaded_files(uploaded_files):
    pdf_names = []
    total_pages = 0
    total_chunks = 0
    skipped = 0

    progress = st.progress(0)
    status_text = st.empty()

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        pdf_names.append(uploaded_file.name)
        status_text.info(f"Preparing {uploaded_file.name} ({index}/{len(uploaded_files)})")

        save_path = save_uploaded_pdf(uploaded_file)

        if already_indexed(save_path):
            skipped += 1
            progress.progress(index / len(uploaded_files))
            status_text.info(f"{uploaded_file.name} is already indexed.")
            continue

        docs = load_pdf(save_path)
        chunks = chunk_documents(docs)

        create_vector_store(chunks)
        add_document(save_path, pages=len(docs), chunks=len(chunks))

        total_pages += len(docs)
        total_chunks += len(chunks)
        progress.progress(index / len(uploaded_files))

    db = load_vector_store()
    st.session_state.retriever = get_retriever(db)

    st.session_state.uploaded_pdf_names.extend(
        pdf_name
        for pdf_name in pdf_names
        if pdf_name not in st.session_state.uploaded_pdf_names
    )

    status_text.success("PDF processing complete.")

    return {
        "processed": len(pdf_names),
        "pages": total_pages,
        "chunks": total_chunks,
        "skipped": skipped,
    }


def render_upload_section():
    st.markdown(
        """
        <div class="section-heading">
            <span>Library</span>
            <h2>Upload and index PDFs</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="upload-shell">
            <div class="upload-top">
                <div>
                    <div class="upload-title">Build your private study library</div>
                    <p class="upload-subtitle">
                        Add multiple PDFs. Existing files are skipped using your manifest.
                    </p>
                </div>
                <div class="upload-badge">Persistent vector database</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        selected_names = ", ".join(uploaded_file.name for uploaded_file in uploaded_files)
        st.markdown(
            f"""
            <div class="selected-files">
                <strong>{len(uploaded_files)} PDF file(s) selected:</strong>
                {escape(selected_names)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Process PDFs", type="primary", use_container_width=True):
            with st.status("Indexing PDFs and creating embeddings...", expanded=True) as status:
                summary = process_uploaded_files(uploaded_files)
                status.update(label="Knowledge base updated.", state="complete", expanded=False)

            st.session_state.last_process_summary = summary
            st.success(f"Processed {summary['processed']} PDF(s).")

            if summary["pages"] or summary["chunks"]:
                st.info(f"Indexed {summary['pages']} pages into {summary['chunks']} chunks.")

            if summary["skipped"]:
                st.info(f"Skipped {summary['skipped']} already-indexed PDF(s).")

    elif st.session_state.last_process_summary:
        summary = st.session_state.last_process_summary
        st.caption(
            f"Last run: {summary['processed']} PDF(s), "
            f"{summary['pages']} pages, {summary['chunks']} chunks, "
            f"{summary['skipped']} skipped."
        )


def stream_answer(text, placeholder, delay=0.018):
    streamed = ""
    lines = text.splitlines(keepends=True)
    for line in lines:
        words = line.split(" ")
        for i, word in enumerate(words):
            streamed += word
            if i < len(words) - 1:
                streamed += " "
            placeholder.markdown(streamed)
            time.sleep(delay)


def render_source_cards(sources):
    return


def render_chat_section():
    st.markdown(
        """
        <div class="section-heading">
            <span>Ask</span>
            <h2>AI chat</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.chat_history:
        st.markdown(
            """
            <div class="chat-compact-hint">
                <span>💡</span>
                <span>Ask a question after indexing PDFs. Answers will appear here.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(chat["question"])

        with st.chat_message("assistant"):
            st.markdown(chat["answer"])


def handle_chat_input():
    question = st.chat_input("Ask anything from your uploaded PDFs...")

    if not question:
        return

    if not ensure_retriever():
        st.warning("Please upload and process PDFs first.")
        return

    with st.chat_message("user"):
        st.markdown(question)

    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(
        """
        <div class="thinking-card">
            <span class="loader-dot"></span>
            <span>Searching your notes and composing an answer...</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    from src.rag_chain import answer_question

    answer, sources = answer_question(
        question,
        st.session_state.retriever,
        st.session_state.chat_history,
    )

    thinking_placeholder.empty()

    with st.chat_message("assistant"):
        answer_placeholder = st.empty()
        stream_answer(answer, answer_placeholder)

    st.session_state.chat_history.append(
        {
            "question": question,
            "answer": answer,
            "sources": sources,
        }
    )

    st.rerun()

from streamlit_pdf_viewer import pdf_viewer


def render_pdf_preview():

    selected = st.session_state.get("selected_pdf")

    if not selected:
        return

    if not os.path.exists(selected):

        st.session_state.selected_pdf = None

        return

    st.subheader("📄 PDF Preview")

    with open(selected, "rb") as f:

        pdf_bytes = f.read()

    pdf_viewer(
        pdf_bytes,
        width=900,
        height=700
    )

def render_export_chat():

    chat_history = st.session_state.get("chat_history", [])

    if not chat_history:
        return

    st.divider()
    st.subheader("Export Chat")

    pdf = export_chat_pdf(chat_history)

    st.download_button(
        label="📄 Export PDF",
        data=pdf,
        file_name="college_notes_chat.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )

def main():
    inject_styles()
    initialize_state()

    manifest, _, _ = get_manifest_data()

    if st.session_state.sidebar_open:
        left, right = st.columns([1.0, 4.0])
    else:
        left, right = st.columns([0.08, 4.92])

    with left:
        render_sidebar(manifest)

    with right:
        render_hero()
        render_metrics(manifest)
        render_upload_section()
        render_chat_section()
        render_pdf_preview()
        handle_chat_input()
        render_export_chat()

if __name__ == "__main__":
    main()


