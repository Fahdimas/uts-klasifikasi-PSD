with tab_sampel:
    st.subheader("📍 Peta Sebaran Titik Sampel & Hasil Prediksi")
    st.markdown("Menampilkan sebaran titik sampel dari data latih/uji tutupan lahan dengan warna berbeda tiap kelas.")
    
    sample_path = R / "samples.csv"
    if sample_path.exists():
        df_samples = pd.read_csv(sample_path)
        
        if 'class' in df_samples.columns or 'label' in df_samples.columns:
            kolom_kelas = 'class' if 'class' in df_samples.columns else 'label'
            daftar_kelas = df_samples[kolom_kelas].unique().tolist()
            selected_classes = st.multiselect("Pilih Kelas Lahan:", daftar_kelas, default=daftar_kelas)
            
            df_filtered = df_samples[df_samples[kolom_kelas].isin(selected_classes)]
        else:
            df_filtered = df_samples
            
        col_map, col_stat = st.columns([2, 1])
        
        with col_map:
            # Buat Peta untuk Sampel
            m_sampel = folium.Map(location=[-7.536, 112.238], zoom_start=8, tiles=None)
            folium.TileLayer("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google", name="Google Satellite", max_zoom=20).add_to(m_sampel)
            
            classes_meta = meta.get('classes', [])
            
            # Fungsi pintar untuk mencari warna berdasarkan label (bisa string nama, lowercase, atau angka index)
            def get_color_for_label(lbl):
                for idx, c in enumerate(classes_meta):
                    # Cocokkan dengan nama, id, atau indeks angka
                    if str(lbl).strip().lower() == str(c.get('name', '')).strip().lower() or \
                       str(lbl) == str(c.get('id', idx)) or \
                       str(lbl) == str(idx):
                        return c.get('color', '#3388ff')
                return '#3388ff' # Fallback default warna biru jika tidak ketemu
            
            # Tambahkan Marker Titik Sampel dengan warna dinamis per kelas
            for _, row in df_filtered.iterrows():
                lat = row.get('latitude', row.get('lat', -7.5))
                lon = row.get('longitude', row.get('lon', row.get('lng', 112.2)))
                label = row.get('class', row.get('label', 'Sampel'))
                
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
                
            # Tambahkan kotak legenda khusus sampel (dengan text color hitam agar jelas di background putih)
            legenda_items = "".join(
                f"<span style='display:inline-block;width:14px;height:14px;background:{k['color']};margin-right:6px;border-radius:50%;vertical-align:middle;'></span><span style='color:black;vertical-align:middle;'>{k['name']}</span><br>" 
                for k in classes_meta
            )
            legenda_sampel = f"<div style='position:fixed;bottom:25px;left:25px;z-index:9999;background:white;padding:10px 12px;border:1px solid #888;font-size:12px;border-radius:5px;box-shadow: 0 2px 6px rgba(0,0,0,0.3);'><b>Legenda Sampel</b><br>{legenda_items}</div>"
            
            m_sampel.get_root().html.add_child(folium.Element(legenda_sampel))
                
            st_folium(m_sampel, height=500, use_container_width=True, returned_objects=[])
            
        with col_stat:
            st.markdown("### **Distribusi Titik**")
            if 'class' in df_samples.columns or 'label' in df_samples.columns:
                st.dataframe(df_samples[kolom_kelas].value_counts().reset_index(), use_container_width=True)
            else:
                st.info(f"Total Titik Sampel: {len(df_samples)}")
    else:
        st.warning("File `samples.csv` tidak ditemukan di dalam folder results.")