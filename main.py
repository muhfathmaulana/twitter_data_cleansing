import sqlite3
import pandas as pd
import regex as re
from typing import Union, List, Tuple
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

kamus_df = pd.read_csv("C:\\Users\\MyBook SAGA 12\\new_kamusalay.csv", 
                       encoding='latin-1', 
                       header=None, 
                       names=["kata_tidak_baku", "kata_baku"])
kamus = dict(zip(kamus_df["kata_tidak_baku"], kamus_df["kata_baku"]))


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

    cleaned_text3 = re.sub(r"\\\w\d\d|\\\w\w\d|\\\w\d\w|\\\w\w\w", "", cleaned_text2)

    cleaned_text4 = re.sub(r"[^a-zA-Z0-9\s$#]", "", cleaned_text3)


    return {"cleaned_text": cleaned_text4}