# =========================================================
# BACKEND LOGIC & LLM FUNCTIONS
# =========================================================

import requests
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
from utilities import PRIMARY_API_KEY, BACKUP_API_KEY, MODEL_NAME, create_llm_payload

# =========================================================
# LLM FUNCTION
# =========================================================

def ask_llm(prompt):
    """Send prompt to LLM API with fallback API keys"""
    
    api_keys = [
        PRIMARY_API_KEY,
        BACKUP_API_KEY
    ]

    payload = create_llm_payload(prompt)

    for api_key in api_keys:

        try:

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:

                result = response.json()

                return result["choices"][0]["message"]["content"]

        except:
            continue

    return "❌ Semua API gagal. Silakan coba lagi."


# =========================================================
# CSV LOADER
# =========================================================

def load_csv(uploaded_file):
    """Load CSV file and return dataframe"""
    try:
        df = pd.read_csv(uploaded_file)
        return df, True, "✅ CSV berhasil diupload!"
    except Exception as e:
        return None, False, f"❌ Error: {str(e)}"


# =========================================================
# SQLITE FUNCTIONS
# =========================================================

def get_sqlite_tables(sqlite_file):
    """Get list of tables from SQLite file"""
    try:
        with open("temp.db", "wb") as f:
            f.write(sqlite_file.read())

        conn = sqlite3.connect("temp.db")

        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table';",
            conn
        )

        table_list = tables["name"].tolist()
        return table_list, True, "✅ File SQLite berhasil dibaca!"
    except Exception as e:
        return [], False, f"❌ Error: {str(e)}"


def load_sqlite_table(table_name):
    """Load specific table from SQLite"""
    try:
        conn = sqlite3.connect("temp.db")

        df = pd.read_sql(
            f"SELECT * FROM {table_name}",
            conn
        )

        return df, True, "✅ Tabel berhasil dimuat!"
    except Exception as e:
        return None, False, f"❌ Error: {str(e)}"


# =========================================================
# MYSQL FUNCTIONS
# =========================================================

def connect_mysql(host, user, password, database):
    """Connect to MySQL database"""
    try:
        engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}/{database}"
        )

        tables = pd.read_sql(
            "SHOW TABLES",
            engine
        )

        table_list = tables.iloc[:, 0].tolist()

        return engine, table_list, True, "✅ Berhasil connect!"
    except Exception as e:
        return None, [], False, f"❌ Error: {str(e)}"


def load_mysql_table(engine, table_name):
    """Load specific table from MySQL"""
    try:
        df = pd.read_sql(
            f"SELECT * FROM {table_name}",
            engine
        )

        return df, True, "✅ Tabel berhasil dimuat!"
    except Exception as e:
        return None, False, f"❌ Error membaca tabel: {str(e)}"


# =========================================================
# SQL LOADER (SQL DUMP FILE)
# =========================================================

def get_sql_tables(uploaded_file):
    """Get list of tables from SQL file"""
    try:
        sql_content = uploaded_file.read().decode('utf-8')
        
        # Better filtering untuk statement yang tidak kompatibel
        lines = []
        
        for line in sql_content.split('\n'):
            line_stripped = line.strip()
            line_upper = line_stripped.upper()
            
            if not line_stripped or line_stripped.startswith('--'):
                continue
            
            if any(skip in line_upper for skip in [
                'SET SQL_MODE',
                'SET @',
                'START TRANSACTION',
                'COMMIT',
                'SET time_zone',
                'SET CHARACTER',
                'SET NAMES',
                '/*!40',
                'LOCK TABLES',
                'UNLOCK TABLES'
            ]):
                continue
            
            if 'ALTER TABLE' in line_upper and 'MODIFY' in line_upper:
                continue
            
            if 'AUTO_INCREMENT' in line_upper and '=' in line_upper:
                continue
            
            if line_upper.startswith('USE '):
                continue
            
            lines.append(line_stripped)
        
        cleaned_content = '\n'.join(lines)
        
        cleaned_content = cleaned_content.replace('ENGINE=InnoDB', '')
        cleaned_content = cleaned_content.replace('DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci', '')
        cleaned_content = cleaned_content.replace('COLLATE=utf8mb4_general_ci', '')
        cleaned_content = cleaned_content.replace('CHARACTER SET utf8mb4', '')
        
        # Simpan content ke session state (temp file)
        with open("temp_sql.db", "w", encoding='utf-8') as f:
            f.write(cleaned_content)
        
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        statements = cleaned_content.split(';')
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except sqlite3.OperationalError:
                    continue
        
        conn.commit()
        
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table';",
            conn
        )
        
        table_list = tables["name"].tolist()
        conn.close()
        
        return table_list, True, "✅ File SQL berhasil dibaca!"
    except Exception as e:
        return [], False, f"❌ Error: {str(e)}"


def load_sql_table(table_name):
    """Load specific table from SQL file"""
    try:
        # Baca temp file yang sudah disimpan
        with open("temp_sql.db", "r", encoding='utf-8') as f:
            cleaned_content = f.read()
        
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        statements = cleaned_content.split(';')
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except sqlite3.OperationalError:
                    continue
        
        conn.commit()
        
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        return df, True, "✅ Tabel berhasil dimuat!"
    except Exception as e:
        return None, False, f"❌ Error membaca tabel: {str(e)}"


def load_sql(uploaded_file):
    """Load SQL file and extract data from CREATE/INSERT statements (DEPRECATED - use get_sql_tables)"""
    try:
        sql_content = uploaded_file.read().decode('utf-8')
        
        lines = []
        
        for line in sql_content.split('\n'):
            line_stripped = line.strip()
            line_upper = line_stripped.upper()
            
            if not line_stripped or line_stripped.startswith('--'):
                continue
            
            if any(skip in line_upper for skip in [
                'SET SQL_MODE',
                'SET @',
                'START TRANSACTION',
                'COMMIT',
                'SET time_zone',
                'SET CHARACTER',
                'SET NAMES',
                '/*!40',
                'LOCK TABLES',
                'UNLOCK TABLES'
            ]):
                continue
            
            if 'ALTER TABLE' in line_upper and 'MODIFY' in line_upper:
                continue
            
            if 'AUTO_INCREMENT' in line_upper and '=' in line_upper:
                continue
            
            if line_upper.startswith('USE '):
                continue
            
            lines.append(line_stripped)
        
        cleaned_content = '\n'.join(lines)
        
        cleaned_content = cleaned_content.replace('ENGINE=InnoDB', '')
        cleaned_content = cleaned_content.replace('DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci', '')
        cleaned_content = cleaned_content.replace('COLLATE=utf8mb4_general_ci', '')
        cleaned_content = cleaned_content.replace('CHARACTER SET utf8mb4', '')
        
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        statements = cleaned_content.split(';')
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except sqlite3.OperationalError:
                    continue
        
        conn.commit()
        
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table';",
            conn
        )
        
        table_list = tables["name"].tolist()
        
        if not table_list:
            return None, False, "❌ Tidak ada tabel ditemukan dalam file SQL"
        
        first_table = table_list[0]
        df = pd.read_sql(f"SELECT * FROM {first_table}", conn)
        
        conn.close()
        
        return df, True, f"✅ SQL berhasil diupload! (Tabel: {first_table})"
    except Exception as e:
        return None, False, f"❌ Error: {str(e)}"


# =========================================================
# EXCEL LOADER (.XLS / .XLSX)
# =========================================================

def load_xls(uploaded_file):
    """Load XLS/XLSX file and return dataframe"""
    try:
        df = pd.read_excel(uploaded_file)
        return df, True, "✅ Excel berhasil diupload!"
    except Exception as e:
        return None, False, f"❌ Error: {str(e)}"
