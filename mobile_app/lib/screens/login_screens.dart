// baris 2-5 : Import library (untuk baris 3 berfungsi untuk mengirim request HTTP login ke API. untuk baris 4 berfungsi untuk menampilkan dialog notifikasi. untuk baris 5 berfungsi untuk mengubah data dari/ke JSON)
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:awesome_dialog/awesome_dialog.dart';
import 'dart:convert';

// baris 8-13 : berfungsi untuk halaman login yang memiliki state (karena ada loading state, input form, dll), kemudian untuk baris 12 berfungsi untuk createState() menghubungkan ke _LoginScreenState
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

// baris 16-21 (State & Variable). untuk _formKey berfungsi validasi form (Email & password). untuk email & password berfungsi menyimpan input user. _isLoading berfungsi untuk menampilkan loading indicator di tombol login.
class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();

  String email = '';
  String password = '';
  bool _isLoading = false;

  // baris 24-67 : fungsi login (HTTP POST) berfungsi untuk mengaktifkan loading, mengrim request POST ke API login dengan menggunakan email & password dalam format JSON. untuk baris 38-67 berfungsi untuk jika login sukses maka akan menampilkan dialog sukses dan menuju ke halaman dashboard. jika login gagal akan muncul tampilan dialog error
  Future<void> loginUser() async {
    setState(() => _isLoading = true);

    final url =
        Uri.parse('https://sig-pneumonia-4a86.up.railway.app/api/login');
    final response = await http
        .post(
          url,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'email': email, 'password': password}),
        )
        .timeout(const Duration(seconds: 10));

    setState(() => _isLoading = false);

    if (response.statusCode == 200) {
      var data = jsonDecode(response.body);
      String username = data['username'];

      AwesomeDialog(
        context: context,
        dialogType: DialogType.success,
        animType: AnimType.bottomSlide,
        title: 'Berhasil',
        desc: data['message'] ?? 'Login Berhasil',
        btnOkOnPress: () {
          Navigator.pushReplacementNamed(
            context,
            '/dashboard',
            arguments: {'username': username},
          );
        },
      ).show();
    } else {
      var data = jsonDecode(response.body);
      AwesomeDialog(
        context: context,
        dialogType: DialogType.error,
        animType: AnimType.bottomSlide,
        title: 'Gagal',
        desc: data['message'] ?? 'Username atau Password Salah',
        btnOkOnPress: () {},
      ).show();
    }
  }

  // baris 70-159 : berfungsi untuk UI / tampilan halaman login seperti AppBar, logo, form dan tombol login.
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Login'),
        backgroundColor: Colors.blueAccent,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 30),
              Image.asset('assets/logo_fix.png', width: 150), // logo app
              const SizedBox(height: 10),
              const Text(
                "App Kesehatan Bangkalan", // judul app
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.blueAccent,
                ),
              ),
              const SizedBox(height: 30),
              Form(
                // form login
                key: _formKey,
                child: Column(
                  children: [
                    TextFormField(
                      // untuk menginput email wajib ada @
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        border: OutlineInputBorder(),
                      ),
                      onSaved: (val) => email = val!,
                      validator: (val) =>
                          val!.contains('@') ? null : 'Email tidak valid',
                    ),
                    const SizedBox(height: 15),

                    // Untuk menginput Password
                    TextFormField(
                      decoration: const InputDecoration(
                        labelText: 'Password',
                        border: OutlineInputBorder(),
                      ),
                      obscureText: true,
                      onSaved: (val) => password = val!,
                      validator: (val) =>
                          val!.isEmpty ? 'Password wajib diisi' : null,
                    ),
                    const SizedBox(height: 25),
                    SizedBox(
                      // berfungsi untuk tombol login
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        onPressed: _isLoading
                            ? null
                            : () {
                                if (_formKey.currentState!.validate()) {
                                  _formKey.currentState!.save();
                                  loginUser();
                                }
                              },
                        child: _isLoading
                            ? const CircularProgressIndicator(
                                color: Colors.white,
                              )
                            : const Text(
                                "Login",
                                style: TextStyle(fontSize: 18),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
