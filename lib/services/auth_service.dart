import 'dart:convert';
import '../core/network/api_client.dart';
import '../core/network/api_endpoints.dart';
import '../core/storage/token_storage.dart';
import '../models/user_model.dart';

class AuthService {
  final ApiClient _client = ApiClient();
  final TokenStorage _tokenStorage = TokenStorage();

  Future<UserModel> register({
    required String fullName,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    final response = await _client.post(
      ApiEndpoints.register,
      data: {
        'full_name': fullName,
        'email': email,
        'password': password,
        'confirm_password': confirmPassword,
      },
    );

    final userData = response['data'] as Map<String, dynamic>;
    return UserModel.fromJson(userData);
  }

  Future<UserModel> login({
    required String email,
    required String password,
  }) async {
    final response = await _client.post(
      ApiEndpoints.login,
      data: {
        'email': email,
        'password': password,
      },
    );

    final data = response['data'] as Map<String, dynamic>;
    final accessToken = data['access_token'] as String;
    final refreshToken = data['refresh_token'] as String;
    final userData = data['user'] as Map<String, dynamic>;

    await _tokenStorage.saveTokens(
      accessToken: accessToken,
      refreshToken: refreshToken,
    );
    await _tokenStorage.saveUserData(jsonEncode(userData));

    return UserModel.fromJson(userData);
  }

  Future<UserModel> getCurrentUser() async {
    final response = await _client.get(ApiEndpoints.me);
    final userData = response['data'] as Map<String, dynamic>;
    await _tokenStorage.saveUserData(jsonEncode(userData));
    return UserModel.fromJson(userData);
  }

  Future<UserModel> getUserProfile() async {
    final response = await _client.get(ApiEndpoints.userProfile);
    final userData = response['data'] as Map<String, dynamic>;
    await _tokenStorage.saveUserData(jsonEncode(userData));
    return UserModel.fromJson(userData);
  }

  Future<UserModel> updateProfile({
    String? fullName,
    String? email,
    String? profileImage,
  }) async {
    final Map<String, dynamic> data = {};
    if (fullName != null) data['full_name'] = fullName;
    if (email != null) data['email'] = email;
    if (profileImage != null) data['profile_image'] = profileImage;

    final response = await _client.put(
      ApiEndpoints.userProfile,
      data: data,
    );
    final userData = response['data'] as Map<String, dynamic>;
    await _tokenStorage.saveUserData(jsonEncode(userData));
    return UserModel.fromJson(userData);
  }

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    await _client.post(
      ApiEndpoints.changePassword,
      data: {
        'current_password': currentPassword,
        'new_password': newPassword,
        'confirm_password': confirmPassword,
      },
    );
  }

  Future<String?> forgotPassword(String email) async {
    final response = await _client.post(
      ApiEndpoints.forgotPassword,
      data: {'email': email},
    );
    final data = response['data'] as Map<String, dynamic>?;
    return data?['dev_reset_token'] as String?;
  }

  Future<void> resetPassword({
    required String token,
    required String newPassword,
    required String confirmPassword,
  }) async {
    await _client.post(
      ApiEndpoints.resetPassword,
      data: {
        'token': token,
        'new_password': newPassword,
        'confirm_password': confirmPassword,
      },
    );
  }

  Future<void> logout() async {
    try {
      await _client.post(ApiEndpoints.logout);
    } catch (_) {}
    await _tokenStorage.clearTokens();
  }
}
