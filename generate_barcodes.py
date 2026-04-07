import barcode
from barcode.writer import ImageWriter
import os

# ── All products (original 4 + new 10) ──
products = [
    # Original products
    ("Coca_Cola_500ml",    "123456789"),
    ("Bread_Loaf",         "987654321"),
    ("Rice_1kg",           "111222333"),
    ("Milk_1L",            "444555666"),

    # New products
    ("Milo_400g",          "555666777"),
    ("Sugar_1kg",          "666777888"),
    ("Cooking_Oil_1L",     "777888999"),
    ("Tuna_Can_170g",      "888999000"),
    ("Cabin_Biscuits",     "100200300"),
    ("Indomie_Noodles",    "200300400"),
    ("Tomato_Paste_70g",   "300400500"),
    ("Canola_Soap",        "400500600"),
    ("Detergent_500g",     "500600700"),
    ("Bottled_Water_500ml","600700800"),
]

# ── Output folder ──
output_folder = "barcodes"
os.makedirs(output_folder, exist_ok=True)

print("Generating barcodes for all products...\n")

success = 0
failed  = 0

for name, code in products:
    padded = code.zfill(12)
    filepath = os.path.join(output_folder, name)
    try:
        ean = barcode.get("ean13", padded, writer=ImageWriter())
        ean.save(filepath)
        print(f"[OK]  {name}.png")
        success += 1
    except Exception:
        try:
            code128 = barcode.get("code128", code, writer=ImageWriter())
            code128.save(filepath)
            print(f"[OK]  {name}.png  (Code128 fallback)")
            success += 1
        except Exception as e:
            print(f"[ERR] {name} — {e}")
            failed += 1

print(f"\n✅ Done! {success} barcode(s) saved in '{output_folder}/' folder.")
if failed:
    print(f"⚠️  {failed} barcode(s) failed — check errors above.")
print("\nYou can open and print them from the barcodes folder.")
