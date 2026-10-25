from pathlib import Path
import pandas as pd

FOLDER = Path(__file__).resolve().parent
FILE_EXCEL = FOLDER / "KelompokB_D5_Dashboard.xlsx"
FILE_CSV = FOLDER / "Data_Bersih.csv"
FOLDER_HASIL = FOLDER / "hasil_analisis"

FOLDER_HASIL.mkdir(exist_ok=True)


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
            "File Excel atau CSV tidak ditemukan."
        )

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce"
    )

    return df


df = baca_data()

print("=== PEMERIKSAAN DATA ===")
print("Jumlah baris:", len(df))
print("Jumlah kolom:", len(df.columns))
print("Jumlah baris duplikat:", df.duplicated().sum())

print("\nJumlah nilai kosong per kolom:")
print(df.isna().sum().to_string())

total_omzet = df["Omzet_Bersih_Rp"].sum()
total_transaksi = df["Jumlah_Transaksi"].sum()
total_ulasan = df["Jumlah_Ulasan"].sum()

rata_transaksi = (
    total_omzet / total_transaksi
    if total_transaksi else 0
)

rating_berbobot = (
    df["Rating_x_Ulasan"].sum() / total_ulasan
    if total_ulasan else 0
)

ringkasan = pd.DataFrame([{
    "Jumlah_Record": len(df),
    "Omzet_Bersih_Rp": total_omzet,
    "Jumlah_Transaksi": total_transaksi,
    "Rata_Nilai_Transaksi_Rp": rata_transaksi,
    "Rating_Berbobot": rating_berbobot
}])

ringkasan.to_csv(
    FOLDER_HASIL / "ringkasan_kpi.csv",
    index=False
)


outlet = (
    df.groupby("Outlet", as_index=False)
    .agg(
        Omzet_Bersih_Rp=("Omzet_Bersih_Rp", "sum"),
        Jumlah_Transaksi=("Jumlah_Transaksi", "sum"),
        Transaksi_Wisatawan=("Transaksi_Wisatawan", "sum"),
        Transaksi_Lokal=("Transaksi_Lokal", "sum")
    )
    .sort_values("Omzet_Bersih_Rp", ascending=False)
)

outlet.to_csv(
    FOLDER_HASIL / "omzet_per_outlet.csv",
    index=False
)


kanal = (
    df.groupby("Kanal_Penjualan", as_index=False)
    .agg(
        Omzet_Bersih_Rp=("Omzet_Bersih_Rp", "sum"),
        Jumlah_Transaksi=("Jumlah_Transaksi", "sum"),
        Transaksi_Wisatawan=("Transaksi_Wisatawan", "sum"),
        Transaksi_Lokal=("Transaksi_Lokal", "sum")
    )
    .sort_values("Omzet_Bersih_Rp", ascending=False)
)

kanal.to_csv(
    FOLDER_HASIL / "omzet_per_kanal.csv",
    index=False
)

bulanan = (
    df.groupby(["Bulan_No", "Bulan"], as_index=False)
    .agg(
        Omzet_Bersih_Rp=("Omzet_Bersih_Rp", "sum"),
        Jumlah_Transaksi=("Jumlah_Transaksi", "sum"),
        Transaksi_Wisatawan=("Transaksi_Wisatawan", "sum"),
        Transaksi_Lokal=("Transaksi_Lokal", "sum")
    )
    .sort_values("Bulan_No")
)

bulanan.to_csv(
    FOLDER_HASIL / "omzet_per_bulan.csv",
    index=False
)


print("\n=== RINGKASAN KPI ===")
print(ringkasan.to_string(index=False))

print("\n=== OMZET PER OUTLET ===")
print(outlet.to_string(index=False))

print("\n=== OMZET PER KANAL ===")
print(kanal.to_string(index=False))

print("\n=== OMZET PER BULAN ===")
print(bulanan.to_string(index=False))

print(
    "\nHasil analisis tersimpan di folder:",
    FOLDER_HASIL
)