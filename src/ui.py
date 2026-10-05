"""Helper tampilan: format angka gaya Indonesia, pemanggil grafik, dan keterangan sumber."""
import inspect

import numpy as np
import streamlit as st

_HAS_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters


def fmt_int(n) -> str:
    return f"{int(round(float(n))):,}".replace(",", ".")


def fmt_dec(x, d: int = 1) -> str:
    return f"{float(x):,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def show(fig, key=None, **kw):
    """st.plotly_chart yang kompatibel lintas versi Streamlit."""
    fig.update_layout(separators=",.")  # desimal koma, ribuan titik
    if _HAS_WIDTH:
        return st.plotly_chart(fig, width="stretch", key=key, theme=None, **kw)
    return st.plotly_chart(fig, use_container_width=True, key=key, theme=None, **kw)


_DF_WIDTH = "width" in inspect.signature(st.dataframe).parameters


def tabel(df, target=st, **kw):
    """st.dataframe yang kompatibel lintas versi Streamlit."""
    if _DF_WIDTH:
        return target.dataframe(df, width="stretch", **kw)
    return target.dataframe(df, use_container_width=True, **kw)


def sumber(tabel: str):
    st.caption(f"**Sumber: BPS.** {tabel}. Olahan penulis.")


def zoom_dari_bounds(minx, miny, maxx, maxy):
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    span = max(maxx - minx, (maxy - miny) * 1.6, 0.05)
    zoom = float(np.clip(np.log2(560 / span) - 0.2, 3.0, 10.0))
    return dict(lat=cy, lon=cx), zoom
