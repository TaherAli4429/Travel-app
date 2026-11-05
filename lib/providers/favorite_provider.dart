import 'package:flutter/material.dart';
import '../models/destination.dart';
import '../services/favorite_service.dart';
import 'destination_provider.dart';

class FavoriteProvider extends ChangeNotifier {
  final FavoriteService _favoriteService = FavoriteService();

  List<Destination> _savedDestinations = [];
  Set<String> _savedIds = {};
  bool _isLoading = false;

  List<Destination> get savedDestinations => _savedDestinations;
  Set<String> get savedIds => _savedIds;
  int get savedCount => _savedIds.length;
  bool get isLoading => _isLoading;

  bool isSaved(String destinationId) {
    return _savedIds.contains(destinationId);
  }

  Future<void> fetchFavorites() async {
    _isLoading = true;
    notifyListeners();

    try {
      final list = await _favoriteService.getFavorites();
      _savedDestinations = list;
      _savedIds = list.map((d) => d.id).toSet();
    } catch (_) {
      // Keep current state on network failure
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> toggleFavorite({
    required Destination destination,
    required DestinationProvider destinationProvider,
  }) async {
    final destinationId = destination.id;
    final currentlySaved = isSaved(destinationId);
    final targetState = !currentlySaved;

    // Optimistic UI update
    if (targetState) {
      _savedIds.add(destinationId);
      final exists = _savedDestinations.any((d) => d.id == destinationId);
      if (!exists) {
        _savedDestinations.insert(0, destination.copyWith(isSaved: true));
      }
    } else {
      _savedIds.remove(destinationId);
      _savedDestinations.removeWhere((d) => d.id == destinationId);
    }
    destinationProvider.updateDestinationSavedState(destinationId, targetState);
    notifyListeners();

    // Call real backend API
    try {
      if (targetState) {
        await _favoriteService.addFavorite(destinationId);
      } else {
        await _favoriteService.removeFavorite(destinationId);
      }
    } catch (e) {
      // Rollback on error
      if (currentlySaved) {
        _savedIds.add(destinationId);
        _savedDestinations.add(destination.copyWith(isSaved: true));
      } else {
        _savedIds.remove(destinationId);
        _savedDestinations.removeWhere((d) => d.id == destinationId);
      }
      destinationProvider.updateDestinationSavedState(destinationId, currentlySaved);
      notifyListeners();
    }
  }

  void clear() {
    _savedDestinations.clear();
    _savedIds.clear();
    notifyListeners();
  }
}
