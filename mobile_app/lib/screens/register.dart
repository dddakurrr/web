// baris 2-5 : Import library (untuk baris 3 berfungsi untuk mengirim request HTTP login ke API. untuk baris 4 berfungsi untuk menampilkan dialog notifikasi. untuk baris 5 berfungsi untuk mengubah data dari/ke JSON)
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:awesome_dialog/awesome_dialog.dart';
import 'dart:convert';

// baris 8-13 : berfungsi untuk halaman register yang memiliki state (karena ada loading state, input form, dll), kemudian untuk baris 12 berfungsi untuk createState() menghubungkan ke _RegisterScreenState
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

  // baris 25-35 berfungsi untuk mengirimkan POST request ke API register
  Future<void> registerUser() async {
    final url =
        Uri.parse('https://sig-pneumonia-4a86.up.railway.app/api/register');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );

    // baris 38-50 berfungsi untuk menampilkan popup jika sukses dan ketika klik ok akan kembali kehalaman sebelumnya. lalu baris 51-61 berfungsi untuk menampilkan popup jika gagal register.
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

  // baris 65-175 : halaman UI halaman register user
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
              Image.asset('assets/logo_fix.png', width: 100),
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
                            borderRadius: BorderRadius.circular(12),
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
