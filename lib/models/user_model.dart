class UserModel {
  final String id;
  final String fullName;
  final String email;
  final String? profileImage;
  final bool isActive;
  final bool isVerified;
  final DateTime? createdAt;
  final int savedCount;
  final int reviewsCount;
  final int tripsCount;

  UserModel({
    required this.id,
    required this.fullName,
    required this.email,
    this.profileImage,
    this.isActive = true,
    this.isVerified = false,
    this.createdAt,
    this.savedCount = 0,
    this.reviewsCount = 0,
    this.tripsCount = 0,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String? ?? '',
      fullName: (json['full_name'] ?? json['fullName'] ?? '') as String,
      email: json['email'] as String? ?? '',
      profileImage: (json['profile_image'] ?? json['profileImage']) as String?,
      isActive: (json['is_active'] ?? json['isActive'] ?? true) as bool,
      isVerified: (json['is_verified'] ?? json['isVerified'] ?? false) as bool,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
      savedCount: (json['saved_count'] ?? json['savedCount'] as num?)?.toInt() ?? 0,
      reviewsCount: (json['reviews_count'] ?? json['reviewsCount'] as num?)?.toInt() ?? 0,
      tripsCount: (json['trips_count'] ?? json['tripsCount'] as num?)?.toInt() ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'full_name': fullName,
      'email': email,
      'profile_image': profileImage,
      'is_active': isActive,
      'is_verified': isVerified,
      'created_at': createdAt?.toIso8601String(),
      'saved_count': savedCount,
      'reviews_count': reviewsCount,
      'trips_count': tripsCount,
    };
  }

  UserModel copyWith({
    String? id,
    String? fullName,
    String? email,
    String? profileImage,
    bool? isActive,
    bool? isVerified,
    DateTime? createdAt,
    int? savedCount,
    int? reviewsCount,
    int? tripsCount,
  }) {
    return UserModel(
      id: id ?? this.id,
      fullName: fullName ?? this.fullName,
      email: email ?? this.email,
      profileImage: profileImage ?? this.profileImage,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      createdAt: createdAt ?? this.createdAt,
      savedCount: savedCount ?? this.savedCount,
      reviewsCount: reviewsCount ?? this.reviewsCount,
      tripsCount: tripsCount ?? this.tripsCount,
    );
  }
}
