class NotificationModel {
  final String id;
  final String userId;
  final String title;
  final String message;
  bool isRead;
  final DateTime? createdAt;

  NotificationModel({
    required this.id,
    required this.userId,
    required this.title,
    required this.message,
    this.isRead = false,
    this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] as String? ?? '',
      userId: (json['user_id'] ?? json['userId'] ?? '') as String,
      title: json['title'] as String? ?? '',
      message: json['message'] as String? ?? '',
      isRead: (json['is_read'] ?? json['isRead'] ?? false) as bool,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'title': title,
      'message': message,
      'is_read': isRead,
      'created_at': createdAt?.toIso8601String(),
    };
  }
}
