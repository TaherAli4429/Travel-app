import '../models/destination.dart';

class MockDestinations {
  static List<Destination> getDestinations() {
    return [
      Destination(
        id: 'dest_1',
        name: 'Bali',
        country: 'Indonesia',
        category: 'Beaches',
        imageUrl:
            'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1000&q=80',
        rating: 4.9,
        reviewsCount: 384,
        price: '\$450 / person',
        description:
            'Tropical paradise known for its forested volcanic mountains, iconic rice paddies, beaches, coral reefs, and vibrant cultural heritage.',
        isFeatured: true,
        isSaved: true,
      ),
      Destination(
        id: 'dest_2',
        name: 'Swiss Alps',
        country: 'Switzerland',
        category: 'Mountains',
        imageUrl:
            'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=1000&q=80',
        rating: 4.88,
        reviewsCount: 290,
        price: '\$820 / person',
        description:
            'Dramatic alpine peaks, crystalline glacial lakes, and world-class skiing, hiking, and picturesque mountain chalets.',
        isFeatured: false,
        isSaved: false,
      ),
      Destination(
        id: 'dest_3',
        name: 'Santorini',
        country: 'Greece',
        category: 'Beaches',
        imageUrl:
            'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1000&q=80',
        rating: 4.95,
        reviewsCount: 512,
        price: '\$680 / person',
        description:
            'Whitewashed cubiform cliffside villages overlooking the azure Aegean caldera, famous for world-renowned sunsets and volcanic beaches.',
        isFeatured: false,
        isSaved: true,
      ),
      Destination(
        id: 'dest_4',
        name: 'Kyoto',
        country: 'Japan',
        category: 'Cities',
        imageUrl:
            'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1000&q=80',
        rating: 4.92,
        reviewsCount: 430,
        price: '\$550 / person',
        description:
            'Historic heart of Japan, featuring ancient Buddhist temples, serene bamboo groves, traditional wooden machiya houses, and cherry blossoms.',
        isFeatured: false,
        isSaved: false,
      ),
      Destination(
        id: 'dest_5',
        name: 'Maldives',
        country: 'Maldives',
        category: 'Resorts',
        imageUrl:
            'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&w=1000&q=80',
        rating: 4.97,
        reviewsCount: 610,
        price: '\$950 / person',
        description:
            'Luxury overwater bungalows, turquoise shallow lagoons, and vibrant manta ray and turtle coral reefs in the Indian Ocean.',
        isFeatured: false,
        isSaved: true,
      ),
      Destination(
        id: 'dest_6',
        name: 'Dubai',
        country: 'United Arab Emirates',
        category: 'Cities',
        imageUrl:
            'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1000&q=80',
        rating: 4.85,
        reviewsCount: 345,
        price: '\$620 / person',
        description:
            'Futuristic desert metropolis boasting Burj Khalifa, expansive luxury shopping, desert safaris, and ultramodern waterfront attractions.',
        isFeatured: false,
        isSaved: false,
      ),
      Destination(
        id: 'dest_7',
        name: 'Banff National Park',
        country: 'Canada',
        category: 'Camping',
        imageUrl:
            'https://images.unsplash.com/photo-1503614472-8c93d56e92ce?auto=format&fit=crop&w=1000&q=80',
        rating: 4.91,
        reviewsCount: 275,
        price: '\$490 / person',
        description:
            'Majestic Canadian Rockies, pristine turquoise Lake Louise, thermal hot springs, and awe-inspiring hiking trails.',
        isFeatured: false,
        isSaved: false,
      ),
      Destination(
        id: 'dest_8',
        name: 'Queenstown',
        country: 'New Zealand',
        category: 'Adventure',
        imageUrl:
            'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?auto=format&fit=crop&w=1000&q=80',
        rating: 4.89,
        reviewsCount: 198,
        price: '\$710 / person',
        description:
            'World adventure hub on the shores of Lake Wakatipu, set against the dramatic Southern Alps, famous for bungee jumping and skydiving.',
        isFeatured: false,
        isSaved: false,
      ),
      Destination(
        id: 'dest_9',
        name: 'Amalfi Coast',
        country: 'Italy',
        category: 'Resorts',
        imageUrl:
            'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=1000&q=80',
        rating: 4.93,
        reviewsCount: 420,
        price: '\$780 / person',
        description:
            'Picturesque Italian coastline featuring colorful pastel cliffside towns, Mediterranean lemon groves, and scenic coastal road drives.',
        isFeatured: false,
        isSaved: false,
      ),
    ];
  }
}
