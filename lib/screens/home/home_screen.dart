import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_constants.dart';
import '../../core/theme/app_colors.dart';
import '../../models/destination.dart';
import '../../providers/auth_provider.dart';
import '../../providers/destination_provider.dart';
import '../../providers/favorite_provider.dart';
import '../../providers/notification_provider.dart';
import '../../widgets/category_chip.dart';
import '../../widgets/destination_card.dart';
import '../../widgets/destination_detail_sheet.dart';
import '../../widgets/featured_destination_card.dart';

class HomeScreen extends StatefulWidget {
  final List<Destination>? destinations;
  final Function(String id)? onToggleFavorite;
  final VoidCallback onNavigateToExplore;

  const HomeScreen({
    super.key,
    this.destinations,
    this.onToggleFavorite,
    required this.onNavigateToExplore,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _showNotificationsSheet(BuildContext context) {
    final notificationProvider = Provider.of<NotificationProvider>(context, listen: false);
    notificationProvider.fetchNotifications();

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      builder: (context) {
        return Consumer<NotificationProvider>(
          builder: (context, notifProvider, _) {
            final items = notifProvider.notifications;
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Notifications',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w800,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      if (items.isNotEmpty && notifProvider.unreadCount > 0)
                        TextButton(
                          onPressed: () => notifProvider.markAllAsRead(),
                          child: const Text('Mark all as read'),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  if (items.isEmpty)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 32),
                      child: Center(
                        child: Column(
                          children: [
                            Icon(Icons.notifications_off_outlined, size: 48, color: AppColors.textMuted),
                            SizedBox(height: 10),
                            Text(
                              "No notifications yet. You're all caught up! ✈️",
                              style: TextStyle(color: AppColors.textSecondary, fontSize: 14),
                            ),
                          ],
                        ),
                      ),
                    )
                  else
                    ConstrainedBox(
                      constraints: BoxConstraints(
                        maxHeight: MediaQuery.of(context).size.height * 0.45,
                      ),
                      child: ListView.separated(
                        shrinkWrap: true,
                        itemCount: items.length,
                        separatorBuilder: (context, index) => const Divider(height: 1, color: Color(0xFFF1F5F9)),
                        itemBuilder: (context, index) {
                          final n = items[index];
                          return ListTile(
                            leading: Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: n.isRead ? const Color(0xFFF1F5F9) : AppColors.lightTeal,
                                shape: BoxShape.circle,
                              ),
                              child: Icon(
                                Icons.notifications_active_rounded,
                                size: 18,
                                color: n.isRead ? AppColors.textMuted : AppColors.primary,
                              ),
                            ),
                            title: Text(
                              n.title,
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: n.isRead ? FontWeight.w500 : FontWeight.w700,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            subtitle: Text(
                              n.message,
                              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                            ),
                            onTap: () {
                              if (!n.isRead) {
                                notifProvider.markAsRead(n.id);
                              }
                            },
                          );
                        },
                      ),
                    ),
                  const SizedBox(height: 8),
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _openFilterSheet(DestinationProvider destProvider) {
    double tempRating = destProvider.minRating;

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Filter Destinations',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close_rounded),
                        onPressed: () => Navigator.of(context).pop(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Rating Filter
                  const Text(
                    'Minimum Rating',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [0.0, 4.5, 4.8, 4.9].map((rating) {
                      final isSelected = tempRating == rating;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(rating == 0.0 ? 'All' : '⭐ $rating+'),
                          selected: isSelected,
                          selectedColor: AppColors.primary,
                          labelStyle: TextStyle(
                            color: isSelected ? Colors.white : AppColors.textPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                          onSelected: (selected) {
                            setSheetState(() {
                              tempRating = rating;
                            });
                          },
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),

                  // Actions
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            destProvider.resetFilters();
                            _searchController.clear();
                            Navigator.of(context).pop();
                          },
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: AppColors.inputBorder),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
                          ),
                          child: const Text(
                            'Reset',
                            style: TextStyle(color: AppColors.textSecondary),
                          ),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            destProvider.setRating(tempRating);
                            Navigator.of(context).pop();
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
                          ),
                          child: const Text(
                            'Apply Filter',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final destinationProvider = Provider.of<DestinationProvider>(context);
    final favoriteProvider = Provider.of<FavoriteProvider>(context);
    final notificationProvider = Provider.of<NotificationProvider>(context);

    final featured = destinationProvider.featuredDestination;
    final filteredList = destinationProvider.filteredDestinations;
    final userFirstName = authProvider.currentUser?.fullName.split(' ').first ?? 'Traveler';

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: CustomScrollView(
          physics: const BouncingScrollPhysics(),
          slivers: [
            // Top App Header with Real User Name and Unread Notification Count
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Profile greeting
                    Row(
                      children: [
                        Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: AppColors.secondary,
                              width: 2,
                            ),
                            image: DecorationImage(
                              image: NetworkImage(
                                authProvider.currentUser?.profileImage ??
                                    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80',
                              ),
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Hello, $userFirstName 👋',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            const SizedBox(height: 2),
                            const Text(
                              'Where do you want to explore?',
                              style: TextStyle(
                                fontSize: 13,
                                color: AppColors.textSecondary,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),

                    // Notification button with real unread badge
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(14),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.04),
                            blurRadius: 10,
                            offset: const Offset(0, 3),
                          ),
                        ],
                      ),
                      child: IconButton(
                        icon: Stack(
                          clipBehavior: Clip.none,
                          children: [
                            const Icon(
                              Icons.notifications_none_rounded,
                              color: AppColors.textPrimary,
                              size: 24,
                            ),
                            if (notificationProvider.unreadCount > 0)
                              Positioned(
                                top: -2,
                                right: -1,
                                child: Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: const BoxDecoration(
                                    color: AppColors.heart,
                                    shape: BoxShape.circle,
                                  ),
                                  constraints: const BoxConstraints(minWidth: 8, minHeight: 8),
                                ),
                              ),
                          ],
                        ),
                        onPressed: () => _showNotificationsSheet(context),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Search Bar & Filter Button
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                child: Row(
                  children: [
                    Expanded(
                      child: Container(
                        height: 52,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.04),
                              blurRadius: 12,
                              offset: const Offset(0, 3),
                            ),
                          ],
                        ),
                        child: TextField(
                          controller: _searchController,
                          onChanged: (val) {
                            destinationProvider.setSearchQuery(val);
                          },
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: AppColors.textPrimary,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Search destinations, hotels...',
                            hintStyle: const TextStyle(
                              color: AppColors.textMuted,
                              fontSize: 14,
                            ),
                            prefixIcon: const Icon(
                              Icons.search_rounded,
                              color: AppColors.textSecondary,
                              size: 22,
                            ),
                            suffixIcon: _searchController.text.isNotEmpty
                                ? IconButton(
                                    icon: const Icon(Icons.clear_rounded, size: 18),
                                    onPressed: () {
                                      _searchController.clear();
                                      destinationProvider.setSearchQuery('');
                                    },
                                  )
                                : null,
                            border: InputBorder.none,
                            enabledBorder: InputBorder.none,
                            focusedBorder: InputBorder.none,
                            contentPadding: const EdgeInsets.symmetric(
                              vertical: 16,
                              horizontal: 16,
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    GestureDetector(
                      onTap: () => _openFilterSheet(destinationProvider),
                      child: Container(
                        height: 52,
                        width: 52,
                        decoration: BoxDecoration(
                          color: destinationProvider.minRating > 0.0
                              ? AppColors.primary
                              : AppColors.primaryDark,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.primary.withValues(alpha: 0.25),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.tune_rounded,
                          color: Colors.white,
                          size: 22,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Category Chips Row
            SliverToBoxAdapter(
              child: Container(
                height: 52,
                margin: const EdgeInsets.only(top: 14, bottom: 8),
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  physics: const BouncingScrollPhysics(),
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  itemCount: AppConstants.categories.length,
                  separatorBuilder: (context, index) => const SizedBox(width: 10),
                  itemBuilder: (context, index) {
                    final item = AppConstants.categories[index];
                    final name = item['name'] as String;
                    final icon = item['icon'] as IconData;
                    final isSelected = destinationProvider.selectedCategory == name;

                    return CategoryChip(
                      label: name,
                      icon: icon,
                      isSelected: isSelected,
                      onTap: () {
                        destinationProvider.setCategory(name);
                      },
                    );
                  },
                ),
              ),
            ),

            // Featured Destination Section
            if (featured != null &&
                destinationProvider.searchQuery.isEmpty &&
                destinationProvider.selectedCategory == 'All') ...[
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 16, 20, 10),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Featured Destination',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.lightTeal,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'Top Pick',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: FeaturedDestinationCard(
                    destination: featured.copyWith(
                      isSaved: favoriteProvider.isSaved(featured.id),
                    ),
                    onFavoriteToggle: () {
                      favoriteProvider.toggleFavorite(
                        destination: featured,
                        destinationProvider: destinationProvider,
                      );
                    },
                    onTap: () {
                      DestinationDetailSheet.show(
                        context,
                        destination: featured.copyWith(
                          isSaved: favoriteProvider.isSaved(featured.id),
                        ),
                        onFavoriteToggle: () {
                          favoriteProvider.toggleFavorite(
                            destination: featured,
                            destinationProvider: destinationProvider,
                          );
                        },
                      );
                    },
                  ),
                ),
              ),
            ],

            // Popular Destinations Heading
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 14),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        const Text(
                          'Popular Destinations',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w800,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFFE2E8F0),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            '${filteredList.length}',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ),
                      ],
                    ),
                    GestureDetector(
                      onTap: widget.onNavigateToExplore,
                      child: const Text(
                        'See All',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Horizontal Carousel or Empty State
            if (filteredList.isEmpty)
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 36),
                  child: Column(
                    children: [
                      Icon(
                        Icons.search_off_rounded,
                        size: 56,
                        color: AppColors.textMuted.withValues(alpha: 0.7),
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        'No destinations found',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Try searching for another place or clear filters.',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 13,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextButton.icon(
                        onPressed: () {
                          _searchController.clear();
                          destinationProvider.resetFilters();
                        },
                        icon: const Icon(Icons.refresh_rounded, size: 18),
                        label: const Text('Reset Search & Filters'),
                        style: TextButton.styleFrom(
                          foregroundColor: AppColors.primary,
                        ),
                      ),
                    ],
                  ),
                ),
              )
            else ...[
              // Horizontal Scrollable Cards
              SliverToBoxAdapter(
                child: SizedBox(
                  height: 250,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    physics: const BouncingScrollPhysics(),
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    itemCount: filteredList.length,
                    separatorBuilder: (context, index) => const SizedBox(width: 14),
                    itemBuilder: (context, index) {
                      final item = filteredList[index];
                      final isSaved = favoriteProvider.isSaved(item.id);
                      final displayItem = item.copyWith(isSaved: isSaved);

                      return DestinationCard(
                        destination: displayItem,
                        width: 210,
                        onFavoriteToggle: () {
                          favoriteProvider.toggleFavorite(
                            destination: item,
                            destinationProvider: destinationProvider,
                          );
                        },
                        onTap: () {
                          DestinationDetailSheet.show(
                            context,
                            destination: displayItem,
                            onFavoriteToggle: () {
                              favoriteProvider.toggleFavorite(
                                destination: item,
                                destinationProvider: destinationProvider,
                              );
                            },
                          );
                        },
                      );
                    },
                  ),
                ),
              ),

              // Responsive Two-Column Grid of Destinations
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 30),
                sliver: SliverGrid(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    childAspectRatio: 0.72,
                  ),
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final item = filteredList[index];
                      final isSaved = favoriteProvider.isSaved(item.id);
                      final displayItem = item.copyWith(isSaved: isSaved);

                      return DestinationCard(
                        destination: displayItem,
                        width: double.infinity,
                        onFavoriteToggle: () {
                          favoriteProvider.toggleFavorite(
                            destination: item,
                            destinationProvider: destinationProvider,
                          );
                        },
                        onTap: () {
                          DestinationDetailSheet.show(
                            context,
                            destination: displayItem,
                            onFavoriteToggle: () {
                              favoriteProvider.toggleFavorite(
                                destination: item,
                                destinationProvider: destinationProvider,
                              );
                            },
                          );
                        },
                      );
                    },
                    childCount: filteredList.length,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
