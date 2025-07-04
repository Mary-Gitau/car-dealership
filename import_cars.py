import csv
from main import app
from models import db, Car

with app.app_context():
    with open('cars.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        added = 0
        skipped = 0

        for row in reader:
            name = row['name'].strip()
            brand = row['brand'].strip()
            year = int(row['year'])
            description = row['description'].strip()
            price = float(row['price'])
            image = row['image'].strip()

            existing = Car.query.filter_by(name=name, year=year).first()
            if existing:
                skipped += 1
                continue

            car = Car(
                name=name,
                brand=brand,
                year=year,
                description=description,
                price=price,
                image=image
            )
            db.session.add(car)
            added += 1

        db.session.commit()
        print(f"✅ Import complete: {added} cars added, {skipped} skipped (duplicates).")


