import json
from pathlib import Path
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Klasifikasi Lahan Jawa Timur", layout="wide")
R = Path(__file__).parent / "results"
meta = json.loads((R / "metadata.json").read_text())

st.title("Klasifikasi Tutupan Lahan Jawa Timur")
st.caption(f"Sentinel-2 L2A, periode {meta['periode'][0]} s/d {meta['periode'][1]}, model: {meta['model']}")
a, b, c = st.columns(3)
a.metric("Akurasi uji", f"{meta['metrics']['accuracy'] * 100:.2f}%")
b.metric("F1 macro", f"{meta['metrics']['f1_macro']:.3f}")
c.metric("Data latih / uji", f"{meta['n_train']} / {meta['n_test']}")

tab_peta, tab_eval = st.tabs(["Peta", "Evaluasi dan statistik"])
with tab_peta:
    pilih = st.selectbox("Zoom ke area", [x["name"] for x in meta["aois"]])
    pusat = next(x for x in meta["aois"] if x["name"] == pilih)["center"]
    opasitas = st.slider("Opasitas hasil klasifikasi", 0.1, 1.0, 0.75)
    m = folium.Map(location=pusat, zoom_start=13, tiles=None)
    folium.TileLayer("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google", name="Google Satellite", max_zoom=20).add_to(m)
    prov = meta.get("province")
    if prov:
        folium.raster_layers.ImageOverlay(image=str(R / prov["file"]), bounds=prov["bounds"], opacity=opasitas, name="Seluruh Jawa Timur").add_to(m)
    for x in meta["aois"]:
        folium.raster_layers.ImageOverlay(image=str(R / x["file"]), bounds=x["bounds"], opacity=opasitas, name=x["name"]).add_to(m)
    legenda = "<div style='position:fixed;bottom:25px;left:25px;z-index:9999;background:white;padding:8px 10px;border:1px solid #888;font-size:12px'><b>Legenda</b><br>" + "".join(
        f"<span style='display:inline-block;width:14px;height:14px;background:{k['color']};margin-right:6px'></span>{k['name']}<br>" for k in meta["classes"]) + "</div>"
    m.get_root().html.add_child(folium.Element(legenda))
    folium.LayerControl().add_to(m)
    st_folium(m, height=600, use_container_width=True, returned_objects=[])

with tab_eval:
    st.subheader("Perbandingan model")
    st.dataframe(pd.read_csv(R / "model_comparison.csv").round(4))
    st.subheader("Jumlah data latih dan uji")
    st.dataframe(pd.read_csv(R / "train_test_split.csv"))
    st.subheader("Luas kelas per area (hektar)")
    st.dataframe(pd.read_csv(R / "luas_per_aoi_ha.csv").set_index("AOI"))
    st.image(str(R / "confusion_matrix.png"), caption="Confusion matrix data uji")
