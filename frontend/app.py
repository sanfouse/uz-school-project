import json
import time

import streamlit as st
import api

from typing import Dict, Any, List

example_json = """
{
  "profi_login": "string",
  "profi_password": "string",
  "accept_text": "string",
  "accept_price": "string",
  "accept_newbie": "True",
  "accept": "True",
  "proxy_host": "string",
  "proxy_user": "string",
  "proxy_password": "string",
  "proxy_port": "string"
}
"""

st.set_page_config(page_title="Scrapers Frontend", layout="wide", page_icon="🕷️")

if "show_logs_for" not in st.session_state:
    st.session_state.show_logs_for = None
if "logs_autorefresh" not in st.session_state:
    st.session_state.logs_autorefresh = True
if "logs_tail" not in st.session_state:
    st.session_state.logs_tail = 500


def tag(text: str, color: str = "gray"):
    st.markdown(
        f"<span style='background:{color};padding:2px 6px;border-radius:6px;color:white;font-size:12px'>{text}</span>",
        unsafe_allow_html=True,
    )


st.sidebar.title("Scrapers Frontend")
with st.sidebar:
    h = api.health()
    if h["ok"]:
        tag("API: OK", "#16a34a")
        st.write(h["data"])
    else:
        tag("API: DOWN", "#dc2626")
        st.error(h["error"])
    st.caption(f"BASE_URL: `{api.BASE_URL}`")

st.header("Запуск скрапера")
with st.form("start_form", clear_on_submit=False):
    col1, col2 = st.columns([1, 1])
    with col1:
        job_name = st.text_input(
            "Имя job",
            placeholder="my-scraper",
            help="Произвольный идентификатор задачи",
        )
    with col2:
        params_text = st.text_area(
            "Параметры (JSON)",
            value=example_json,
            height=250,
        )
    submitted = st.form_submit_button("Старт", use_container_width=True)
    if submitted:
        try:
            params = json.loads(params_text) if params_text.strip() else {}
        except json.JSONDecodeError as e:
            st.error(f"Некорректный JSON: {e}")
        else:
            if not job_name.strip():
                st.warning("Укажи имя job.")
            else:
                res = api.start_scraper(job_name.strip(), params)
                if res["ok"]:
                    st.success(f"Запущено: {res['data']}")
                else:
                    st.error(f"Ошибка запуска: {res['error']}")

st.divider()
st.header("Активные job'ы")

jobs_res = api.list_jobs()
if not jobs_res["ok"]:
    st.error(f"Не удалось получить список: {jobs_res['error']}")
else:
    jobs: List[Dict[str, Any]] = jobs_res["data"] or []
    if not jobs:
        st.info("Активных job'ов нет.")
    else:
        cols = st.columns([2, 1, 2, 1, 1])
        headers = ["Job Name", "Status", "Created", "Логи", "Стоп"]
        for c, hdr in zip(cols, headers):
            c.markdown(f"**{hdr}**")
        for j in jobs:
            c1, c3, c4, c5, c6 = st.columns([2, 1, 2, 1, 1])
            c1.write(j.get("job_name") or j.get("name") or "-")
            status = j.get("status", "-")
            color = (
                "#16a34a"
                if status in ("running", "active")
                else "#f59e0b" if status in ("pending", "starting") else "#6b7280"
            )
            c3.markdown(
                f"<span style='color:{color};font-weight:600'>{status}</span>",
                unsafe_allow_html=True,
            )
            c4.write(j.get("start_time") or "-")
            log_btn = c5.button(
                "Показать", key=f"show_{j.get('name')}_{j}"
            )
            stop_btn = c6.button("⏹️", key=f"stop_{j.get('name')}", type="secondary")
            if log_btn:
                st.session_state.show_logs_for = j.get("name")
                st.session_state.logs_autorefresh = True
            if stop_btn and j.get("name"):
                stop_res = api.stop_scraper(str(j["name"]))
                if stop_res["ok"]:
                    st.toast("Остановлено", icon="✅")
                else:
                    st.error(f"Ошибка остановки: {stop_res['error']}")
                st.rerun()

if st.session_state.show_logs_for:
    with st.expander(f"Логи: {st.session_state.show_logs_for}", expanded=True):
        top = st.columns([1, 2, 1])
        with top[0]:
            st.toggle(
                "Автообновление",
                value=st.session_state.logs_autorefresh,
                key="logs_autorefresh",
            )
        with top[2]:
            if st.button("Закрыть"):
                st.session_state.show_logs_for = None
                st.rerun()

        placeholder = st.empty()

        def render_logs():
            res = api.get_job_logs(
                st.session_state.show_logs_for
            )
            if res["ok"]:
                placeholder.code(res["data"][-100000:], language="bash")
            else:
                placeholder.error(res["error"])

        if st.session_state.logs_autorefresh:
            i = 0
            while i < 10:
                render_logs()
                time.sleep(15)
                i += 1
                st.caption("Обновление…")
        else:
            render_logs()
