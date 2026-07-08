import time
import streamlit as st


def init_timer():

    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False

    if "timer_paused" not in st.session_state:
        st.session_state.timer_paused = False

    if "remaining_time" not in st.session_state:
        st.session_state.remaining_time = 0

    if "timer_type" not in st.session_state:
        st.session_state.timer_type = "Exercise"


def start_timer(seconds, timer_type="Exercise"):

    st.session_state.remaining_time = seconds
    st.session_state.timer_running = True
    st.session_state.timer_paused = False
    st.session_state.timer_type = timer_type


def pause_timer():
    st.session_state.timer_paused = True


def resume_timer():
    st.session_state.timer_paused = False


def update_timer():

    if (
        st.session_state.timer_running
        and not st.session_state.timer_paused
    ):

        if st.session_state.remaining_time > 0:

            time.sleep(1)

            st.session_state.remaining_time -= 1

            st.rerun()

        else:

            st.session_state.timer_running = False