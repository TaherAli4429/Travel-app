from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.destination import Destination

SEED_DESTINATIONS = [
    {
        "id": "dest_1",
        "name": "Bali",
        "country": "Indonesia",
        "category": "Beaches",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.9,
        "reviews_count": 384,
        "price": "$450 / person",
        "description": "Tropical paradise known for its forested volcanic mountains, iconic rice paddies, beaches, coral reefs, and vibrant cultural heritage.",
        "is_featured": True,
    },
    {
        "id": "dest_2",
        "name": "Swiss Alps",
        "country": "Switzerland",
        "category": "Mountains",
        "image_url": "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.88,
        "reviews_count": 290,
        "price": "$820 / person",
        "description": "Dramatic alpine peaks, crystalline glacial lakes, and world-class skiing, hiking, and picturesque mountain chalets.",
        "is_featured": False,
    },
    {
        "id": "dest_3",
        "name": "Santorini",
        "country": "Greece",
        "category": "Beaches",
        "image_url": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.95,
        "reviews_count": 512,
        "price": "$680 / person",
        "description": "Whitewashed cubiform cliffside villages overlooking the azure Aegean caldera, famous for world-renowned sunsets and volcanic beaches.",
        "is_featured": False,
    },
    {
        "id": "dest_4",
        "name": "Kyoto",
        "country": "Japan",
        "category": "Cities",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.92,
        "reviews_count": 430,
        "price": "$550 / person",
        "description": "Historic heart of Japan, featuring ancient Buddhist temples, serene bamboo groves, traditional wooden machiya houses, and cherry blossoms.",
        "is_featured": False,
    },
    {
        "id": "dest_5",
        "name": "Maldives",
        "country": "Maldives",
        "category": "Resorts",
        "image_url": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.97,
        "reviews_count": 610,
        "price": "$950 / person",
        "description": "Luxury overwater bungalows, turquoise shallow lagoons, and vibrant manta ray and turtle coral reefs in the Indian Ocean.",
        "is_featured": False,
    },
    {
        "id": "dest_6",
        "name": "Dubai",
        "country": "United Arab Emirates",
        "category": "Cities",
        "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.85,
        "reviews_count": 345,
        "price": "$620 / person",
        "description": "Futuristic desert metropolis boasting Burj Khalifa, expansive luxury shopping, desert safaris, and ultramodern waterfront attractions.",
        "is_featured": False,
    },
    {
        "id": "dest_7",
        "name": "Banff National Park",
        "country": "Canada",
        "category": "Camping",
        "image_url": "https://images.unsplash.com/photo-1503614472-8c93d56e92ce?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.91,
        "reviews_count": 275,
        "price": "$490 / person",
        "description": "Majestic Canadian Rockies, pristine turquoise Lake Louise, thermal hot springs, and awe-inspiring hiking trails.",
        "is_featured": False,
    },
    {
        "id": "dest_8",
        "name": "Queenstown",
        "country": "New Zealand",
        "category": "Adventure",
        "image_url": "https://images.unsplash.com/photo-1507699622108-4be3abd695ad?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.89,
        "reviews_count": 198,
        "price": "$710 / person",
        "description": "World adventure hub on the shores of Lake Wakatipu, set against the dramatic Southern Alps, famous for bungee jumping and skydiving.",
        "is_featured": False,
    },
    {
        "id": "dest_9",
        "name": "Amalfi Coast",
        "country": "Italy",
        "category": "Resorts",
        "image_url": "https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=1000&q=80",
        "rating": 4.93,
        "reviews_count": 420,
        "price": "$780 / person",
        "description": "Picturesque Italian coastline featuring colorful pastel cliffside towns, Mediterranean lemon groves, and scenic coastal road drives.",
        "is_featured": False,
    },
]


def seed_destinations(db: Session = None):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        inserted_count = 0
        updated_count = 0

        for data in SEED_DESTINATIONS:
            dest = db.query(Destination).filter(Destination.id == data["id"]).first()
            if not dest:
                new_dest = Destination(**data)
                db.add(new_dest)
                inserted_count += 1
            else:
                for key, value in data.items():
                    setattr(dest, key, value)
                updated_count += 1

        db.commit()
        print(f"Seed completed: {inserted_count} destinations inserted, {updated_count} updated.")
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    seed_destinations()
