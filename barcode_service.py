import requests
from pyzbar.pyzbar import decode
from PIL import Image
from database import SessionLocal, ProductCache


def read_barcode(image_path):
    image = Image.open(image_path)
    codes = decode(image)

    if not codes:
        return None

    return codes[0].data.decode()


def get_product_by_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    cached_product = get_cached_product(barcode)

    if cached_product:
        print(f"CACHE HIT: {barcode}")
        return cached_product

    headers = {
        "User-Agent": "FoodTracerBot/1.0"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    data = response.json()

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    nutriments = product.get("nutriments", {})

    product_name = (
        product.get("product_name")
        or product.get("product_name_en")
        or product.get("generic_name")
        or "Unknown product"
    )

    brand = product.get("brands", "")

    calories = (
        nutriments.get("energy-kcal_100g")
        or nutriments.get("energy-kcal")
        or 0
    )

    protein = (
        nutriments.get("proteins_100g")
        or nutriments.get("protein_100g")
        or 0
    )

    product_data = {
    "barcode": barcode,
    "name": product_name,
    "brand": brand,
    "calories_per_100g": float(calories or 0),
    "protein_per_100g": float(protein or 0),
    }

    save_to_cache(product_data)

    return product_data

def get_cached_product(barcode):
    db = SessionLocal()

    product = (
        db.query(ProductCache)
        .filter(ProductCache.barcode == barcode)
        .first()
    )

    db.close()

    if not product:
        return None

    return {
        "barcode": product.barcode,
        "name": product.name,
        "brand": product.brand,
        "calories_per_100g": product.calories_per_100g,
        "protein_per_100g": product.protein_per_100g,
    }

    print(f"CACHE HIT: {barcode}", flush=True)

def save_to_cache(product):
    db = SessionLocal()

    existing = (
        db.query(ProductCache)
        .filter(ProductCache.barcode == product["barcode"])
        .first()
    )

    if not existing:
        db.add(
            ProductCache(
                barcode=product["barcode"],
                name=product["name"],
                brand=product["brand"],
                calories_per_100g=product["calories_per_100g"],
                protein_per_100g=product["protein_per_100g"],
            )
        )

        db.commit()

    db.close()

    print(
    f"PRODUCT CACHED: {product['name']} ({product['barcode']})",
    flush=True
    )