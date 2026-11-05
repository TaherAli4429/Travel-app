import 'package:flutter/material.dart';

class AppConstants {
  static const String appName = 'Wanderly';
  static const String appTagline = 'Discover the world, your way.';

  // Default Categories
  static const List<Map<String, dynamic>> categories = [
    {'name': 'All', 'icon': Icons.explore_rounded},
    {'name': 'Beaches', 'icon': Icons.beach_access_rounded},
    {'name': 'Mountains', 'icon': Icons.terrain_rounded},
    {'name': 'Cities', 'icon': Icons.location_city_rounded},
    {'name': 'Adventure', 'icon': Icons.paragliding_rounded},
    {'name': 'Resorts', 'icon': Icons.pool_rounded},
    {'name': 'Camping', 'icon': Icons.forest_rounded},
  ];
}
