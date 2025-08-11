import 'package:flutter/material.dart';
import 'register.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _isLoginHovered = false;
  bool _isRegisterHovered = false;

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
              Image.asset('assets/logo.png', width: 120),
              SizedBox(height: 10),

              // judul
              Text(
                "App Kesehatan Bangkalan",
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.blueAccent,
                ),
              ),
              SizedBox(height: 40),

              // tombol login
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
                      print("Login Chicked");
                    },
                    child: Text(
                      "Login",
                      style: TextStyle(color: Colors.white, fontSize: 18),
                    ),
                  ),
                ),
              ),
              SizedBox(height: 20),
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
