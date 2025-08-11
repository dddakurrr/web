import 'package:flutter/material.dart'; // mengimport library flutter untuk material desain seperti (Scaffold, AppBar, MaterialApp)

// MaterialApp berfungsi untuk mengatur judul app, menentukan tema global, mengatur navigasi dan rute. untuk Scaffold merupakan layout halaman. AppBar merupakan header navbar aplikasi.

import 'package:mobile_app/screens/dashboard.dart'; // mengimport file dashboard.dart
import 'screens/welcome.dart'; // import halaman welcome
import 'screens/login_screens.dart'; // import halaman login
import 'screens/register.dart'; // import halaman register
import 'screens/pendaftaran.dart'; // import halaman pendaftaran pasien

// Fungsi Utama yang pertama kali dijalankan
void main() {
  runApp(MyApp());
}

// untuk mendeklarasikan MyApp sebagai halaman utama aplikasi
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override // sebagai penanda method statelessWidget
  Widget build(BuildContext context) {
    return MaterialApp(
      // widget utama flutter untuk aplikasi material desain
      debugShowCheckedModeBanner: false, // untuk menghilangkan label debug
      title: 'App Kesehatan Bangkalan', // Judul aplikasi
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ), // untuk mengatur tama aplikasi dengan warna utama biru
      initialRoute:
          '/', // untuk rute pertama yang dijalankan saat aplikasi dimulai
      routes: {
        '/': (context) => const WelcomeScreen(), // menuju ke halaman welcome
        '/login': (context) =>
            const LoginScreen(), // menuju ke halaman login user
        '/register': (context) =>
            const RegisterScreen(), // menuju ke halaman daftar user
      },
      onGenerateRoute: (settings) {
        // untuk membuat route dinamis
        //  merupakan settingan apabila ke halaman dashboard muncul apa saja
        if (settings.name == '/dashboard') {
          final args = settings.arguments as Map<String, dynamic>;
          return MaterialPageRoute(
            builder: (context) => DashboardScreen(username: args['username']),
          );
        }

        //  merupakan settingan apabila ke halaman pendaftaran pasien muncul apa saja
        if (settings.name == '/pendaftaran') {
          final args = settings.arguments as Map<String, dynamic>;
          return MaterialPageRoute(
            builder: (context) =>
                PendaftaranPasienScreen(username: args['username']),
          );
        }

        return null;
      },
    );
  }
}
