"""Pembungkus cache Streamlit untuk pemuat data."""
import streamlit as st

from . import config as C
from . import data_loader as dl


@st.cache_data(show_spinner="Memuat data kab/kota…")
def geospasial():
    return dl.load_geospasial()


@st.cache_data(show_spinner=False)
def hierarki():
    return dl.load_hierarki()


@st.cache_data(show_spinner=False)
def multivariat():
    return dl.load_multivariat()


@st.cache_resource(show_spinner=False)
def geojson_kab():
    return dl.load_geojson(C.FILE_GJ_KAB)


@st.cache_resource(show_spinner=False)
def geojson_prov():
    return dl.load_geojson(C.FILE_GJ_PROV)
