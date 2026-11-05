import '../core/network/api_client.dart';
import '../core/network/api_endpoints.dart';
import '../models/destination.dart';

class DestinationService {
  final ApiClient _client = ApiClient();

  Future<List<Destination>> getDestinations({
    String? category,
    double? minRating,
    String? search,
    bool? isFeatured,
    int page = 1,
    int limit = 50,
  }) async {
    final Map<String, dynamic> params = {
      'page': page,
      'limit': limit,
    };
    if (category != null && category.isNotEmpty && category != 'All') {
      params['category'] = category;
    }
    if (minRating != null && minRating > 0.0) {
      params['min_rating'] = minRating;
    }
    if (search != null && search.trim().isNotEmpty) {
      params['search'] = search.trim();
    }
    if (isFeatured != null) {
      params['is_featured'] = isFeatured;
    }

    final response = await _client.get(
      ApiEndpoints.destinations,
      queryParameters: params,
    );

    final list = response['data'] as List<dynamic>? ?? [];
    return list.map((item) => Destination.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<Destination?> getFeaturedDestination() async {
    try {
      final response = await _client.get(ApiEndpoints.featuredDestination);
      final data = response['data'] as Map<String, dynamic>?;
      if (data == null) return null;
      return Destination.fromJson(data);
    } catch (_) {
      return null;
    }
  }

  Future<List<String>> getCategories() async {
    try {
      final response = await _client.get(ApiEndpoints.destinationCategories);
      final list = response['data'] as List<dynamic>? ?? [];
      return list.map((c) => c.toString()).toList();
    } catch (_) {
      return ['All', 'Beaches', 'Mountains', 'Cities', 'Adventure', 'Resorts', 'Camping'];
    }
  }

  Future<Destination> getDestinationById(String id) async {
    final response = await _client.get(ApiEndpoints.destinationDetail(id));
    final data = response['data'] as Map<String, dynamic>;
    return Destination.fromJson(data);
  }
}
