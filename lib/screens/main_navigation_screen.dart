import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/destination_provider.dart';
import '../providers/favorite_provider.dart';
import '../providers/notification_provider.dart';
import '../widgets/app_bottom_navigation.dart';
import 'explore/explore_screen.dart';
import 'home/home_screen.dart';
import 'profile/profile_screen.dart';
import 'saved/saved_screen.dart';

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<DestinationProvider>().loadInitialData();
        context.read<FavoriteProvider>().fetchFavorites();
        context.read<NotificationProvider>().fetchNotifications();
      }
    });
  }

  void _onTabSelected(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final destinationProvider = Provider.of<DestinationProvider>(context);
    final favoriteProvider = Provider.of<FavoriteProvider>(context);

    final screens = [
      HomeScreen(
        onNavigateToExplore: () => _onTabSelected(1),
      ),
      ExploreScreen(
        onToggleFavorite: (id) {
          final dest = destinationProvider.destinations.firstWhere(
            (d) => d.id == id,
            orElse: () => destinationProvider.destinations.first,
          );
          favoriteProvider.toggleFavorite(
            destination: dest,
            destinationProvider: destinationProvider,
          );
        },
      ),
      SavedScreen(
        onNavigateToHome: () => _onTabSelected(0),
        onToggleFavorite: (id) {
          final dest = destinationProvider.destinations.firstWhere(
            (d) => d.id == id,
            orElse: () => favoriteProvider.savedDestinations.firstWhere((d) => d.id == id),
          );
          favoriteProvider.toggleFavorite(
            destination: dest,
            destinationProvider: destinationProvider,
          );
        },
      ),
      const ProfileScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: AppBottomNavigation(
        currentIndex: _currentIndex,
        savedCount: favoriteProvider.savedCount,
        onTap: _onTabSelected,
      ),
    );
  }
}
