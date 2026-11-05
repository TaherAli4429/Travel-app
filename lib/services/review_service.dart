import '../core/network/api_client.dart';
import '../models/review_model.dart';

class ReviewService {
  final ApiClient _apiClient = ApiClient();

  Future<List<ReviewModel>> getDestinationReviews(String destinationId) async {
    try {
      final response = await _apiClient.get('/reviews/destination/$destinationId');
      final data = response.data['data'] as List<dynamic>? ?? [];
      return data.map((json) => ReviewModel.fromJson(json as Map<String, dynamic>)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<ReviewModel?> submitReview({
    required String destinationId,
    required double rating,
    required String comment,
  }) async {
    final response = await _apiClient.post(
      '/reviews',
      data: {
        'destination_id': destinationId,
        'rating': rating,
        'comment': comment,
      },
    );
    if (response.data['data'] != null) {
      return ReviewModel.fromJson(response.data['data'] as Map<String, dynamic>);
    }
    return null;
  }
}
