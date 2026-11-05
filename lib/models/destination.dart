class Destination {
  final String id;
  final String name;
  final String country;
  final String category;
  final String imageUrl;
  final double rating;
  final int reviewsCount;
  final String price;
  final String description;
  final bool isFeatured;
  bool isSaved;

  Destination({
    required this.id,
    required this.name,
    required this.country,
    required this.category,
    required this.imageUrl,
    required this.rating,
    this.reviewsCount = 142,
    required this.price,
    required this.description,
    this.isFeatured = false,
    this.isSaved = false,
  });

  factory Destination.fromJson(Map<String, dynamic> json) {
    return Destination(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      country: json['country'] as String? ?? '',
      category: json['category'] as String? ?? '',
      imageUrl: (json['image_url'] ?? json['imageUrl'] ?? '') as String,
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
      reviewsCount: (json['reviews_count'] ?? json['reviewsCount'] as num?)?.toInt() ?? 0,
      price: json['price'] as String? ?? '',
      description: json['description'] as String? ?? '',
      isFeatured: (json['is_featured'] ?? json['isFeatured'] ?? false) as bool,
      isSaved: (json['is_saved'] ?? json['isSaved'] ?? false) as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'country': country,
      'category': category,
      'image_url': imageUrl,
      'rating': rating,
      'reviews_count': reviewsCount,
      'price': price,
      'description': description,
      'is_featured': isFeatured,
      'is_saved': isSaved,
    };
  }

  Destination copyWith({
    String? id,
    String? name,
    String? country,
    String? category,
    String? imageUrl,
    double? rating,
    int? reviewsCount,
    String? price,
    String? description,
    bool? isFeatured,
    bool? isSaved,
  }) {
    return Destination(
      id: id ?? this.id,
      name: name ?? this.name,
      country: country ?? this.country,
      category: category ?? this.category,
      imageUrl: imageUrl ?? this.imageUrl,
      rating: rating ?? this.rating,
      reviewsCount: reviewsCount ?? this.reviewsCount,
      price: price ?? this.price,
      description: description ?? this.description,
      isFeatured: isFeatured ?? this.isFeatured,
      isSaved: isSaved ?? this.isSaved,
    );
  }
}
