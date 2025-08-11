import 'package:flutter/material.dart'; // berfungsi import library material desain untuk UI

// baris 4-11 : berfungsi untuk membuat halaman dashboard yang menerima parameter username
class DashboardScreen extends StatefulWidget {
  final String username;

  const DashboardScreen({super.key, required this.username});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex =
      0; // untuk menyimpan index menu bottom navigator yang dipilih

  // Untuk Membuat UI halaman dashboard
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading:
            false, // untuk menghilangkan tombol back di navbar
        backgroundColor: Colors.lightBlueAccent,
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [Image.asset('assets/logo_nobg.png', width: 100)],
            ), // menampilkan logo di navbar sebelah kiri

            Text(
              'Hello, ${widget.username}',
              style: const TextStyle(
                fontSize: 14,
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ), // membuat sapaan dengan menggunakan username
            ),
          ],
        ),
        actions: [],
      ),

      // menu dashboard
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: ListView(
          // supaya bisa scroll ke bawah/atas
          children: [
            _buildMenuButton(
              // button pendaftaran pasien
              title: 'Pendaftaran Pasien',
              icon: Icons.person_add,
              color: Colors.green,
              onTap: () {
                // diarahkan ke halaman pendaftaran
                Navigator.pushNamed(
                  context,
                  '/pendaftaran',
                  arguments: {'username': widget.username},
                );
              },
            ),
            const SizedBox(height: 20),
            _buildMenuButton(
              // button peta sebaran
              title: 'Peta Sebaran',
              icon: Icons.map,
              color: Colors.green,
              onTap: () {
                // navigasi ke halaman peta sebaran
              },
            ),
            const SizedBox(height: 20),
            _buildMenuButton(
              // button info
              title: 'Tentang',
              icon: Icons.info,
              color: Colors.orange,
              onTap: () {
                // navigasi ke halaman info
              },
            ),
          ],
        ),
      ),

      // baris 81-101 : membuat bottom yang berisikan beranda, puskesmas dan akun
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        selectedItemColor: Colors.blueAccent,
        unselectedItemColor: Colors.grey,
        items: const [
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

  // baris 115-132 : berfungsi membuat tombol menu dengan ketentuan icon + judul, warna border sesuai dengan parameter dan efek klik.
  Widget _buildMenuButton({
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color, width: 2),
        ),
        child: Row(
          children: [
            Icon(icon, size: 30, color: color),
            const SizedBox(width: 20),
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
