// baris 2-8 : mengimport yang diperlukan (baris 5: menampilkan peta google dan baris 6: mendapatkan lokasi GPS)
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/gestures.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// berfungsi untuk halaman pendaftaran pasien, menerima username dari dashboard
class PendaftaranPasienScreen extends StatefulWidget {
  final String username;

  const PendaftaranPasienScreen({super.key, required this.username});

  @override
  State<PendaftaranPasienScreen> createState() =>
      _PendaftaranPasienScreenState();
}

class _PendaftaranPasienScreenState extends State<PendaftaranPasienScreen> {
  // untuk menyimpan nilai form dan data lokasi pasien
  final _formKey = GlobalKey<FormState>();
  TextEditingController namaCtrl = TextEditingController();
  TextEditingController nikCtrl = TextEditingController();
  TextEditingController umurCtrl = TextEditingController();
  TextEditingController alamatCtrl = TextEditingController();
  TextEditingController desaCtrl = TextEditingController();
  TextEditingController kecamatanCtrl = TextEditingController();
  TextEditingController puskesmasCtrl = TextEditingController();

  String jenisKelamin = 'Laki-laki';
  LatLng? selectedLocation; // lokasi / koordinat yang dipilih
  GoogleMapController? mapController;
  bool _isLoading = false;
  bool _isUpdatingLocation = false;
  int? idDesa;
  bool _nikSudahDipakai = false;

  // berfungsi untuk mengambil lokasi awal gps user berada
  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  //
  Future<void> _getCurrentLocation() async {
    bool serviceEnambled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnambled) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Nyalakan GPS untuk melanjutkan")),
      );
      return;
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }
    if (permission == LocationPermission.deniedForever) return;

    try {
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.low,
        timeLimit: const Duration(seconds: 10),
      );

      setState(() {
        selectedLocation = LatLng(position.latitude, position.longitude);
      });

      await _updateAlamatDariKoordinat(position.latitude, position.longitude);
    } catch (e) {
      // kalau terjadi timeout atau error, pakai lokasi terakhir
      Position? lastPos = await Geolocator.getLastKnownPosition();
      if (lastPos != null) {
        setState(() {
          selectedLocation = LatLng(lastPos.latitude, lastPos.longitude);
        });
        await _updateAlamatDariKoordinat(lastPos.latitude, lastPos.longitude);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Tidak dapat menemukan lokasi")),
        );
      }
    }
  }

  Future<void> _updateAlamatDariKoordinat(double lat, double lng) async {
    setState(() => _isUpdatingLocation = true);

    final url =
        Uri.parse("https://sig-pneumonia-4a86.up.railway.app/cari-wilayah");
    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"lat": lat, "lng": lng}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      setState(() {
        desaCtrl.text = data['nama_desa'] ?? '';
        kecamatanCtrl.text = data['kecamatan'] ?? '';
        puskesmasCtrl.text = data['puskesmas'] ?? '';
        idDesa = data['id_desa'];
      });
    } else {
      print("Gagal mengambil data lokasi: ${response.body}");
    }

    setState(() => _isUpdatingLocation = false);
  }

  // pop up konfirmasi
  Future<bool?> _showKonfirmasiDialog() {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Konfirmasi"),
        content: const Text(
          "Apakah Anda sudah yakin dengan isi form? Setelah dikirim, data tidak dapat diubah kembali.",
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Belum"),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text("Sudah"),
          ),
        ],
      ),
    );
  }

  // pop up berhasil
  Future<void> _showResultDialog(String title, String message) async {
    await showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              if (title == "Pendaftaran Berhasil") {
                // refresh halaman
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        PendaftaranPasienScreen(username: widget.username),
                  ),
                );
              }
            },
            child: const Text("OK"),
          ),
        ],
      ),
    );
  }

  Future<void> _daftarPasien() async {
    if (!_formKey.currentState!.validate() ||
        selectedLocation == null ||
        idDesa == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Wilayah tdak terdeteksi")));
      return;
    }

    setState(() => _isLoading = true);

    final url =
        Uri.parse("https://sig-pneumonia-4a86.up.railway.app/api/pendaftaran");
    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "nama": namaCtrl.text,
        "nik": nikCtrl.text,
        "umur": umurCtrl.text,
        "jenis_kelamin": jenisKelamin,
        "alamat": alamatCtrl.text,
        "desa_kelurahan": desaCtrl.text,
        "kecamatan": kecamatanCtrl.text,
        "puskesmas": puskesmasCtrl.text,
        "latitude": selectedLocation!.latitude,
        "longitude": selectedLocation!.longitude,
        "id_desa": idDesa,
      }),
    );

    setState(() => _isLoading = false);

    if (response.statusCode == 200) {
      await _showResultDialog(
        "Pendaftaran Berhasil",
        "Jika ada kesalahan, Silakan menuju puskesmas terdekat.",
      );
    } else if (response.statusCode == 409) {
      await _showResultDialog(
        "Pendaftaran Gagal",
        "NIK sudah digunakan, Masukkan NIK dengan benar jika ada kendala langsung menuju puskesmas terdekat.",
      );
    } else {
      await _showResultDialog("Gagal", "Terjadi kesalahan, silakan coba lagi.");
    }
  }

  Future<void> _cekNikSudahAda(String nik) async {
    final url =
        Uri.parse("https://sig-pneumonia-4a86.up.railway.app/api/cek-nik");
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"nik": nik}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // backend mengirim { "exists": true/false }
        setState(() {
          _nikSudahDipakai = data['exists'] ?? false;
        });
      }
    } catch (e) {
      print("Error cek NIK: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.lightBlueAccent,
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Image.asset('assets/logo_nobg.png', width: 100),
            Text(
              'Hello, ${widget.username}',
              style: const TextStyle(
                fontSize: 14,
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Form Pendaftaran Pasien",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: namaCtrl,
                    decoration: const InputDecoration(
                      labelText: "Nama Lengkap",
                      border: OutlineInputBorder(),
                    ),
                    validator: (val) => val!.isEmpty ? "Wajib diisi" : null,
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: nikCtrl,
                    decoration: InputDecoration(
                      labelText: "NIK Pasien",
                      border: OutlineInputBorder(),
                      suffixIcon: _nikSudahDipakai
                          ? Icon(Icons.error, color: Colors.red)
                          : null,
                    ),
                    keyboardType: TextInputType.number,
                    validator: (val) => val!.length < 16
                        ? "NIK tidak valid"
                        : _nikSudahDipakai
                            ? "NIK sudah digunakan"
                            : null,
                    onChanged: (val) async {
                      if (val.length == 16) {
                        _cekNikSudahAda(val);
                      } else {
                        setState(() => _nikSudahDipakai = false);
                      }
                    },
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: umurCtrl,
                    decoration: const InputDecoration(
                      labelText: "Umur Pasien",
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                    validator: (val) => val!.isEmpty ? "Wajib diisi" : null,
                  ),
                  const SizedBox(height: 10),
                  DropdownButtonFormField(
                    value: jenisKelamin,
                    items: ['Laki-laki', 'Perempuan']
                        .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                        .toList(),
                    onChanged: (val) => setState(() => jenisKelamin = val!),
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      labelText: "Jenis Kelamin",
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: alamatCtrl,
                    decoration: const InputDecoration(
                      labelText: "Alamat Pasien",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: desaCtrl,
                    decoration: const InputDecoration(
                      labelText: "Desa/Kelurahan",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: kecamatanCtrl,
                    decoration: const InputDecoration(
                      labelText: "Kecamatan",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: puskesmasCtrl,
                    decoration: const InputDecoration(
                      labelText: "Puskesmas",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 10),
                  SizedBox(
                    height: 250,
                    child: selectedLocation == null
                        ? const Center(child: CircularProgressIndicator())
                        : Stack(
                            children: [
                              GoogleMap(
                                initialCameraPosition: CameraPosition(
                                  target: selectedLocation!,
                                  zoom: 15,
                                ),
                                onTap: (pos) async {
                                  setState(() => selectedLocation = pos);
                                  await _updateAlamatDariKoordinat(
                                    pos.latitude,
                                    pos.longitude,
                                  );
                                },
                                markers: {
                                  Marker(
                                    markerId: const MarkerId("lokasi"),
                                    position: selectedLocation!,
                                  ),
                                },
                                onMapCreated: (controller) =>
                                    mapController = controller,
                                myLocationEnabled: true,
                                zoomGesturesEnabled: true,
                                scrollGesturesEnabled: true,
                                rotateGesturesEnabled: true,
                                tiltGesturesEnabled: true,
                                gestureRecognizers: <Factory<
                                    OneSequenceGestureRecognizer>>{
                                  Factory<OneSequenceGestureRecognizer>(
                                    () => EagerGestureRecognizer(),
                                  ),
                                },
                              ),
                              if (_isUpdatingLocation)
                                const Positioned.fill(
                                  child: Center(
                                    child: CircularProgressIndicator(
                                      color: Colors.blue,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: _isLoading
                          ? null
                          : () async {
                              final yakin = await _showKonfirmasiDialog();
                              if (yakin == true) {
                                await _daftarPasien();
                              }
                            },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                      ),
                      child: _isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text(
                              "Daftar Sekarang",
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
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        onTap: (index) {},
        selectedItemColor: Colors.lightBlueAccent,
        unselectedItemColor: Colors.grey,
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Beranda'),
          BottomNavigationBarItem(
            icon: Icon(Icons.local_hospital),
            label: 'Puskesmas',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_circle),
            label: 'Akun',
          ),
        ],
      ),
    );
  }
}
