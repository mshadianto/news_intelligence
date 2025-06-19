import sqlite3
import os

# 1. Cetak lokasi kerja saat ini untuk memastikan kita ada di tempat yang benar.
cwd = os.getcwd()
print(f"Direktori kerja saat ini: {cwd}")
print("-" * 20)

db_file = "test_database.db"
print(f"Mencoba membuat/menyambung ke database: {db_file}")

try:
    # 2. Coba buat koneksi. Ini seharusnya membuat file jika belum ada.
    conn = sqlite3.connect(db_file)
    conn.close() # Langsung tutup koneksi setelah berhasil.
    print("Perintah sqlite3.connect() berhasil dijalankan tanpa error.")

    # 3. Periksa apakah file benar-benar ada di disk setelah perintah di atas.
    if os.path.exists(os.path.join(cwd, db_file)):
        print("\n[ HASIL: BERHASIL! ]")
        print("File 'test_database.db' berhasil dibuat di direktori di atas.")
        print("Ini berarti Python dan izin folder Anda SEBENARNYA BISA membuat file.")
    else:
        print("\n[ HASIL: ANEH! ]")
        print("Koneksi berhasil, TAPI file tidak ditemukan di disk.")
        print("Ini bisa jadi indikasi masalah dengan Antivirus atau keamanan sistem.")

except Exception as e:
    # 4. Jika ada error APAPUN saat koneksi, kita akan menangkapnya di sini.
    print(f"\n[ HASIL: GAGAL TOTAL! ]")
    print("Terjadi error saat mencoba menyambung ke database:")
    print(f"Tipe Error: {type(e).__name__}")
    print(f"Pesan Error: {e}")