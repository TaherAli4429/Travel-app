import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_colors.dart';
import '../../models/destination.dart';
import '../../providers/destination_provider.dart';
import '../../providers/favorite_provider.dart';
import '../../widgets/destination_card.dart';
import '../../widgets/destination_detail_sheet.dart';
import '../../widgets/primary_button.dart';

class SavedScreen extends StatelessWidget {
  final List<Destination>? savedDestinations;
  final Function(String id)? onToggleFavorite;
  final VoidCallback onNavigateToHome;

  const SavedScreen({
    super.key,
    this.savedDestinations,
    this.onToggleFavorite,
    required this.onNavigateToHome,
  });

  @override
  Widget build(BuildContext context) {
    final favoriteProvider = Provider.of<FavoriteProvider>(context);
    final destinationProvider = Provider.of<DestinationProvider>(context);

    final list = savedDestinations ?? favoriteProvider.savedDestinations;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Saved Places',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: AppColors.textPrimary,
              ),
            ),
            if (list.isNotEmpty) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  '${list.length}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppColors.textPrimary),
            tooltip: 'Refresh saved places',
            onPressed: () {
              favoriteProvider.fetchFavorites();
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await favoriteProvider.fetchFavorites();
        },
        child: list.isEmpty
            ? LayoutBuilder(
                builder: (context, constraints) => SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(
                    parent: BouncingScrollPhysics(),
                  ),
                  child: ConstrainedBox(
                    constraints: BoxConstraints(minHeight: constraints.maxHeight),
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 32),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(24),
                              decoration: BoxDecoration(
                                color: AppColors.heart.withValues(alpha: 0.08),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(
                                Icons.favorite_border_rounded,
                                size: 64,
                                color: AppColors.heart,
                              ),
                            ),
                            const SizedBox(height: 20),
                            const Text(
                              'No saved destinations yet',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.w700,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              'Explore world-class destinations and tap the heart icon to save them to your travel bucket list.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: 14,
                                color: AppColors.textSecondary,
                                height: 1.5,
                              ),
                            ),
                            const SizedBox(height: 24),
                            SizedBox(
                              width: 240,
                              child: PrimaryButton(
                                text: 'Explore Destinations',
                                icon: Icons.explore_rounded,
                                onPressed: onNavigateToHome,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              )
            : GridView.builder(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
                physics: const AlwaysScrollableScrollPhysics(
                  parent: BouncingScrollPhysics(),
                ),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  childAspectRatio: 0.72,
                ),
                itemCount: list.length,
                itemBuilder: (context, index) {
                  final item = list[index];
                  final isSaved = favoriteProvider.isSaved(item.id);
                  final displayItem = item.copyWith(isSaved: isSaved);

                  void handleToggle() {
                    if (onToggleFavorite != null) {
                      onToggleFavorite!(item.id);
                    } else {
                      favoriteProvider.toggleFavorite(
                        destination: item,
                        destinationProvider: destinationProvider,
                      );
                    }
                  }

                  return DestinationCard(
                    destination: displayItem,
                    width: double.infinity,
                    onFavoriteToggle: handleToggle,
                    onTap: () {
                      DestinationDetailSheet.show(
                        context,
                        destination: displayItem,
                        onFavoriteToggle: handleToggle,
                      );
                    },
                  );
                },
              ),
      ),
    );
  }
}
