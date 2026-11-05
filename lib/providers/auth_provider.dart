import 'dart:convert';
import 'package:flutter/material.dart';
import '../core/network/api_exceptions.dart';
import '../core/storage/token_storage.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  final TokenStorage _tokenStorage = TokenStorage();

  UserModel? _currentUser;
  bool _isLoading = false;
  String? _errorMessage;

  UserModel? get currentUser => _currentUser;
  bool get isAuthenticated => _currentUser != null;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<bool> checkAuthStatus() async {
    final hasToken = await _tokenStorage.hasToken();
    if (!hasToken) {
      _currentUser = null;
      notifyListeners();
      return false;
    }

    // Try loading cached user data first for instant UI response
    final cachedData = await _tokenStorage.getUserData();
    if (cachedData != null) {
      try {
        _currentUser = UserModel.fromJson(jsonDecode(cachedData));
        notifyListeners();
      } catch (_) {}
    }

    // Validate with backend
    try {
      final user = await _authService.getCurrentUser();
      _currentUser = user;
      notifyListeners();
      return true;
    } catch (e) {
      // If token is invalid/expired on server, clear
      if (e is ApiException && (e.statusCode == 401 || e.statusCode == 403)) {
        await _tokenStorage.clearTokens();
        _currentUser = null;
        notifyListeners();
        return false;
      }
      // If network error occurred, keep cached session if available
      return _currentUser != null;
    }
  }

  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final user = await _authService.login(
        email: email,
        password: password,
      );
      _currentUser = user;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      if (e is ApiException) {
        _errorMessage = e.message;
      } else {
        _errorMessage = 'An unexpected error occurred during login.';
      }
      notifyListeners();
      return false;
    }
  }

  Future<bool> register({
    required String fullName,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _authService.register(
        fullName: fullName,
        email: email,
        password: password,
        confirmPassword: confirmPassword,
      );
      // Automatically login after successful registration
      final loggedIn = await login(email: email, password: password);
      return loggedIn;
    } catch (e) {
      _isLoading = false;
      if (e is ApiException) {
        _errorMessage = e.message;
      } else {
        _errorMessage = 'Registration failed. Please try again.';
      }
      notifyListeners();
      return false;
    }
  }

  Future<void> refreshProfile() async {
    if (!isAuthenticated) return;
    try {
      final profile = await _authService.getUserProfile();
      _currentUser = profile;
      notifyListeners();
    } catch (_) {}
  }

  Future<bool> updateProfile({String? fullName, String? email, String? profileImage}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final updated = await _authService.updateProfile(
        fullName: fullName,
        email: email,
        profileImage: profileImage,
      );
      _currentUser = updated;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      if (e is ApiException) {
        _errorMessage = e.message;
      } else {
        _errorMessage = 'Failed to update profile.';
      }
      notifyListeners();
      return false;
    }
  }

  Future<String?> forgotPassword(String email) async {
    try {
      return await _authService.forgotPassword(email);
    } catch (e) {
      if (e is ApiException) {
        _errorMessage = e.message;
      }
      return null;
    }
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    await _authService.logout();
    _currentUser = null;
    _isLoading = false;
    notifyListeners();
  }
}
