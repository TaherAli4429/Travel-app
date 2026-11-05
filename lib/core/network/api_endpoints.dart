import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';

class ApiEndpoints {
  // Production Cloud URL (overridable via --dart-define=API_URL=https://... or setProductionBaseUrl)
  static String _productionBaseUrl = 'https://wanderly-api.onrender.com/api/v1';

  static String? _customBaseUrl;

  static void setBaseUrl(String url) {
    _customBaseUrl = url.endsWith('/') ? url.substring(0, url.length - 1) : url;
  }

  static void setProductionBaseUrl(String url) {
    _productionBaseUrl = url.endsWith('/') ? url.substring(0, url.length - 1) : url;
  }

  static String get baseUrl {
    // 1. Explicit runtime override
    if (_customBaseUrl != null && _customBaseUrl!.isNotEmpty) {
      return _customBaseUrl!;
    }

    // 2. Compile-time variable: flutter build apk --dart-define=API_URL=https://...
    const envUrl = String.fromEnvironment('API_URL');
    if (envUrl.isNotEmpty) {
      return envUrl.endsWith('/') ? envUrl.substring(0, envUrl.length - 1) : envUrl;
    }

    // 3. In Release mode (Production APK), ALWAYS use production HTTPS cloud backend!
    if (kReleaseMode) {
      return _productionBaseUrl;
    }

    // 4. In Debug / Development mode on local machine
    if (kIsWeb) {
      return 'http://127.0.0.1:8001/api/v1';
    }

    try {
      if (Platform.isAndroid) {
        // Android Emulator loops back to host machine at 10.0.2.2
        return 'http://10.0.2.2:8001/api/v1';
      }
    } catch (_) {}

    return 'http://127.0.0.1:8001/api/v1';
  }

  // Auth
  static String get register => '$baseUrl/auth/register';
  static String get login => '$baseUrl/auth/login';
  static String get me => '$baseUrl/auth/me';
  static String get refresh => '$baseUrl/auth/refresh';
  static String get logout => '$baseUrl/auth/logout';
  static String get forgotPassword => '$baseUrl/auth/forgot-password';
  static String get resetPassword => '$baseUrl/auth/reset-password';

  // Users
  static String get userProfile => '$baseUrl/users/me';
  static String get changePassword => '$baseUrl/users/me/change-password';

  // Destinations
  static String get destinations => '$baseUrl/destinations';
  static String get featuredDestination => '$baseUrl/destinations/featured';
  static String get destinationCategories => '$baseUrl/destinations/categories';
  static String get destinationSearch => '$baseUrl/destinations/search';
  static String destinationDetail(String id) => '$baseUrl/destinations/$id';

  // Favorites
  static String get favorites => '$baseUrl/favorites';
  static String favoriteAction(String destinationId) => '$baseUrl/favorites/$destinationId';
  static String addFavorite(String destinationId) => '$baseUrl/favorites/$destinationId';
  static String removeFavorite(String destinationId) => '$baseUrl/favorites/$destinationId';
  static String checkFavorite(String destinationId) => '$baseUrl/favorites/check/$destinationId';

  // Reviews
  static String get reviews => '$baseUrl/reviews';
  static String destinationReviews(String destinationId) => '$baseUrl/reviews/destination/$destinationId';
  static String get myReviews => '$baseUrl/reviews/my-reviews';
  static String updateReview(String reviewId) => '$baseUrl/reviews/$reviewId';
  static String deleteReview(String reviewId) => '$baseUrl/reviews/$reviewId';

  // Notifications
  static String get notifications => '$baseUrl/notifications';
  static String get unreadNotificationsCount => '$baseUrl/notifications/unread-count';
  static String markNotificationRead(String notificationId) => '$baseUrl/notifications/$notificationId/read';
  static String markNotificationAsRead(String notificationId) => '$baseUrl/notifications/$notificationId/read';
  static String get markAllNotificationsRead => '$baseUrl/notifications/read-all';
  static String get markAllNotificationsAsRead => '$baseUrl/notifications/read-all';
  static String deleteNotification(String notificationId) => '$baseUrl/notifications/$notificationId';

  // Health Check
  static String get health => '$baseUrl/health';
}
