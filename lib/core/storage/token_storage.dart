import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenStorage {
  static final TokenStorage _instance = TokenStorage._internal();
  factory TokenStorage() => _instance;
  TokenStorage._internal();

  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    wOptions: WindowsOptions(useBackwardCompatibility: true),
  );

  // In-memory fallback for environments with secure storage restrictions
  final Map<String, String> _memoryCache = {};

  static const String _accessTokenKey = 'wanderly_access_token';
  static const String _refreshTokenKey = 'wanderly_refresh_token';
  static const String _userDataKey = 'wanderly_user_data';

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    _memoryCache[_accessTokenKey] = accessToken;
    _memoryCache[_refreshTokenKey] = refreshToken;

    try {
      await _secureStorage.write(key: _accessTokenKey, value: accessToken);
      await _secureStorage.write(key: _refreshTokenKey, value: refreshToken);
    } catch (e) {
      debugPrint('TokenStorage write warning: $e');
    }
  }

  Future<String?> getAccessToken() async {
    if (_memoryCache.containsKey(_accessTokenKey)) {
      return _memoryCache[_accessTokenKey];
    }
    try {
      final token = await _secureStorage.read(key: _accessTokenKey);
      if (token != null) {
        _memoryCache[_accessTokenKey] = token;
      }
      return token;
    } catch (e) {
      debugPrint('TokenStorage read warning: $e');
      return null;
    }
  }

  Future<String?> getRefreshToken() async {
    if (_memoryCache.containsKey(_refreshTokenKey)) {
      return _memoryCache[_refreshTokenKey];
    }
    try {
      final token = await _secureStorage.read(key: _refreshTokenKey);
      if (token != null) {
        _memoryCache[_refreshTokenKey] = token;
      }
      return token;
    } catch (e) {
      return null;
    }
  }

  Future<bool> hasToken() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  Future<void> saveUserData(String jsonString) async {
    _memoryCache[_userDataKey] = jsonString;
    try {
      await _secureStorage.write(key: _userDataKey, value: jsonString);
    } catch (_) {}
  }

  Future<String?> getUserData() async {
    if (_memoryCache.containsKey(_userDataKey)) {
      return _memoryCache[_userDataKey];
    }
    try {
      return await _secureStorage.read(key: _userDataKey);
    } catch (_) {
      return null;
    }
  }

  Future<void> clearTokens() async {
    _memoryCache.clear();
    try {
      await _secureStorage.deleteAll();
    } catch (e) {
      debugPrint('TokenStorage clear warning: $e');
    }
  }
}
