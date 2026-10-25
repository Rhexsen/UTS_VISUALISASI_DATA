from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard Gudeg Sekar Arum",
    page_icon="🍲",
    layout="wide"
)

FOLDER = Path(__file__).resolve().parent
FILE_EXCEL = FOLDER / "KelompokB_D5_Dashboard.xlsx"
FILE_CSV = FOLDER / "Data_Bersih.csv"


@st.cache_data
def baca_data():
    if FILE_EXCEL.exists():
        df = pd.read_excel(
            FILE_EXCEL,
            sheet_name="Data_Bersih"
        )
    elif FILE_CSV.exists():
        df = pd.read_csv(FILE_CSV)
    else:
        raise FileNotFoundError(
            "File Excel atau Data_Bersih.csv tidak ditemukan."
        )

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"], errors="coerce"
    )

    return df


try:
    data = baca_data()
except Exception as error:
    st.error(f"Data gagal dibaca: {error}")
    st.stop()

kolom_wajib = [
    "Tanggal",
    "Bulan",
    "Bulan_No",
    "Outlet",
    "Kanal_Penjualan",
    "Jumlah_Transaksi",
    "Transaksi_Wisatawan",
    "Transaksi_Lokal",
    "Omzet_Bersih_Rp",
    "Rating_x_Ulasan",
    "Jumlah_Ulasan"
]

kolom_hilang = [
    kolom for kolom in kolom_wajib
    if kolom not in data.columns
]

if kolom_hilang:
    st.error(
        "Kolom berikut tidak ditemukan: "
        + ", ".join(kolom_hilang)
    )
    st.stop()

st.title("Dashboard Penjualan Gudeg Sekar Arum")
st.caption(
    "Ringkasan kinerja penjualan berdasarkan data tahun 2025."
)

with st.sidebar:
    st.header("Filter Data")

    daftar_outlet = sorted(
        data["Outlet"].dropna().unique().tolist()
    )

    daftar_kanal = sorted(
        data["Kanal_Penjualan"].dropna().unique().tolist()
    )

    daftar_bulan = (
        data[["Bulan", "Bulan_No"]]
        .dropna()
        .drop_duplicates()
        .sort_values("Bulan_No")["Bulan"]
        .tolist()
    )

    outlet_pilihan = st.multiselect(
        "Pilih outlet",
        daftar_outlet,
        default=daftar_outlet
    )

    kanal_pilihan = st.multiselect(
        "Pilih kanal penjualan",
        daftar_kanal,
        default=daftar_kanal
    )

    bulan_pilihan = st.multiselect(
        "Pilih bulan",
        daftar_bulan,
        default=daftar_bulan
    )

hasil = data[
    data["Outlet"].isin(outlet_pilihan)
    & data["Kanal_Penjualan"].isin(kanal_pilihan)
    & data["Bulan"].isin(bulan_pilihan)
].copy()

if hasil.empty:
    st.warning(
        "Tidak ada data yang sesuai dengan filter."
    )
    st.stop()

total_omzet = hasil["Omzet_Bersih_Rp"].sum()
total_transaksi = hasil["Jumlah_Transaksi"].sum()

rata_transaksi = (
    total_omzet / total_transaksi
    if total_transaksi > 0 else 0
)

total_ulasan = hasil["Jumlah_Ulasan"].sum()

rating_berbobot = (
    hasil["Rating_x_Ulasan"].sum() / total_ulasan
    if total_ulasan > 0 else 0
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Omzet Bersih",
    f"Rp{total_omzet:,.0f}"
)

k2.metric(
    "Jumlah Transaksi",
    f"{total_transaksi:,.0f}"
)

k3.metric(
    "Rata-rata Nilai Transaksi",
    f"Rp{rata_transaksi:,.0f}"
)

k4.metric(
    "Rating Berbobot",
    f"{rating_berbobot:.2f} / 5"
)


st.divider()

kiri, kanan = st.columns(2)

with kiri:
    st.subheader("Tren Omzet Bulanan")

    bulanan = (
        hasil.groupby(
            ["Bulan_No", "Bulan"],
            as_index=False
        )
        .agg(
            Omzet_Bersih_Rp=(
                "Omzet_Bersih_Rp", "sum"
            )
        )
        .sort_values("Bulan_No")
    )

    grafik_bulanan = px.line(
        bulanan,
        x="Bulan",
        y="Omzet_Bersih_Rp",
        markers=True,
        labels={
            "Bulan": "Bulan",
            "Omzet_Bersih_Rp": "Omzet Bersih (Rp)"
        }
    )

    st.plotly_chart(
        grafik_bulanan,
        use_container_width=True
    )


with kanan:
    st.subheader("Perbandingan Omzet Antaroutlet")

    per_outlet = (
        hasil.groupby("Outlet", as_index=False)
        .agg(
            Omzet_Bersih_Rp=(
                "Omzet_Bersih_Rp", "sum"
            )
        )
        .sort_values(
            "Omzet_Bersih_Rp",
            ascending=False
        )
    )

    grafik_outlet = px.bar(
        per_outlet,
        x="Outlet",
        y="Omzet_Bersih_Rp",
        labels={
            "Outlet": "Outlet",
            "Omzet_Bersih_Rp": "Omzet Bersih (Rp)"
        }
    )

    st.plotly_chart(
        grafik_outlet,
        use_container_width=True
    )

kiri, kanan = st.columns(2)

with kiri:
    st.subheader("Omzet Berdasarkan Kanal")

    per_kanal = (
        hasil.groupby(
            "Kanal_Penjualan",
            as_index=False
        )
        .agg(
            Omzet_Bersih_Rp=(
                "Omzet_Bersih_Rp", "sum"
            )
        )
        .sort_values(
            "Omzet_Bersih_Rp",
            ascending=False
        )
    )

    grafik_kanal = px.bar(
        per_kanal,
        x="Kanal_Penjualan",
        y="Omzet_Bersih_Rp",
        labels={
            "Kanal_Penjualan": "Kanal Penjualan",
            "Omzet_Bersih_Rp": "Omzet Bersih (Rp)"
        }
    )

    st.plotly_chart(
        grafik_kanal,
        use_container_width=True
    )

with kanan:
    st.subheader("Komposisi Segmen Pelanggan")

    komposisi = pd.DataFrame({
        "Segmen": [
            "Wisatawan",
            "Pelanggan Lokal"
        ],
        "Jumlah Transaksi": [
            hasil["Transaksi_Wisatawan"].sum(),
            hasil["Transaksi_Lokal"].sum()
        ]
    })

    grafik_segmen = px.pie(
        komposisi,
        names="Segmen",
        values="Jumlah Transaksi",
        hole=0.4
    )

    st.plotly_chart(
        grafik_segmen,
        use_container_width=True
    )

st.subheader("Rincian Data")

kolom_tabel = [
    "Tanggal",
    "Outlet",
    "Kanal_Penjualan",
    "Jumlah_Transaksi",
    "Transaksi_Wisatawan",
    "Transaksi_Lokal",
    "Omzet_Bersih_Rp"
]

kolom_tabel = [
    kolom for kolom in kolom_tabel
    if kolom in hasil.columns
]

st.dataframe(
    hasil[kolom_tabel].sort_values("Tanggal"),
    use_container_width=True,
    hide_index=True
)

csv = hasil.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="Unduh Data Hasil Filter",
    data=csv,
    file_name="data_gudeg_hasil_filter.csv",
    mime="text/csv"
)

st.caption(
    "Omzet bersih bukan laba. Dataset ini digunakan "
    "untuk menganalisis pola penjualan tahun 2025."
)