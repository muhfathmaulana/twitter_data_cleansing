import sqlite3
import pandas as pd
import re
from typing import Union, List, Tuple
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import csv

app = FastAPI()

# Membuat koneksi ke database SQLite
conn = sqlite3.connect('kamus_alay.db')
cursor = conn.cursor()

# Membuat tabel kamus_alay jika belum ada
cursor.execute('''CREATE TABLE IF NOT EXISTS kamus_alay (
                    kata_tidak_baku TEXT PRIMARY KEY,
                    kata_baku TEXT
                )''')

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

kamus_df = pd.read_csv("new_kamusalay.csv", 
                       encoding='latin-1', 
                       header=None, 
                       names=["kata_tidak_baku", "kata_baku"])
kamus = dict(zip(kamus_df["kata_tidak_baku"], kamus_df["kata_baku"]))

def update_kamus_alay(new_data: dict):
    # Menambahkan data baru ke tabel kamus_alay
    for kata_tidak_baku, kata_baku in new_data.items():
        cursor.execute("INSERT OR REPLACE INTO kamus_alay (kata_tidak_baku, kata_baku) VALUES (?, ?)", (kata_tidak_baku, kata_baku))
    conn.commit()

    # Menambahkan data baru ke file new_kamusalay.csv
    with open("new_kamusalay.csv", 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for kata_tidak_baku, kata_baku in new_data.items():
            writer.writerow([kata_tidak_baku, kata_baku])

@app.post("/update/kamus_alay")
async def update_kamus(new_data: dict):
    update_kamus_alay(new_data)
    return {"message": "Kamus alay berhasil diperbarui"}

@app.post("/items/text_cleansing")
def update_item(text: str):
    # Buat regex pattern dari dictionary
    pattern = re.compile(r'\b(?:' + '|'.join(re.escape(k) for k in kamus.keys()) + r')\b', re.IGNORECASE)

    # Fungsi untuk mengganti kata tidak baku dengan kata baku
    def ganti_kata(match):
        return kamus[match.group(0).lower()]

    # Gunakan regex untuk mengganti kata tidak baku
    cleaned_text = pattern.sub(ganti_kata, text)
    cleaned_text2 = re.sub(r"\\dan", " ", cleaned_text)
    cleaned_text3 = re.sub(r"\\\w\d\d|\\\w\w\d|\\\w\d\w|\\\w\w\w|USER|RT", "", cleaned_text2)
    cleaned_text4 = re.sub(r"[^a-zA-Z0-9\s$#,.]", "", cleaned_text3)
    
    return {"cleaned_text": cleaned_text4}

@app.post("/clean/csv")
async def clean_csv(file: UploadFile = File(...)):
    if file.filename.endswith('.csv'):
        contents = await file.read()
        decoded_contents = contents.decode('latin-1').splitlines()

        # Gabungkan semua baris menjadi satu string tunggal
        cleaned_text = '\n'.join(decoded_contents)

        # Buat regex pattern dari dictionary
        pattern = re.compile(r'\b(?:' + '|'.join(re.escape(k) for k in kamus.keys()) + r')\b', re.IGNORECASE)

        # Fungsi untuk mengganti kata tidak baku dengan kata baku
        def ganti_kata(match):
            return kamus[match.group(0).lower()]

        # Lakukan pembersihan teks menggunakan regex
        cleaned_text0 = pattern.sub(ganti_kata, cleaned_text)
        cleaned_text2 = re.sub(r"\\dan", " ", cleaned_text0)
        cleaned_text3 = re.sub(r"\\\w\d\d|\\\w\w\d|\\\w\d\w|\\\w\w\w", "", cleaned_text2)
        cleaned_text4 = re.sub(r"[^a-zA-Z0-9\s$#,.]", "", cleaned_text3)
        cleaned_text5 = re.sub(r"\t|,00|RT|pengguna|uniform|resource|locator", "", cleaned_text4)
        cleaned_text6 = re.sub(r",(?=\d)", "\t", cleaned_text5)
        
        # Tulis data yang telah dibersihkan ke file CSV baru
        output_file_path = "cleaned_file.csv"
        with open(output_file_path, 'w', newline='') as csvfile:
            csvfile.write(cleaned_text6)

        # Kembalikan file CSV yang telah dibersihkan sebagai respons
        return FileResponse(output_file_path, media_type='text/csv')
    else:
        return {"error": "File harus berformat CSV"}

