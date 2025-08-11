// baris ke 2 - 4 mengimport library yang ada
import 'package:flutter/material.dart';
import 'register.dart';
import 'login_screens.dart';

// mendeklarasi halaman utama untuk menghubungkan UI dan logika pada halaman welcome
class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

// baris 15 -17 : merupakan variable dari state dari widget yang berfungsi untuk menyimpan login dan register apakah tombol sedang dihover atau tidak
class _WelcomeScreenState extends State<WelcomeScreen> {
  bool _isLoginHovered = false;
  bool _isRegisterHovered = false;

  // baris 20 - 108 : berfungsi untuk menggambarkan UI halaman wlcome semua konten ada didalam Scaffold.
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Baris 31 - 41 : berfungsi untuk menampilkan logo aplikasi dan judul di tengah layar.
              Image.asset('assets/logo_fix.png', width: 200),
              SizedBox(height: 10),
              Text(
                "App Kesehatan Bangkalan",
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.blueAccent,
                ),
              ),
              SizedBox(height: 40),

              // baris 44-70: tombol login dengan hover yang berfungsi untuk memberikan efek hover dan saat diklik menuju ke halaman login
              MouseRegion(
                onEnter: (_) => setState(() => _isLoginHovered = true),
                onExit: (_) => setState(() => _isLoginHovered = false),
                child: AnimatedContainer(
                  duration: Duration(milliseconds: 200),
                  width: double.infinity,
                  height: 50,
                  decoration: BoxDecoration(
                    color: _isLoginHovered
                        ? Colors.blue[700]
                        : Colors.blueAccent,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => LoginScreen()),
                      );
                    },
                    child: Text(
                      "Login",
                      style: TextStyle(color: Colors.white, fontSize: 18),
                    ),
                  ),
                ),
              ),
              SizedBox(height: 20),
              // baris 73-101 : tombol register dengan hover yang berfungsi untuk memberikan efek hover dan saat diklik menuju ke halaman register
              MouseRegion(
                onEnter: (_) => setState(() => _isRegisterHovered = true),
                onExit: (_) => setState(() => _isRegisterHovered = false),
                child: AnimatedContainer(
                  duration: Duration(milliseconds: 200),
                  width: double.infinity,
                  height: 50,
                  decoration: BoxDecoration(
                    color: _isRegisterHovered
                        ? Colors.green[700]
                        : Colors.green,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => RegisterScreen(),
                        ),
                      );
                    },
                    child: Text(
                      "Register",
                      style: TextStyle(color: Colors.white, fontSize: 18),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
