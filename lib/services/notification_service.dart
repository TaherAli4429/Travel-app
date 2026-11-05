import '../core/network/api_client.dart';
import '../core/network/api_endpoints.dart';
import '../models/notification_model.dart';

class NotificationService {
  final ApiClient _client = ApiClient();

  Future<List<NotificationModel>> getNotifications({int page = 1, int limit = 20}) async {
    final response = await _client.get(
      ApiEndpoints.notifications,
      queryParameters: {'page': page, 'limit': limit},
    );

    final list = response['data'] as List<dynamic>? ?? [];
    return list.map((item) => NotificationModel.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<int> getUnreadCount() async {
    try {
      final response = await _client.get(ApiEndpoints.unreadNotificationsCount);
      final data = response['data'] as Map<String, dynamic>?;
      return (data?['unread_count'] as num?)?.toInt() ?? 0;
    } catch (_) {
      return 0;
    }
  }

  Future<void> markAsRead(String id) async {
    await _client.patch(ApiEndpoints.markNotificationRead(id));
  }

  Future<void> markAllAsRead() async {
    await _client.patch(ApiEndpoints.markAllNotificationsRead);
  }
}
