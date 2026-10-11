import json
from pathlib import Path
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Klasifikasi Lahan Jawa Timur", layout="wide")
BASE = Path(__file__).parent
R = BASE / "results"
meta = json.loads((R / "metadata.json").read_text())

st.title("Klasifikasi Tutupan Lahan Jawa Timur - UTS PSD")
st.caption(f"Sentinel-2 L2A | Model: {meta['model']}")

# Tab Navigasi
tab_peta, tab_sampel, tab_eval, tab_hitung = st.tabs(
    ["Peta Regional & AOI", "Peta Titik Sampel", "Evaluasi dan Statistik", "Perhitungan Manual"]
)

classes_meta = meta.get("classes", [])

with tab_peta:
    pilih = st.selectbox("Zoom ke area", [x["name"] for x in meta["aois"]])
    pusat = next(x for x in meta["aois"] if x["name"] == pilih)["center"]
    opasitas = st.slider("Opasitas hasil klasifikasi", 0.1, 1.0, 0.75)

    m = folium.Map(location=pusat, zoom_start=11, tiles=None)
    folium.TileLayer("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google", name="Google Satellite", max_zoom=20).add_to(m)

    prov = meta.get("province")
    if prov and (R / prov["file"]).exists():
        folium.raster_layers.ImageOverlay(image=str(R / prov["file"]), bounds=prov["bounds"], opacity=opasitas, name="Seluruh Jawa Timur").add_to(m)

    for x in meta["aois"]:
        if (R / x["file"]).exists():
            folium.raster_layers.ImageOverlay(image=str(R / x["file"]), bounds=x["bounds"], opacity=opasitas, name=x["name"]).add_to(m)

    # Legenda untuk Peta Utama
    legenda_items_peta = "".join(
        f"<span style='display:inline-block;width:14px;height:14px;background:{k['color']};margin-right:6px;border-radius:3px;vertical-align:middle;'></span><span style='color:black;vertical-align:middle;'>{k['name']}</span><br>"
        for k in classes_meta
    )
    legenda_peta_html = f"<div style='position:fixed;bottom:25px;left:25px;z-index:9999;background:white;padding:10px 12px;border:1px solid #888;font-size:12px;border-radius:5px;box-shadow: 0 2px 6px rgba(0,0,0,0.3);'><b>Legenda Klasifikasi</b><br>{legenda_items_peta}</div>"
    m.get_root().html.add_child(folium.Element(legenda_peta_html))

    folium.LayerControl().add_to(m)
    st_folium(m, height=550, use_container_width=True, returned_objects=[])

with tab_sampel:
    st.subheader("📍 Peta Sebaran Titik Sampel & Hasil Prediksi")
    st.markdown("Menampilkan sebaran titik sampel dari data latih/uji tutupan lahan dengan warna berbeda tiap kelas.")

    sample_path = R / "samples.csv"
    if sample_path.exists():
        df_samples = pd.read_csv(sample_path)

        # nama kelas: kolom 'label' berisi angka 0-5, diubah ke nama kelas
        nama_by_id = {c.get("id", i): c["name"] for i, c in enumerate(classes_meta)}
        kolom_kelas = "class" if "class" in df_samples.columns else ("label" if "label" in df_samples.columns else None)
        if kolom_kelas:
            if pd.api.types.is_numeric_dtype(df_samples[kolom_kelas]):
                df_samples["Kelas"] = df_samples[kolom_kelas].map(nama_by_id).fillna(df_samples[kolom_kelas].astype(str))
            else:
                df_samples["Kelas"] = df_samples[kolom_kelas].astype(str)
            daftar_kelas = df_samples["Kelas"].unique().tolist()
            selected_classes = st.multiselect("Pilih Kelas Lahan:", daftar_kelas, default=daftar_kelas)
            df_filtered = df_samples[df_samples["Kelas"].isin(selected_classes)]
        else:
            df_filtered = df_samples

        maks_titik = st.slider("Jumlah titik yang ditampilkan di peta", 100, 3000, 1500, step=100,
                               help="Titik diambil acak dari data. Semua titik tetap dihitung di tabel distribusi.")
        df_tampil = df_filtered.sample(min(maks_titik, len(df_filtered)), random_state=42) if len(df_filtered) else df_filtered

        col_map, col_stat = st.columns([2, 1])

        with col_map:
            m_sampel = folium.Map(location=[-7.536, 112.238], zoom_start=8, tiles=None)
            folium.TileLayer("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google", name="Google Satellite", max_zoom=20).add_to(m_sampel)

            def get_color_for_label(lbl):
                for idx, c in enumerate(classes_meta):
                    if str(lbl).strip().lower() == str(c.get("name", "")).strip().lower() or \
                       str(lbl) == str(c.get("id", idx)) or \
                       str(lbl) == str(idx):
                        return c.get("color", "#3388ff")
                return "#3388ff"

            for _, row in df_tampil.iterrows():
                lat = row.get("latitude", row.get("lat", -7.5))
                lon = row.get("longitude", row.get("lon", row.get("lng", 112.2)))
                label = row.get("Kelas", "Sampel")

                marker_color = get_color_for_label(label)

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6,
                    color=marker_color,
                    weight=1,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.8,
                    popup=f"Kelas: {label}"
                ).add_to(m_sampel)

            legenda_items_sampel = "".join(
                f"<span style='display:inline-block;width:14px;height:14px;background:{k['color']};margin-right:6px;border-radius:50%;vertical-align:middle;'></span><span style='color:black;vertical-align:middle;'>{k['name']}</span><br>"
                for k in classes_meta
            )
            legenda_sampel = f"<div style='position:fixed;bottom:25px;left:25px;z-index:9999;background:white;padding:10px 12px;border:1px solid #888;font-size:12px;border-radius:5px;box-shadow: 0 2px 6px rgba(0,0,0,0.3);'><b>Legenda Sampel</b><br>{legenda_items_sampel}</div>"

            m_sampel.get_root().html.add_child(folium.Element(legenda_sampel))

            st_folium(m_sampel, height=500, use_container_width=True, returned_objects=[])

        with col_stat:
            st.markdown("### **Distribusi Titik**")
            if kolom_kelas:
                st.dataframe(df_samples["Kelas"].value_counts().rename_axis("Kelas").reset_index(name="Jumlah"), use_container_width=True)
            else:
                st.info(f"Total Titik Sampel: {len(df_samples)}")
    else:
        st.warning("File `samples.csv` tidak ditemukan di dalam folder results.")

with tab_eval:
    st.subheader("📊 Evaluasi Performa Model")
    if (R / "model_comparison.csv").exists():
        st.dataframe(pd.read_csv(R / "model_comparison.csv").round(4))
    if (R / "confusion_matrix.png").exists():
        st.image(str(R / "confusion_matrix.png"), caption="Confusion Matrix")
    if (R / "luas_per_aoi_ha.csv").exists():
        st.subheader("Luas Kelas per Area (Hektar)")
        st.dataframe(pd.read_csv(R / "luas_per_aoi_ha.csv").set_index("AOI"))

with tab_hitung:
    file_md = BASE / "perhitungan_manual.md"
    if file_md.exists():
        st.markdown(file_md.read_text(encoding="utf-8"))
    else:
        st.info("File perhitungan_manual.md belum ada di repo (taruh sejajar dengan app.py).")
