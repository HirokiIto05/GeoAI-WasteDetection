# 02.code/assign_files.py
# Assign tiles to waste / non-waste folders and train/val/test subfolders

from pathlib import Path
import shutil
import random

import geopandas as gpd
import pandas as pd

from pyprojroot.here import here

# ====== Basic path settings ======
base_filename = "690585b76415e43597ffd7eb_complete_"

# ====== Load GeoJSON and preprocess ======
df_merged_raw = gpd.read_file(
    here("01_data/points/merged.geojson")
)

df_merged = (
    df_merged_raw
    .assign(
        is_waste = df_merged_raw["layer"] == "waste_point"
    )[["id", "is_waste", "row", "col", "geometry"]]
    .sort_values(["id", "row", "col"])
)
df_merged["row"] = df_merged["row"].astype(int)
df_merged["col"] = df_merged["col"].astype(int)

# ====== Generate a list of filenames for waste / non-waste ======
def generate_list_files(df_merged, is_waste_i):

    subset = df_merged[df_merged["is_waste"] == is_waste_i].copy()
    subset["file_path"] = (
        "r" + subset["row"].astype(str)
        + "_c" + subset["col"].astype(str)
        + ".tif"
    )

    return subset["file_path"].tolist()

# ====== Assign files to train / val / test subfolders ======
def assign_files(list_files, category_i: str, folder_name_i: str):
    """
    list_files: list of filenames
    category_i: "train", "val", or "test"
    folder_name: "waste" or "non_waste"
    """
    for fname in list_files:
        src = "01.data/raw/tiles/" + fname
        dst = "01.data/raw/images" + "/" + category_i + "/" + folder_name_i + "/" + fname
        src_path = here(src)
        dst_path = here(dst)
        if Path(src_path).exists():
            shutil.copy2(src_path, dst_path)
        else:
            print(f"File not found, skipped: {src_path}")

def copy_files_to_category(df_merged, is_waste_i: bool):

    if is_waste_i:
        folder_name_i = "waste"
    else:
        folder_name_i = "non_waste"

    # List all files in waste / non_waste folder
    list_files = generate_list_files(df_merged, is_waste_i)

    total_n = len(list_files)
    idx = list(range(total_n))

    random.seed(1111)  # Equivalent to R's set.seed(1111)
    random.shuffle(idx)

    # 70% train, 15% val, 15% test
    train_n = int(total_n * 0.7)
    val_n   = int(total_n * 0.15)
    test_n  = total_n - train_n - val_n

    list_files_train = [list_files[i] for i in idx[0:train_n]]
    list_files_val   = [list_files[i] for i in idx[train_n:train_n+val_n]]
    list_files_test  = [list_files[i] for i in idx[train_n+val_n:total_n]]

    assign_files(list_files_train, "train", folder_name_i)
    assign_files(list_files_val,   "val",   folder_name_i)
    assign_files(list_files_test,  "test",  folder_name_i)


# Split into train/val/test for waste and non-waste
copy_files_to_category(True)
copy_files_to_category(False)
