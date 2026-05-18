# Dokumentasi Fitur Baru - Import Data

## Fitur yang Ditambahkan

### 1. **Upload Excel (.xls / .xlsx)** 📋
- **Deskripsi**: Memungkinkan user untuk mengupload file Excel dan menggunakannya sebagai data untuk chatbot
- **Format File**: `.xls` dan `.xlsx`
- **Fungsi**: `load_xls()` di `backend.py`
- **Implementasi**: Menggunakan library `openpyxl`
- **Cara Kerja**: File Excel dibaca dan dikonversi menjadi DataFrame pandas

### 2. **Upload SQL File (.sql)** 📄
- **Deskripsi**: Memungkinkan user untuk mengupload file SQL dump dan mengekstrak data dari tabel yang ada
- **Format File**: `.sql`
- **Fungsi**: `load_sql()` di `backend.py`
- **Implementasi**: SQL statements dijalankan pada SQLite in-memory database
- **Cara Kerja**: 
  - File SQL di-parse dan dijalankan
  - Tabel pertama yang ditemukan akan dimuat sebagai data
  - Data ditampilkan dalam bentuk DataFrame pandas

## Perubahan File

### 1. **requirements.txt**
- Tambahan: `openpyxl` (untuk membaca file Excel)

### 2. **backend.py**
- Tambahan 2 fungsi baru:
  - `load_sql(uploaded_file)` - untuk membaca file SQL
  - `load_xls(uploaded_file)` - untuk membaca file Excel

### 3. **app.py**
- Update import untuk `load_sql` dan `load_xls`
- Tambah 2 menu pilihan baru di selectbox:
  - "📋 Upload Excel (.xls/.xlsx)"
  - "📄 SQL File (.sql)"
- Tambah 2 blok kondisional baru untuk handling Excel dan SQL upload

## Cara Penggunaan

### Upload Excel
1. Pilih "📋 Upload Excel (.xls/.xlsx)" dari menu "Pilih Sumber Data"
2. Klik untuk upload file Excel
3. Data akan ditampilkan dan siap digunakan

### Upload SQL
1. Pilih "📄 SQL File (.sql)" dari menu "Pilih Sumber Data"
2. Klik untuk upload file SQL
3. Data dari tabel pertama akan ditampilkan dan siap digunakan

## Catatan Penting

- ✅ Tidak ada perubahan pada kode yang sudah ada (CSV, SQLite, MySQL)
- ✅ Struktur dan pattern UI/UX tetap konsisten
- ✅ Error handling yang sama seperti fitur yang sudah ada
- ✅ Semua fungsi mengikuti pola yang sudah diterapkan
- ✅ Session state tetap berfungsi normal

## Dependencies Tambahan

```
openpyxl   # Untuk membaca file Excel
```

Sudah ditambahkan ke `requirements.txt`. Install dengan:
```bash
pip install -r requirements.txt
```
