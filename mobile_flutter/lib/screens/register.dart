import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:awesome_dialog/awesome_dialog.dart';
import 'dart:convert';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  // form key untuk validasi
  final _formkey = GlobalKey<FormState>();

  // variabel untuk simpan input dari user
  String username = '';
  String email = '';
  String password = '';

  Future<void> registerUser() async {
    final url = Uri.parse('http://192.168.1.5:5000/api/register');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      var data = jsonDecode(response.body);

      AwesomeDialog(
        context: context,
        dialogType: DialogType.success,
        animType: AnimType.bottomSlide,
        title: 'Berhasil',
        desc: data['message'] ?? 'Registrasi Berhasil',
        btnOkOnPress: () {
          Navigator.pop(context);
        },
      ).show();
    } else {
      var data = jsonDecode(response.body);
      AwesomeDialog(
        context: context,
        dialogType: DialogType.error,
        animType: AnimType.bottomSlide,
        title: 'Gagal',
        desc: data['message'] ?? 'Email sudah dipakai, gunakan yang lain',
        btnOkOnPress: () {},
      ).show();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Register'),
        backgroundColor: Colors.blueAccent,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0), // padding sekitar layar
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 30), // jarak atas
              // logo
              Image.asset('assets/logo.png', width: 100),
              const SizedBox(height: 10),

              // judul aplikasi
              const Text(
                "App Kesehatan Bangkalan",
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.blueAccent,
                ),
              ),
              const SizedBox(height: 30),

              // form register
              Form(
                key: _formkey,
                child: Column(
                  children: [
                    // username form kolom
                    TextFormField(
                      decoration: const InputDecoration(
                        labelText: 'Username Pasien',
                        border: OutlineInputBorder(),
                      ),
                      onSaved: (val) => username = val!,
                      validator: (val) =>
                          val!.isEmpty ? 'Username wajib diisi' : null,
                    ),
                    const SizedBox(height: 15),

                    // email form kolom
                    TextFormField(
                      decoration: const InputDecoration(
                        labelText: 'Email Pasien',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.emailAddress,
                      onSaved: (val) => email = val!,
                      validator: (val) =>
                          val!.contains('@') ? null : 'Email tidak valid',
                    ),
                    const SizedBox(height: 15),

                    // password form kolom
                    TextFormField(
                      decoration: const InputDecoration(
                        labelText: 'Password Baru',
                        border: OutlineInputBorder(),
                      ),
                      obscureText: true,
                      onSaved: (val) => password = val!,
                      validator: (val) =>
                          val!.length < 6 ? 'Minimal 6 karakter' : null,
                    ),
                    const SizedBox(height: 25),

                    // Tombol register
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadiusGeometry.circular(12),
                          ),
                        ),
                        onPressed: () {
                          if (_formkey.currentState!.validate()) {
                            _formkey.currentState!.save();
                            print("Username: $username");
                            print("Email: $email");
                            print("Password: $password");

                            // panggil API
                            registerUser();
                          }
                        },
                        child: const Text(
                          "Register",
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
