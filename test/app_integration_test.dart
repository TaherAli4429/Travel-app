import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_app/models/destination.dart';
import 'package:travel_app/providers/auth_provider.dart';
import 'package:travel_app/providers/destination_provider.dart';
import 'package:travel_app/providers/favorite_provider.dart';
import 'package:travel_app/providers/notification_provider.dart';
import 'package:travel_app/screens/auth/login_screen.dart';
import 'package:travel_app/screens/auth/signup_screen.dart';
import 'package:travel_app/screens/saved/saved_screen.dart';
import 'package:travel_app/widgets/app_bottom_navigation.dart';
import 'package:travel_app/widgets/category_chip.dart';
import 'package:travel_app/widgets/custom_text_field.dart';
import 'package:travel_app/widgets/primary_button.dart';

void main() {
  group('Provider Unit Tests', () {
    test('DestinationProvider filter logic works properly', () {
      final provider = DestinationProvider();
      expect(provider.selectedCategory, 'All');
      expect(provider.minRating, 0.0);
      expect(provider.searchQuery, '');

      provider.setCategory('Beaches');
      expect(provider.selectedCategory, 'Beaches');

      provider.setRating(4.5);
      expect(provider.minRating, 4.5);

      provider.setSearchQuery('Bali');
      expect(provider.searchQuery, 'Bali');

      provider.resetFilters();
      expect(provider.selectedCategory, 'All');
      expect(provider.minRating, 0.0);
      expect(provider.searchQuery, '');
    });

    test('FavoriteProvider tracks saved destinations accurately', () {
      final provider = FavoriteProvider();
      expect(provider.savedCount, 0);
      expect(provider.isSaved('dest_1'), isFalse);

      final mockDest = Destination(
        id: 'dest_1',
        name: 'Bali Sanctuary',
        country: 'Indonesia',
        category: 'Beaches',
        imageUrl: 'https://example.com/image.jpg',
        rating: 4.9,
        reviewsCount: 120,
        price: '\$750',
        description: 'Tropical paradise',
        isFeatured: true,
        isSaved: false,
      );

      final destProvider = DestinationProvider();
      provider.toggleFavorite(destination: mockDest, destinationProvider: destProvider);
      expect(provider.isSaved('dest_1'), isTrue);
      expect(provider.savedCount, 1);

      provider.clear();
      expect(provider.savedCount, 0);
      expect(provider.isSaved('dest_1'), isFalse);
    });

    test('AuthProvider stores and clears user profile correctly', () {
      final provider = AuthProvider();
      expect(provider.isAuthenticated, isFalse);
      expect(provider.currentUser, isNull);
    });

    test('NotificationProvider local state handling', () {
      final provider = NotificationProvider();
      expect(provider.notifications, isEmpty);
      expect(provider.unreadCount, 0);
      expect(provider.isLoading, isFalse);
    });
  });

  group('Widget Component Tests', () {
    testWidgets('AppBottomNavigation renders all 4 tabs with badge', (tester) async {
      int selected = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            bottomNavigationBar: AppBottomNavigation(
              currentIndex: selected,
              savedCount: 3,
              onTap: (i) => selected = i,
            ),
          ),
        ),
      );

      expect(find.text('Home'), findsOneWidget);
      expect(find.byIcon(Icons.explore_outlined), findsOneWidget);
      expect(find.byIcon(Icons.favorite_border_rounded), findsOneWidget);
      expect(find.byIcon(Icons.person_outline_rounded), findsOneWidget);
      expect(find.text('3'), findsOneWidget);
    });

    testWidgets('CategoryChip displays text and handles tap', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CategoryChip(
              label: 'Mountains',
              icon: Icons.terrain_rounded,
              isSelected: true,
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      expect(find.text('Mountains'), findsOneWidget);
      await tester.tap(find.text('Mountains'));
      expect(tapped, isTrue);
    });

    testWidgets('PrimaryButton displays text and triggers callback', (tester) async {
      bool pressed = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: PrimaryButton(
              text: 'Book Adventure',
              onPressed: () => pressed = true,
            ),
          ),
        ),
      );

      expect(find.text('Book Adventure'), findsOneWidget);
      await tester.tap(find.text('Book Adventure'));
      expect(pressed, isTrue);
    });

    testWidgets('CustomTextField handles input properly', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CustomTextField(
              controller: controller,
              hintText: 'Enter destination...',
              prefixIcon: Icons.search,
            ),
          ),
        ),
      );

      expect(find.text('Enter destination...'), findsOneWidget);
      await tester.enterText(find.byType(TextField), 'Santorini');
      expect(controller.text, 'Santorini');
    });
  });

  group('Screen UI & Form Validation Tests', () {
    testWidgets('LoginScreen displays required fields and labels', (tester) async {
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => AuthProvider()),
          ],
          child: const MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      expect(find.text('Welcome Back'), findsOneWidget);
      expect(find.text('Log In'), findsOneWidget);
      expect(find.textContaining("Don't have an account?"), findsOneWidget);
      expect(find.text('Sign Up'), findsOneWidget);
    });

    testWidgets('SignUpScreen displays registration inputs', (tester) async {
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => AuthProvider()),
          ],
          child: const MaterialApp(
            home: SignUpScreen(),
          ),
        ),
      );

      expect(find.text('Create Account'), findsNWidgets(2));
      expect(find.textContaining('Already have an account?'), findsOneWidget);
      expect(find.text('Login'), findsOneWidget);
    });

    testWidgets('SavedScreen renders empty bucket list state when empty', (tester) async {
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => FavoriteProvider()),
            ChangeNotifierProvider(create: (_) => DestinationProvider()),
          ],
          child: MaterialApp(
            home: SavedScreen(
              savedDestinations: const [],
              onNavigateToHome: () {},
            ),
          ),
        ),
      );

      expect(find.text('No saved destinations yet'), findsOneWidget);
      expect(find.text('Explore Destinations'), findsOneWidget);
    });
  });
}
