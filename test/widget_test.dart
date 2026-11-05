import 'package:flutter_test/flutter_test.dart';
import 'package:travel_app/app.dart';

void main() {
  testWidgets('Wanderly App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const WanderlyApp());
    expect(find.text('Wanderly'), findsOneWidget);
  });
}
