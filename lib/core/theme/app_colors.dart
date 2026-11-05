import 'package:flutter/material.dart';

class AppColors {
  // Brand colors
  static const Color primary = Color(0xFF176B87); // Deep ocean blue
  static const Color primaryDark = Color(0xFF04364A); // Navy depth
  static const Color secondary = Color(0xFF64CCC5); // Turquoise
  static const Color lightTeal = Color(0xFFDAFFFB); // Pale aqua tint
  static const Color accent = Color(0xFF05B292); // Vivid accent teal

  // Neutral background & surfaces
  static const Color background = Color(0xFFF7FAFC);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cardBg = Color(0xFFFFFFFF);

  // Typography colors
  static const Color textPrimary = Color(0xFF172B3A); // Deep slate
  static const Color textSecondary = Color(0xFF718096); // Cool grey
  static const Color textMuted = Color(0xFFA0AEC0); // Subtle placeholder

  // Form input colors
  static const Color inputBorder = Color(0xFFE2E8F0);
  static const Color inputFocusBorder = Color(0xFF176B87);
  static const Color inputFill = Color(0xFFF8FAFC);

  // Status & Accents
  static const Color star = Color(0xFFFFB800);
  static const Color heart = Color(0xFFFF4D6D);
  static const Color success = Color(0xFF10B981);
  static const Color error = Color(0xFFE53E3E);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF176B87), Color(0xFF64CCC5)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient heroGradient = LinearGradient(
    colors: [
      Colors.transparent,
      Color(0x99000000),
      Color(0xDD000000),
    ],
    stops: [0.4, 0.75, 1.0],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
