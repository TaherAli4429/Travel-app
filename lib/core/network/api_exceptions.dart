import 'package:dio/dio.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final List<String> errors;

  ApiException({
    required this.message,
    this.statusCode,
    this.errors = const [],
  });

  factory ApiException.fromDioException(DioException error) {
    int? code = error.response?.statusCode;
    String fallbackMessage = 'Network connection failed. Please check your internet or backend connection.';
    List<String> errorList = [];

    if (error.response?.data != null && error.response!.data is Map<String, dynamic>) {
      final data = error.response!.data as Map<String, dynamic>;
      if (data['message'] != null) {
        fallbackMessage = data['message'].toString();
      }
      if (data['errors'] is List) {
        errorList = (data['errors'] as List).map((e) => e.toString()).toList();
      }
    } else if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      fallbackMessage = 'Request timed out. Please verify the backend server is running.';
    } else if (error.type == DioExceptionType.connectionError) {
      fallbackMessage = 'Could not connect to backend server at ${error.requestOptions.uri}. Ensure the FastAPI server is running.';
    }

    return ApiException(
      message: fallbackMessage,
      statusCode: code,
      errors: errorList,
    );
  }

  @override
  String toString() => message;
}
