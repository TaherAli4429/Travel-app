import '../core/network/api_client.dart';
import '../core/network/api_endpoints.dart';
import '../models/destination.dart';

class FavoriteService {
  final ApiClient _client = ApiClient();

  Future<void> addFavorite(String destinationId) async {
    await _client.post(ApiEndpoints.favoriteAction(destinationId));
  }

  Future<void> removeFavorite(String destinationId) async {
    await _client.delete(ApiEndpoints.favoriteAction(destinationId));
  }

  Future<List<Destination>> getFavorites({int page = 1, int limit = 50}) async {
    final response = await _client.get(
      ApiEndpoints.favorites,
      queryParameters: {'page': page, 'limit': limit},
    );

    final list = response['data'] as List<dynamic>? ?? [];
    return list.map((item) => Destination.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<bool> checkFavorite(String destinationId) async {
    try {
      final response = await _client.get(ApiEndpoints.checkFavorite(destinationId));
      final data = response['data'] as Map<String, dynamic>?;
      return (data?['is_saved'] as bool?) ?? false;
    } catch (_) {
      return false;
    }
  }
}
