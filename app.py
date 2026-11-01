# Dashboard hasil mini project: Association Rule dan Sequential Pattern pada Dunnhumby
# Dashboard ini hanya membaca file CSV hasil notebook Colab (folder "hasil/"), tidak menghitung ulang.
# Menjalankan: streamlit run app.py

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Dashboard Dunnhumby: AR dan SPM", layout="wide")

FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hasil")


# ---------------------------------------------------------------------
# Fungsi bantu
# ---------------------------------------------------------------------
def angka(x, d=0):
    # Format angka gaya Indonesia: 12.345,6
    s = f"{x:,.{d}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def persen(x, d=1):
    return angka(100 * x, d) + "%"


@st.cache_data
def baca(nama, **kwargs):
    # Membaca CSV dari folder hasil; mengembalikan None jika file tidak ada
    path = os.path.join(FOLDER, nama)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path, **kwargs)


def tata_letak(fig, tinggi=450):
    fig.update_layout(height=tinggi, margin=dict(l=10, r=10, t=60, b=10), title_x=0.0)
    return fig


def file_hilang(nama):
    st.info(f"File `hasil/{nama}` belum ada. Jalankan notebook versi terbaru sampai bagian 8, "
            f"lalu salin file tersebut ke folder `hasil/` di samping `app.py`.")


# ---------------------------------------------------------------------
# Memuat data
# ---------------------------------------------------------------------
aturan = baca("rq1_aturan_final.csv")
pola2 = baca("rq2_pola_panjang2.csv")
sens = baca("rq2_sensitivitas_N.csv", index_col=0)
seg_aturan = baca("rq3_segmen_aturan.csv")
seg_pola = baca("rq3_segmen_pola.csv")
seg_ukuran = baca("rq3_ukuran_keranjang_segmen.csv")
eda_ring = baca("eda_ringkasan.csv")
eda_mingguan = baca("eda_mingguan.csv")
eda_uk = baca("eda_ukuran_keranjang.csv")
eda_top = baca("eda_top_commodity.csv")
eda_ulang = baca("eda_porsi_ulang.csv")
eda_jeda = baca("eda_jeda_kunjungan.csv")

if aturan is not None:
    aturan["jumlah_item_antecedent"] = aturan["antecedent"].str.count(r"\+") + 1
if pola2 is not None:
    pola2["searah"] = pola2["searah"].astype(str).str.lower().eq("true")
    pola2["A"] = pola2["pola"].str.split("  ->  ").str[0]
    pola2["B"] = pola2["pola"].str.split("  ->  ").str[1]

# ---------------------------------------------------------------------
# Navigasi
# ---------------------------------------------------------------------
st.sidebar.title("Navigasi")
halaman = st.sidebar.radio("Pilih halaman", ["Ringkasan", "EDA", "RQ1: Association rule",
                                             "RQ2: Sequential pattern", "RQ3: Segmen"])
st.sidebar.markdown("---")
st.sidebar.caption("Data: Dunnhumby The Complete Journey (2.500 rumah tangga, 2 tahun). "
                   "Semua pola menunjukkan asosiasi, bukan sebab-akibat.")

# =====================================================================
# Halaman: Ringkasan
# =====================================================================
if halaman == "Ringkasan":
    st.title("Pola belanja rumah tangga: association rule dan sequential pattern")
    st.markdown("Mini project data mining pada data Dunnhumby *The Complete Journey*. "
                "Dashboard ini merangkum hasil notebook Colab.")

    k1, k2, k3, k4 = st.columns(4)
    if aturan is not None:
        k1.metric("Aturan final RQ1", angka(len(aturan)))
        k2.metric("Lift tertinggi RQ1", angka(aturan["lift"].max(), 2))
    if pola2 is not None:
        k3.metric("Pola panjang 2 RQ2", angka(len(pola2)))
        k4.metric("Pola searah RQ2", angka(int(pola2["searah"].sum())))

    st.subheader("Kesimpulan per pertanyaan penelitian")
    st.markdown("""
| RQ | Kesimpulan | Kekuatan bukti |
|---|---|---|
| RQ1 | Asosiasi kuat per tema: menu pasta-saus-daging, konter deli, bahan masak segar, kebutuhan rumah tangga. | Kuat |
| RQ2 | Tidak ada urutan antar-kategori yang kokoh. Urutan sebagian besar mengikuti popularitas barang (artefak frekuensi) dan tidak stabil terhadap N. | Temuan negatif dan kontribusi metode |
| RQ3 | Aturan keranjang hampir sama di kedua segmen. Perbandingan pola RQ2 antar-segmen tidak valid karena syarat rumah tangga aktif. | Sedang / tidak valid |
""")
    if eda_ring is not None:
        st.subheader("Angka kunci EDA")
        st.dataframe(eda_ring, hide_index=True, width="stretch")
    st.caption("Batas klaim: satu jaringan ritel; belanja di toko lain tidak tercatat; "
               "hasil bergantung pada pilihan parameter (support, N, W, level agregasi).")

# =====================================================================
# Halaman: EDA
# =====================================================================
elif halaman == "EDA":
    st.title("Eksplorasi data")

    if eda_mingguan is None:
        file_hilang("eda_mingguan.csv")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=eda_mingguan["week_no"], y=eda_mingguan["aktif"], mode="lines",
                                 name="Rumah tangga berbelanja pada minggu itu"))
        fig.add_trace(go.Scatter(x=eda_mingguan["week_no"], y=eda_mingguan["kumulatif"], mode="lines",
                                 name="Kumulatif rumah tangga yang sudah masuk data", line=dict(dash="dash")))
        tandai = eda_mingguan.iloc[::8]
        fig.add_trace(go.Scatter(x=tandai["week_no"], y=tandai["aktif"], mode="markers+text",
                                 text=[angka(v) for v in tandai["aktif"]], textposition="top center",
                                 showlegend=False, marker=dict(size=5)))
        fig.update_layout(title="Gambar D1. Rumah tangga aktif per minggu dan kumulatif masuk data",
                          xaxis_title="Minggu ke-", yaxis_title="Jumlah rumah tangga")
        st.plotly_chart(tata_letak(fig), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        if eda_uk is None:
            file_hilang("eda_ukuran_keranjang.csv")
        else:
            d = eda_uk.copy()
            d["label"] = [persen(v) for v in d["proporsi"]]
            fig = px.bar(d, x="ukuran", y="jumlah_keranjang", text="label",
                         title="Gambar D2. Ukuran keranjang (jumlah commodity berbeda)",
                         labels={"ukuran": "Commodity per keranjang", "jumlah_keranjang": "Jumlah keranjang"})
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(type="category")
            st.plotly_chart(tata_letak(fig), width="stretch")
    with c2:
        if eda_ulang is None:
            file_hilang("eda_porsi_ulang.csv")
        else:
            d = eda_ulang.copy()
            d["label"] = [persen(v) for v in d["porsi_ulang"]]
            d["jendela"] = d["n_minggu"].astype(str) + " minggu"
            fig = px.bar(d, x="jendela", y="porsi_ulang", text="label",
                         title="Gambar D3. Porsi pembelian yang merupakan pengulangan dalam N minggu",
                         labels={"jendela": "Jendela N", "porsi_ulang": "Proporsi pembelian"})
            fig.update_traces(textposition="outside", cliponaxis=False, marker_color="indianred")
            fig.update_yaxes(range=[0, 1.05], tickformat=".0%")
            st.plotly_chart(tata_letak(fig), width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        if eda_top is None:
            file_hilang("eda_top_commodity.csv")
        else:
            d = eda_top.head(20).iloc[::-1].copy()
            d["label"] = [persen(v) for v in d["support"]]
            fig = px.bar(d, x="support", y="commodity", orientation="h", text="label",
                         title="Gambar D4. 20 commodity dengan support tertinggi",
                         labels={"support": "Proporsi keranjang", "commodity": "Commodity"})
            fig.update_traces(textposition="outside", cliponaxis=False, marker_color="seagreen")
            fig.update_xaxes(tickformat=".0%")
            st.plotly_chart(tata_letak(fig, 600), width="stretch")
    with c4:
        if eda_jeda is None:
            file_hilang("eda_jeda_kunjungan.csv")
        else:
            d = eda_jeda.copy()
            d["label"] = [persen(v) for v in d["proporsi"]]
            fig = px.bar(d, x="jeda_hari", y="jumlah", text="label",
                         title="Gambar D5. Jarak antar-hari kunjungan rumah tangga yang sama",
                         labels={"jeda_hari": "Jarak ke kunjungan berikutnya (hari)", "jumlah": "Jumlah pasangan kunjungan"})
            fig.update_traces(textposition="outside", cliponaxis=False, marker_color="teal")
            fig.update_xaxes(type="category")
            st.plotly_chart(tata_letak(fig, 600), width="stretch")

# =====================================================================
# Halaman: RQ1
# =====================================================================
elif halaman == "RQ1: Association rule":
    st.title("RQ1: Commodity yang dibeli bersama dalam satu keranjang")
    if aturan is None:
        file_hilang("rq1_aturan_final.csv")
        st.stop()

    st.markdown("Aturan sudah lolos lift > 1, uji Fisher dengan koreksi Benjamini-Hochberg, dan pemangkasan redundansi. "
                "**Lift** = berapa kali consequent lebih sering muncul di keranjang yang memuat antecedent "
                "dibanding rata-rata semua keranjang.")

    f1, f2, f3, f4 = st.columns(4)
    min_lift = f1.slider("Lift minimal", 1.0, float(np.ceil(aturan["lift"].max())), 3.0, 0.5)
    min_conf = f2.slider("Confidence minimal", 0.0, 1.0, 0.2, 0.05)
    min_supp = f3.select_slider("Support minimal", options=[0.01, 0.0125, 0.015, 0.02, 0.03, 0.05, 0.1],
                                value=0.01, format_func=lambda v: persen(v, 2))
    jenis = f4.selectbox("Jumlah item di antecedent", ["Semua", "1 item", "2 item"])
    g1, g2 = st.columns([2, 1])
    cari = g1.text_input("Cari commodity (misalnya PASTA, CHEESE, BEEF)", "")
    unik = g2.checkbox("Satu aturan per himpunan item (lift tertinggi)", value=True,
                       help="A -> B dan B -> A memiliki support dan lift yang sama; centang agar tidak muncul dua kali.")

    d = aturan[(aturan["lift"] >= min_lift) & (aturan["confidence"] >= min_conf) & (aturan["support"] >= min_supp)].copy()
    if jenis != "Semua":
        d = d[d["jumlah_item_antecedent"] == int(jenis[0])]
    if cari.strip():
        d = d[d["aturan"].str.contains(cari.strip(), case=False, regex=False)]
    if unik and len(d):
        d["himpunan"] = [" | ".join(sorted(a.split(" + ") + [c])) for a, c in zip(d["antecedent"], d["consequent"])]
        d = d.sort_values("lift", ascending=False).drop_duplicates("himpunan")
    d = d.sort_values("lift", ascending=False)

    st.markdown(f"**{angka(len(d))}** aturan memenuhi filter (dari {angka(len(aturan))}).")
    if len(d) == 0:
        st.warning("Tidak ada aturan yang memenuhi filter. Longgarkan filter di atas.")
        st.stop()

    n_top = st.slider("Jumlah aturan pada grafik", 5, 30, 15)
    t = d.head(n_top).iloc[::-1].copy()
    t["label"] = [f"lift {angka(l, 2)} | conf {persen(c)} | supp {persen(s, 2)}"
                  for l, c, s in zip(t["lift"], t["confidence"], t["support"])]
    fig = px.bar(t, x="lift", y="aturan", orientation="h", text="label",
                 title=f"Gambar R1. {n_top} aturan dengan lift tertinggi (sesuai filter)",
                 labels={"lift": "Lift", "aturan": "Aturan (antecedent -> consequent)"})
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.add_vline(x=1, line_dash="dash", line_color="red")
    fig.update_xaxes(range=[0, t["lift"].max() * 1.6])
    st.plotly_chart(tata_letak(fig, max(420, 32 * n_top)), width="stretch")

    fig = px.scatter(d, x="support", y="confidence", color="lift", hover_name="aturan",
                     hover_data={"support": ":.4f", "confidence": ":.3f", "lift": ":.2f", "n_AB": ":,"},
                     log_x=True, color_continuous_scale="Viridis",
                     title="Gambar R2. Support vs confidence (warna = lift; arahkan kursor untuk melihat aturan)",
                     labels={"support": "Support (skala log)", "confidence": "Confidence", "lift": "Lift"})
    st.plotly_chart(tata_letak(fig, 500), width="stretch")

    tampil = d[["aturan", "support", "confidence", "lift", "n_AB", "q_value"]].rename(
        columns={"n_AB": "jumlah keranjang", "q_value": "q-value"})
    st.dataframe(tampil.style.format({"support": "{:.4f}", "confidence": "{:.3f}", "lift": "{:.2f}",
                                      "jumlah keranjang": "{:,.0f}", "q-value": "{:.1e}"}),
                 width="stretch", hide_index=True, height=420)
    st.download_button("Unduh aturan hasil filter (CSV)", tampil.to_csv(index=False).encode("utf-8"),
                       "aturan_terfilter.csv", "text/csv")
    st.caption("Catatan: hampir semua aturan signifikan karena jumlah keranjang sangat besar; "
               "penyaring yang bermakna adalah lift, confidence, dan pemangkasan redundansi.")

# =====================================================================
# Halaman: RQ2
# =====================================================================
elif halaman == "RQ2: Sequential pattern":
    st.title("RQ2: Urutan commodity baru antar-kunjungan")
    if pola2 is None:
        file_hilang("rq2_pola_panjang2.csv")
        st.stop()

    searah = pola2[pola2["searah"]].sort_values("n_rumah_tangga", ascending=False)
    fin = pola2[np.isfinite(pola2["rasio_arah"]) & pola2["peringkat_pop_A"].notna()].copy()
    fin["selisih_peringkat"] = fin["peringkat_pop_B"] - fin["peringkat_pop_A"]
    rho = fin["selisih_peringkat"].corr(np.log(fin["rasio_arah"]), method="spearman")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Pola panjang 2", angka(len(pola2)))
    k2.metric("Pola searah", angka(len(searah)))
    k3.metric("Searah dengan A lebih populer dari B",
              f"{int((searah['peringkat_pop_A'] < searah['peringkat_pop_B']).sum())} dari {len(searah)}")
    k4.metric("Korelasi arah vs selisih popularitas", angka(rho, 2))

    st.warning("Temuan utama RQ2 bersifat negatif: arah urutan sebagian besar mengikuti popularitas barang "
               "(barang yang lebih sering dibeli muncul kembali lebih dulu) dan tidak stabil terhadap N. "
               "Pola di bawah ini sebaiknya dibaca sebagai kandidat, bukan temuan.")

    tab1, tab2, tab3 = st.tabs(["Diagnostik artefak frekuensi", "Pola searah", "Sensitivitas N"])

    with tab1:
        bins = [-1000, -50, -10, 0, 10, 50, 1000]
        nama = ["A jauh kurang populer (< -50)", "-50 s.d. -10", "-10 s.d. 0",
                "0 s.d. 10", "10 s.d. 50", "A jauh lebih populer (> 50)"]
        fin["kelompok"] = pd.cut(fin["selisih_peringkat"], bins=bins, labels=nama)
        g = fin.groupby("kelompok", observed=False).agg(
            proporsi=("rasio_arah", lambda s: (s > 1).mean()), jumlah=("rasio_arah", "size")).reset_index()
        g["label"] = [f"{persen(p)} (n = {angka(n)})" for p, n in zip(g["proporsi"], g["jumlah"])]
        fig = px.bar(g, x="kelompok", y="proporsi", text="label",
                     title="Gambar S1. Proporsi pola dengan urutan A -> B lebih sering daripada B -> A, "
                           "menurut selisih popularitas",
                     labels={"kelompok": "Peringkat popularitas B dikurangi peringkat A", "proporsi": "Proporsi pola dengan rasio arah > 1"})
        fig.update_traces(textposition="outside", cliponaxis=False, marker_color="darkorange")
        fig.add_hline(y=0.5, line_dash="dash", line_color="gray",
                      annotation_text="50% = tidak ada kecenderungan arah", annotation_position="top left")
        fig.update_yaxes(range=[0, 1.05], tickformat=".0%")
        st.plotly_chart(tata_letak(fig, 480), width="stretch")
        st.markdown("Jika urutan tidak dipengaruhi popularitas, semua batang seharusnya dekat 50%. "
                    "Batang yang naik dari kiri ke kanan menunjukkan bahwa barang yang lebih populer cenderung muncul lebih dulu.")

    with tab2:
        c1, c2 = st.columns(2)
        hanya_jarang = c1.checkbox("Hanya pola dengan A di luar 20 commodity terpopuler", value=False,
                                   help="Pola seperti ini lebih kecil kemungkinannya merupakan artefak frekuensi.")
        cari = c2.text_input("Cari commodity", "")
        d = searah.copy()
        if hanya_jarang:
            d = d[d["peringkat_pop_A"] > 20]
        if cari.strip():
            d = d[d["pola"].str.contains(cari.strip(), case=False, regex=False)]
        if len(d) == 0:
            st.info("Tidak ada pola yang memenuhi filter.")
        else:
            t = d.head(15).iloc[::-1].copy()
            t["label"] = [f"{persen(s)} ({angka(n)} RT) | rasio {angka(r, 2)}"
                          for s, n, r in zip(t["support"], t["n_rumah_tangga"], t["rasio_arah"])]
            fig = px.bar(t, x="support", y="pola", orientation="h", text="label",
                         title="Gambar S2. Pola searah dengan support tertinggi (sesuai filter)",
                         labels={"support": "Support (proporsi rumah tangga)", "pola": "Pola (A -> B)"})
            fig.update_traces(textposition="outside", cliponaxis=False, marker_color="darkorange")
            fig.update_xaxes(range=[0, t["support"].max() * 1.7], tickformat=".0%")
            st.plotly_chart(tata_letak(fig, max(420, 32 * len(t))), width="stretch")
            kol = ["pola", "n_rumah_tangga", "support", "support_balik_n", "rasio_arah", "q_arah",
                   "conf_seq", "peringkat_pop_A", "peringkat_pop_B"]
            st.dataframe(d[kol].style.format({"support": "{:.3f}", "rasio_arah": "{:.2f}",
                                              "q_arah": "{:.1e}", "conf_seq": "{:.3f}"}),
                         width="stretch", hide_index=True)

    with tab3:
        if sens is None:
            file_hilang("rq2_sensitivitas_N.csv")
        else:
            st.dataframe(sens, width="stretch")
            st.markdown("Jaccard mengukur kemiripan 10 pola teratas terhadap N = 8 (1 = identik, 0 = tidak ada yang sama). "
                        "Nilai mendekati 0 berarti pola teratas berubah total saat N diubah, sehingga temuan tidak stabil.")

# =====================================================================
# Halaman: RQ3
# =====================================================================
elif halaman == "RQ3: Segmen":
    st.title("RQ3: Rumah tangga yang sering vs jarang berbelanja")
    st.markdown("Segmen dibagi pada median kunjungan per minggu (masing-masing 1.250 rumah tangga).")

    if seg_ukuran is not None:
        k1, k2, k3 = st.columns(3)
        s = seg_ukuran.set_index("segmen")
        k1.metric("Porsi keranjang dari segmen sering", persen(s.loc["sering", "porsi_keranjang"]))
        k2.metric("Median ukuran keranjang (jarang)", angka(s.loc["jarang", "median_ukuran"], 2))
        k3.metric("Median ukuran keranjang (sering)", angka(s.loc["sering", "median_ukuran"], 2))

    if seg_aturan is None:
        file_hilang("rq3_segmen_aturan.csv")
    else:
        d = seg_aturan.copy()
        d["label"] = [angka(v, 2) for v in d["lift"]]
        fig = px.bar(d, x="lift", y="aturan", color="segmen", barmode="group", orientation="h", text="label",
                     title="Gambar G1. Lift 10 aturan teratas pada segmen sering dan jarang",
                     labels={"lift": "Lift", "aturan": "Aturan", "segmen": "Segmen"},
                     color_discrete_map={"sering": "#1f77b4", "jarang": "#9e9e9e"})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(range=[0, d["lift"].max() * 1.2])
        st.plotly_chart(tata_letak(fig, 620), width="stretch")
        st.markdown("Lift kedua segmen hampir sama: pola keranjang inti tidak bergantung pada frekuensi belanja. "
                    "Belum ada uji formal untuk selisih antar-segmen.")

    if seg_pola is not None:
        with st.expander("Perbandingan pola RQ2 antar-segmen (tidak valid, lihat catatan)"):
            st.error("Syarat rumah tangga aktif (minimal sekian kunjungan dalam N minggu) secara definisi membuang "
                     "sebagian besar kejadian milik pembeli jarang. Perbedaan support antar-segmen di bawah ini "
                     "diciptakan oleh metode, bukan oleh perbedaan kebiasaan belanja.")
            d = seg_pola.copy()
            d["label"] = [persen(v) for v in d["support"]]
            fig = px.bar(d, x="support", y="pola", color="segmen", barmode="group", orientation="h", text="label",
                         title="Gambar G2. Support 10 pola searah teratas per segmen",
                         labels={"support": "Proporsi rumah tangga dalam segmen", "pola": "Pola", "segmen": "Segmen"},
                         color_discrete_map={"sering": "#ff7f0e", "jarang": "#9e9e9e"})
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(tickformat=".0%", range=[0, d["support"].max() * 1.3])
            st.plotly_chart(tata_letak(fig, 620), width="stretch")
