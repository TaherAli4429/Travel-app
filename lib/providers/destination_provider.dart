import 'package:flutter/material.dart';
import '../data/mock_destinations.dart';
import '../models/destination.dart';
import '../services/destination_service.dart';

class DestinationProvider extends ChangeNotifier {
  final DestinationService _destinationService = DestinationService();

  List<Destination> _destinations = [];
  Destination? _featuredDestination;
  List<String> _categories = ['All', 'Beaches', 'Mountains', 'Cities', 'Adventure', 'Resorts', 'Camping'];
  String _selectedCategory = 'All';
  double _minRating = 0.0;
  String _searchQuery = '';
  bool _isLoading = false;
  String? _errorMessage;

  List<Destination> get destinations => _destinations;
  Destination? get featuredDestination => _featuredDestination;
  List<String> get categories => _categories;
  String get selectedCategory => _selectedCategory;
  double get minRating => _minRating;
  String get searchQuery => _searchQuery;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<Destination> get filteredDestinations {
    final query = _searchQuery.trim().toLowerCase();

    return _destinations.where((dest) {
      final matchesCategory = _selectedCategory == 'All' ||
          dest.category.toLowerCase() == _selectedCategory.toLowerCase();

      final matchesSearch = query.isEmpty ||
          dest.name.toLowerCase().contains(query) ||
          dest.country.toLowerCase().contains(query) ||
          dest.category.toLowerCase().contains(query);

      final matchesRating = dest.rating >= _minRating;

      return matchesCategory && matchesSearch && matchesRating;
    }).toList();
  }

  Future<void> loadInitialData() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final fetched = await _destinationService.getDestinations(limit: 50);
      if (fetched.isNotEmpty) {
        _destinations = fetched;
      } else {
        _destinations = MockDestinations.getDestinations();
      }

      final featured = await _destinationService.getFeaturedDestination();
      if (featured != null) {
        _featuredDestination = featured;
      } else if (_destinations.isNotEmpty) {
        _featuredDestination = _destinations.firstWhere(
          (d) => d.isFeatured,
          orElse: () => _destinations.first,
        );
      }

      final cats = await _destinationService.getCategories();
      if (cats.isNotEmpty) {
        _categories = cats;
      }

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      // Graceful fallback to initial mock list on connection failure
      _destinations = MockDestinations.getDestinations();
      _featuredDestination = _destinations.firstWhere(
        (d) => d.isFeatured,
        orElse: () => _destinations.first,
      );
      _isLoading = false;
      _errorMessage = 'Could not reach backend. Showing offline cached destinations.';
      notifyListeners();
    }
  }

  void setCategory(String category) {
    _selectedCategory = category;
    notifyListeners();
  }

  void setRating(double rating) {
    _minRating = rating;
    notifyListeners();
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  void resetFilters() {
    _selectedCategory = 'All';
    _minRating = 0.0;
    _searchQuery = '';
    notifyListeners();
  }

  void updateDestinationSavedState(String destinationId, bool isSaved) {
    final index = _destinations.indexWhere((d) => d.id == destinationId);
    if (index != -1) {
      _destinations[index].isSaved = isSaved;
    }
    if (_featuredDestination != null && _featuredDestination!.id == destinationId) {
      _featuredDestination!.isSaved = isSaved;
    }
    notifyListeners();
  }
}
