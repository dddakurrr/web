import matplotlib.pyplot
matplotlib.use('Agg')
from flask import Flask, flash, render_template, request, session, redirect, url_for, jsonify, json
import os
import folium
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import geojson as gs
import psycopg2
import seaborn as sns
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from geopy.distance import great_circle
from shapely.geometry import Point, shape
from scipy.spatial.distance import pdist, squareform
from kneed import KneeLocator
from sqlalchemy import create_engine, text

# untuk mengatur flask dimana letak file yang sedang berjalan
app = Flask(__name__)
app.secret_key = 'amankan111'  # untuk mengamankan session pengguna

# connect ke database
engine = create_engine("postgresql+psycopg2://postgres.qsbtjgxxrinqelrgjotk:Gudangair0407@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres")

@app.route('/')
def index():
    return redirect(url_for('user_home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET',  'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']

        if not email or not pwd:
            flash('Email dan Password wajib diisi')
            return redirect(url_for('login'))
        
        try: 
            with engine.begin() as conn:
                query = text("SELECT username, password, role FROM data_user WHERE email = :email")
                result = conn.execute(query, {"email": email}).fetchone()

                if not result:
                    flash('email tidak terdaftar')
                    return redirect(url_for('login'))
                
                db_username, db_password, db_role = result

                if pwd == db_password:
                    session['user'] = db_username
                    session['role'] = db_role

                    if db_role == 'admin':
                        return redirect(url_for('dashboard'))
                    else:
                        return redirect(url_for('user_home'))
                else:
                    flash('Password Salah')
                    return redirect(url_for('login'))
            
        except Exception as e:
            flash(f"Gagal login: {str(e)}")
            return redirect(url_for('login'))
        
    return render_template('login.html')

# masuk ke halaman admin
@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        flash("Anda harus login sebagai admin untuk mengakses halaman ini")
        return redirect(url_for('login'))
    return render_template("home.html")     # untuk kembali halaman yang dituju

# masuk ke halaman user
@app.route('/user_home')
def user_home():
    return render_template("user_home.html")     # untuk kembali halaman yang dituju

@app.route('/daftar_puskesmas')
def daftar_puskesmas():
    with engine.begin() as conn:
        result = conn.execute(text("SELECT id_puskesmas, nama_puskesmas, alamat_puskesmas, nomor_telpon, link_maps FROM daftar_puskesmas")).fetchall()
    return render_template("daftar_puskesmas.html", daftar_puskesmas=result)

@app.route('/form-pasien')
def guest_form():
    return render_template('form_pasien.html')

@app.route('/simpan-pasien', methods=['POST'])
def simpan_pasien():
    data = request.get_json()

    print(" data masuk ")
    print(json.dumps(data, indent=2))

    if not data:
        return jsonify({"success": False, "message": "data kosong"}), 400
    
    nameDes = data.get('desa_kelurahan', '').strip().upper()

    with engine.begin() as conn:
        resId = conn.execute(text("SELECT MAX(id_pasien) FROM data_pasien"))
        maxId = resId.scalar() or 0
        newId = maxId + 1
    
        # auto set cluster menjadi (noise) & cari id_desa dari nama desa
        queryDes = text("SELECT id_desa FROM data_desa WHERE UPPER(nama_desa) = :desa LIMIT 1")
        resDes = conn.execute(queryDes, {"desa": nameDes})
        desId = resDes.scalar()

        if desId is None:
            return jsonify({"success": False, "message": f"Nama Desa '{nameDes}' tidak ditemukan di data_desa"}), 400

        # simpan ke database
        queryIns = text("""
            INSERT INTO data_pasien (
                id_pasien, nama, desa_kelurahan, kecamatan, kunjungan, jenis_kelamin, umur, puskesmas, latitude, longitude, id_desa, cluster
            )VALUES (
                :id_pasien, :nama, :desa, :kecamatan, :kunjungan, :jenis_kelamin, :umur,:puskesmas, :latitude, :longitude, :id_desa, :cluster
            )
        """)

        conn.execute(queryIns, {
            'id_pasien': newId,
            'nama': data['nama'],
            'desa': data['desa_kelurahan'],
            'kecamatan': data['kecamatan'],
            'kunjungan': data['kunjungan'],
            'jenis_kelamin': data['jenis_kelamin'],
            'umur': data['umur'],
            'puskesmas': data['puskesmas'],
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'id_desa': desId,
            'cluster': -1
        })

    return jsonify({'success': True, 'message': 'Data Pasien berhasil ditambahkan'})

@app.route('/home_pasien')
def home_pasien():
    return render_template('home_pasien.html')

@app.route('/halaman_tambah_pasien')
def halaman_tambah_pasien():
    return render_template('halaman_tambah_pasien.html')

@app.route('/kontak_kami')
def kontak_kami_pasien():
    return render_template('kontak_kami_pasien.html')

# membuat rute halaman dataset
@app.route('/dataset')
def ambil_dataset():

    # Query untuk mengambil data pasien
    query_pasien = "SELECT * FROM data_pasien ORDER BY id_pasien ASC;"
    df_pasien = pd.read_sql(query_pasien, engine)

    # kirim data ke template sebagai list untuk loop di jinja
    data_pasien = df_pasien.to_dict(orient='records')

    return render_template("dataset.html", data_pasien=data_pasien)

@app.route('/preprocessing')
def prepro():
    # Query untuk mengambil data pasien
    query_pasien = "SELECT * FROM data_pasien ORDER BY id_pasien ASC;"
    df_pasien = pd.read_sql(query_pasien, engine)

    # untuk drop kolom tidak digunakan
    df_pasien_baru = df_pasien.drop(columns=['id_pasien','tgl','nama','no.reg','desa_kelurahan','kecamatan','klasifikasi','kondisi_saat_kunjungan_ulang','keterangan','puskesmas','latitude','longitude','id_desa','cluster'])

    # One-Hot Encoding
    df_ohe = pd.get_dummies(df_pasien_baru, columns=['kunjungan','jenis_kelamin','tindak_lanjut','anti_biotika','faktor_risiko'], dtype=int)

    # MinMax Normalization
    scaler = MinMaxScaler()
    df_minmax = scaler.fit_transform(df_ohe)
    df_minmax = pd.DataFrame(df_minmax, columns=df_ohe.columns)

    return render_template("preprocessing.html",
                           kolom_ohe = df_ohe.columns,
                           data_ohe = df_ohe.to_dict(orient='records'),
                           kolom_minmax = df_minmax.columns,
                           data_minmax = df_minmax.to_dict(orient='records'))

@app.route('/matriks_jarak')
def jarak():
    # mengambil parameter halaman di url
    hal_jarak = int(request.args.get("hal_jarak", 0))
    batas = 15

    # Query untuk mengambil data pasien
    query_pasien = "SELECT * FROM data_pasien ORDER BY id_pasien ASC;"
    df_pasien = pd.read_sql(query_pasien, engine)

    # mengambil dataset yang akan diproses
    df_pasien_baru = df_pasien.drop(columns=['id_pasien','tgl','nama','no.reg','desa_kelurahan','kecamatan','klasifikasi','kondisi_saat_kunjungan_ulang','keterangan','puskesmas','latitude','longitude','id_desa', 'cluster'])

    # One-Hot Encoding
    df_ohe = pd.get_dummies(df_pasien_baru, columns=['kunjungan','jenis_kelamin','tindak_lanjut','anti_biotika','faktor_risiko'], dtype=int)

    # MinMax Normalization
    scaler = MinMaxScaler()
    df_minmax = scaler.fit_transform(df_ohe)

    # matriks jarak
    matriks_jarak = squareform(pdist(df_minmax, metric='euclidean'))
    df_jarak = pd.DataFrame(matriks_jarak)

    # hitung slice
    row_mulai = hal_jarak * batas
    row_akhir = row_mulai + batas
    col_mulai = hal_jarak * batas
    col_akhir = col_mulai + batas

    # untuk menampilkan matriks jarak secara bertahap
    df_sliced = df_jarak.iloc[row_mulai:row_akhir, col_mulai:col_akhir]
    data_jarak = df_sliced.to_dict(orient='records')
    kolom_jarak = df_sliced.columns
    indek_jarak = df_sliced.index.tolist()

    return render_template ("matriks_jarak.html",
                            kolom_jarak = kolom_jarak,
                            indek_jarak = indek_jarak,
                            data_jarak = data_jarak,
                            hal_jarak = hal_jarak)

# rute ke dbscan
@app.route('/dbscan', methods = ['GET', 'POST'])
def hitung():
    # Query untuk mengambil data pasien
    query_pasien = "SELECT * FROM data_pasien ORDER BY id_pasien ASC;"
    df_pasien = pd.read_sql(query_pasien, engine)

    # mengambil dataset yang akan diproses
    df_pasien_baru = df_pasien.drop(columns=['id_pasien','tgl','nama','no.reg','desa_kelurahan','kecamatan','klasifikasi','kondisi_saat_kunjungan_ulang','keterangan','puskesmas','latitude','longitude','id_desa','cluster'])

    # preprocessing
    df_ohe = pd.get_dummies(df_pasien_baru, columns=['kunjungan','jenis_kelamin','tindak_lanjut','anti_biotika','faktor_risiko'], dtype=int)
    scaler = MinMaxScaler()
    df_minmax = scaler.fit_transform(df_ohe)

    # inisialisasi variabel yang dibutuhkan 
    hasil_dbscan = None
    k_distance = []
    epsilon_eps = None
    silhouette_sil = None
    min_k = max_k = 0
    epsilon_input = None
    minpts_input = int(request.form.get('minpts', 3))   # default minpts yakni 3
    hasil_dbscan = None
    n_clusters = None
    n_noise = None
    jumlah_per_cluster = None

    # mencari nilai epsilon dari minimal tetangga (minpts)
    if request.method == 'POST':
        if 'minpts' in request.form and request.form['minpts']:
            minpts = int(request.form['minpts'])

            # menghitung k-distance
            neighbors = NearestNeighbors(n_neighbors=minpts)
            neighbors.fit(df_minmax)
            distances, _ = neighbors.kneighbors(df_minmax)
            k_distance = np.sort(distances[:, minpts - 1])

            # cari knee point
            kneeds = KneeLocator(range(len(k_distance)), k_distance, curve='convex', direction='increasing')
            epsilon_eps = round(k_distance[kneeds.knee], 2)
            min_k = round(float(k_distance.min()), 2)
            max_k = round(float(k_distance.max()), 2)

            # simpan plot 
            plt.figure(figsize=(10, 6))
            plt.plot(k_distance)
            plt.axhline(y=epsilon_eps, color='red', linestyle='--', label=f'Epsilon (knee point): {epsilon_eps:.2f}')
            plt.xlabel('Data Points')
            plt.ylabel(f'{minpts}-NN Distance')
            plt.title('Elbow Method')
            plt.legend()
            plt.grid(True)
            plt.savefig('static/plot_kdistance.png', bbox_inches='tight')
            plt.close()

            # jika nilai epsilon sudah ditemukan maka lanjut dilakukan DBSCAN 
            if 'epsilon' in request.form and request.form['epsilon']:
                epsilon_input = float(request.form['epsilon'])
                dbscan = DBSCAN(eps=epsilon_input, min_samples=minpts, metric='euclidean')
                cluster_labels = dbscan.fit_predict(df_minmax)
                
                # untuk updata kolom cluster dari hasil dbscan ke dalam tabel data_pasien
                with engine.begin() as connection:
                    for i, labels in enumerate(cluster_labels):
                        cluster_pasien = int(labels)
                        id_pasien = int(df_pasien.iloc[i]['id_pasien'])
                        connection.execute(text("UPDATE data_pasien SET cluster = :cluster WHERE id_pasien = :id"), {"cluster": cluster_pasien, "id": id_pasien})
                    
                        # Cek hasil update langsung
                        result = connection.execute(text("SELECT cluster, COUNT(*) FROM data_pasien GROUP BY cluster"))
                        print("Hasil update cluster:")
                        for row in result:
                            print(row)
                
                # menghitung berapa banyak jumlah cluster yang terbentuk dan jumlah data yang masuk kedalam cluster noise
                n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
                n_noise = list(cluster_labels).count(-1)

                # hitung jumlah per cluster
                unique, counts = np.unique(cluster_labels, return_counts=True)
                jumlah_per_cluster = dict(zip(unique, counts))

                # hitung nilai silhouette
                silhouette_sil = "-"
                if n_clusters > 1:
                    filtered = cluster_labels != -1
                    filtered_data = df_minmax[filtered]
                    silhouette_scored = squareform(pdist(filtered_data))
                    silhouette_sil = round(silhouette_score(silhouette_scored, cluster_labels[filtered], metric='precomputed'), 4)
                
                # menyimpan hasil dbscan kedalam variable 
                hasil_dbscan = {
                    'n_cluster':n_clusters,
                    'n_noise':n_noise,
                    'jumlah_per_cluster':jumlah_per_cluster,
                    'silhouette':silhouette_sil
                }

            # simpan history ke session
            if 'dbscan_history' not in session:
                session['dbscan_history'] = []
            
            session['dbscan_history'].append({
                'epsilon':epsilon_input,
                'minpts':minpts,
                'n_cluster':n_clusters,
                'n_noise':n_noise,
                'silhouette':silhouette_sil if silhouette_sil else "-"
            })
            session.modified = True
    
    # untuk membuka halaman dbscan dan mengirimkan data yangdibutuhkan untuk dbscan
    return render_template("dbscan.html", 
            k_distance=k_distance, epsilon_eps = epsilon_eps, minpts = minpts_input, min_k = min_k, max_k = max_k, epsilon = epsilon_input, hasil = hasil_dbscan)

# menampilkan nilai silhouette berupa tabel
@app.route('/silhouette')
def nilai():
    history = session.get('dbscan_history', [])
    return render_template("hasil_dbscan.html", history=history)

# melakukan visualisasi setiap pasien 
@app.route('/visualisasi/pasien')
def vis_pasien():
    #ambil tabel data_pasien
    query_pasien = "SELECT * FROM data_pasien;"
    df_pasien = pd.read_sql(query_pasien, engine)

    # inisialisasi list GeoJson
    features = []
    for _, row in df_pasien.iterrows():     # looping baris dataframe
        features.append({                   # membentuk GeoJson Feature
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]]
            },
            "properties": {
                "id": int(row["id_pasien"]),
                "nama": row["nama"],
                "umur": int(row["umur"]),
                "jenis_kelamin": row["jenis_kelamin"],
                "kunjungan": row["kunjungan"],
                "frek_nafas": int(row["frek_nafas"]),
                "tindak_lanjut": row["tindak_lanjut"],
                "anti_biotika": row["anti_biotika"],
                "faktor_risiko": row["faktor_risiko"],
                "desa": row["desa_kelurahan"],
                "kecamatan": row["kecamatan"],
                "puskesmas": row["puskesmas"],
                "cluster": int(row["cluster"]) if row["cluster"] is not None else -1
            }
        })
    return jsonify({"type": "FeatureCollection", "features": features})     # mengembalikan data ke format geojson agar dapat di tampilkan dalam peta

@app.route('/visualisasi')
def visualisasi_peta():
    print("membuka halaman visualisasi")
    return render_template('visualisasi.html')

@app.route('/visualisasi/pasien_user')
def vis_pasien_user():
    # ambil tabel data_pasien
    query_pasien = "SELECT * FROM data_pasien;"
    df_pasien = pd.read_sql(query_pasien, engine)

    features = []
    for _, row in df_pasien.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]]
            },
            "properties": {
                "id": int(row["id_pasien"]),
                "nama": row["nama"],
                "umur": int(row["umur"]),
                "jenis_kelamin": row["jenis_kelamin"],
                "kunjungan": row["kunjungan"],
                "frek_nafas": int(row["frek_nafas"]),
                "tindak_lanjut": row["tindak_lanjut"],
                "anti_biotika": row["anti_biotika"],
                "faktor_risiko": row["faktor_risiko"],
                "desa": row["desa_kelurahan"],
                "kecamatan": row["kecamatan"],
                "puskesmas": row["puskesmas"],
                "cluster": int(row["cluster"]) if row["cluster"] is not None else -1
            }
        })

    return jsonify({"type": "FeatureCollection", "features": features})

@app.route('/visualisasi_user')
def visualisasi_peta_user():
    return render_template('visualisasi_user.html')  # template khusus user

    
# mengambil isi kolom dari database (data dropdown)
@app.route('/ambil-isi-form')
def ambil_isi_data():
    query1 = "SELECT DISTINCT \"desa_kelurahan\", kecamatan, kunjungan, \"jenis_kelamin\", tindak_lanjut, anti_biotika, kondisi_saat_kunjungan_ulang, faktor_risiko, puskesmas, klasifikasi FROM data_pasien;"
    df_ambil = pd.read_sql(query1, engine)

    data_ambil = {
        'desa': sorted(df_ambil['desa_kelurahan'].dropna().unique().tolist()),
        'kecamatan': sorted(df_ambil['kecamatan'].dropna().unique().tolist()),
        'kunjungan': sorted(df_ambil['kunjungan'].dropna().unique().tolist()),
        'jenis_kelamin': sorted(df_ambil['jenis_kelamin'].dropna().unique().tolist()),
        'tindak_lanjut': sorted(df_ambil['tindak_lanjut'].dropna().unique().tolist()),
        'anti_biotika': sorted(df_ambil['anti_biotika'].dropna().unique().tolist()),
        'kondisi': sorted(df_ambil['kondisi_saat_kunjungan_ulang'].dropna().unique().tolist()),
        'faktor_risiko': sorted(df_ambil['faktor_risiko'].dropna().unique().tolist()),
        'puskesmas': sorted(df_ambil['puskesmas'].dropna().unique().tolist()),
        'klasifikasi': sorted(df_ambil['klasifikasi'].dropna().unique().tolist())
    }

    return jsonify(data_ambil)

@app.route('/tambah-data-pasien', methods=['POST'])
def tambah_data_pasien():
    dataTambah = request.get_json()

    print(" data masuk ")
    print(json.dumps(dataTambah, indent=2))

    if not dataTambah:
        return jsonify({"success": False, "message": "data kosong"}), 400
    
    nameDes = dataTambah.get('desa_kelurahan', '').strip().upper()

    with engine.begin() as conn:
        resId = conn.execute(text("SELECT MAX(id_pasien) FROM data_pasien"))
        maxId = resId.scalar() or 0
        newId = maxId + 1
    
        # auto set cluster menjadi (noise) & cari id_desa dari nama desa
        queryDes = text("SELECT id_desa FROM data_desa WHERE UPPER(nama_desa) = :desa LIMIT 1")
        resDes = conn.execute(queryDes, {"desa": nameDes})
        desId = resDes.scalar()

        if desId is None:
            return jsonify({"success": False, "message": f"Nama Desa '{nameDes}' tidak ditemukan di data_desa"}), 400

        # simpan ke database
        queryIns = text("""
            INSERT INTO data_pasien (
                id_pasien, tgl, nama, desa_kelurahan, kecamatan, kunjungan, jenis_kelamin, umur, frek_nafas, klasifikasi, tindak_lanjut, anti_biotika, kondisi_saat_kunjungan_ulang, keterangan, faktor_risiko, puskesmas, latitude, longitude, id_desa, cluster
            )VALUES (
                :id_pasien, :tgl, :nama, :desa, :kecamatan, :kunjungan, :jenis_kelamin, :umur, :frek_nafas, :klasifikasi, :tindak_lanjut, :anti_biotika, :kondisi, :keterangan, :faktor_risiko, :puskesmas, :latitude, :longitude, :id_desa, :cluster
            )
        """)

        conn.execute(queryIns, {
            'id_pasien': newId,
            'tgl': dataTambah['tgl'],
            'nama': dataTambah['nama'],
            'desa': dataTambah['desa_kelurahan'],
            'kecamatan': dataTambah['kecamatan'],
            'kunjungan': dataTambah['kunjungan'],
            'jenis_kelamin': dataTambah['jenis_kelamin'],
            'umur': dataTambah['umur'],
            'frek_nafas': dataTambah['frek_nafas'],
            'klasifikasi': dataTambah['klasifikasi'],
            'tindak_lanjut': dataTambah['tindak_lanjut'],
            'anti_biotika': dataTambah['anti_biotika'],
            'kondisi': dataTambah['kondisi_saat_kunjungan_ulang'],
            'keterangan': dataTambah.get('keterangan', ''),
            'faktor_risiko': dataTambah['faktor_risiko'],
            'puskesmas': dataTambah['puskesmas'],
            'latitude': dataTambah['latitude'],
            'longitude': dataTambah['longitude'],
            'id_desa': desId,
            'cluster': -1
        })

    return jsonify({'success': True, 'message': 'Data Pasien berhasil ditambahkan'})

@app.route('/cari-wilayah', methods=['POST'])
def cariWilayah():
    dataWil = request.get_json()
    lat, lng = float(dataWil['lat']), float(dataWil['lng'])
    poinWil = Point(lng, lat)

    # geojson desa
    with open('data/hasil_desa_bangkalan.geojson') as f:
        geoDesa = json.load(f)
    
    for fitur in geoDesa['features']:
        if shape(fitur['geometry']).contains(poinWil):
            namaDesa = fitur['properties']['namobj'].lower()

            # cek ke supabase
            with engine.connect() as conn:
                query = text(""" SELECT id_desa, kecamatan, puskesmas FROM data_desa WHERE LOWER(nama_desa) LIKE :nama_desa LIMIT 1 """)

                resultWil = conn.execute(query, {"nama_desa": f"%{namaDesa}%"}).fetchone()

                if resultWil:
                    return jsonify({
                        'nama_desa': namaDesa,
                        'kecamatan': resultWil.kecamatan,
                        'puskesmas' : resultWil.puskesmas,
                        'id_desa': resultWil.id_desa
                    })
                else:
                    return jsonify({
                        'nama_desa': namaDesa,
                        'kecamatan': '',
                        'puskesmas': '',
                        'id_desa': None,
                        'error' : 'wilayah tidak cocok dengan database'
                    })
        
    return jsonify({'error': 'Wilayah tidak ditemukan'}), 404

@app.route('/ambil-data-pasien/<int:id_pasien>')
def ambil_data_pasien(id_pasien):
    with engine.connect() as conn:
        query1 = text("SELECT * FROM data_pasien WHERE id_pasien = :id")
        hasil1 = conn.execute(query1, {"id": id_pasien}).fetchone()
        if hasil1:
            return jsonify({"success": True, "pasien": dict(hasil1._mapping)})
        return jsonify({"success": False, "message": "Data tidak ditemukan"}), 404

@app.route('/edit-data-pasien/<int:id_pasien>', methods=['POST'])
def edit_data_pasien(id_pasien):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Data kosong"}), 400
    
    try:
        with engine.begin() as conn:
            query = text(""" 
                UPDATE data_pasien SET
                    nama = :nama,
                    tgl = :tgl,
                    kunjungan = :kunjungan,
                    jenis_kelamin = :jenis_kelamin,
                    umur = :umur,
                    frek_nafas = :frek_nafas,
                    klasifikasi = :klasifikasi,
                    tindak_lanjut = :tindak_lanjut,
                    anti_biotika = :anti_biotika,
                    kondisi_saat_kunjungan_ulang = :kondisi,
                    faktor_risiko = :faktor_risiko,
                    keterangan = :keterangan,
                    desa_kelurahan = :desa_kelurahan,
                    kecamatan = :kecamatan,
                    puskesmas = :puskesmas
                WHERE id_pasien = :id
            """)

            conn.execute(query, {
                'nama': data.get('nama'),
                'tgl': data.get('tgl'),
                'kunjungan': data.get('kunjungan'),
                'jenis_kelamin': data.get('jenis_kelamin'),
                'umur': int(data.get('umur')),
                'frek_nafas': int(data.get('frek_nafas')),
                'klasifikasi': data.get('klasifikasi'),
                'tindak_lanjut': data.get('tindak_lanjut'),
                'anti_biotika': data.get('anti_biotika'),
                'kondisi': data.get('kondisi_saat_kunjungan_ulang'),
                'faktor_risiko': data.get('faktor_risiko'),
                'keterangan' : data.get('keterangan', '') or None,
                'desa_kelurahan' : data.get('desa_kelurahan'),
                'kecamatan' : data.get('kecamatan'),
                'puskesmas' : data.get('puskesmas'),
                'id': id_pasien
            })
        return jsonify({"success": True, 'message': 'Data berhasil diupdate'})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/update-koordinat/<int:id_pasien>', methods=['POST'])
def update_koordinat(id_pasien):
    data = request.get_json()
    print("Data Masuk : ", data)
    if not data:
        return jsonify({"success": False, "message": "Data Kosong"}), 400
    
    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
        desa_kelurahan = data.get("desa_kelurahan")
        kecamatan = data.get("kecamatan")
        puskesmas = data.get("puskesmas")
        
        if "id_desa" not in data or data["id_desa"] is None:
            raise ValueError("id_desa tidak ditemukan atau bernilai None")
        
        id_desa = int(data["id_desa"])

        print("Update data: ", latitude, longitude, desa_kelurahan, kecamatan, puskesmas, id_desa)
        
        with engine.begin() as conn:
            query = text("""
                UPDATE data_pasien SET latitude = :latitude, longitude = :longitude, desa_kelurahan = :desa_kelurahan, kecamatan = :kecamatan, puskesmas = :puskesmas, id_desa = :id_desa WHERE id_pasien = :id_pasien
            """)
            conn.execute(query, {
                "latitude": latitude,
                "longitude": longitude,
                "desa_kelurahan": desa_kelurahan,
                "kecamatan": kecamatan,
                "puskesmas": puskesmas,
                "id_desa": id_desa,
                "id_pasien": id_pasien
            })
        return jsonify({"success": True})
    except Exception as e:
        print("Gagal update koordinat", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/hapus-data-pasien/<int:id_pasien>', methods=['DELETE'])
def hapus_data_pasien(id_pasien):
    try:
        with engine.begin() as conn:
            query = text("DELETE FROM data_pasien WHERE id_pasien = :id")
            result = conn.execute(query, {"id": id_pasien})

            if result.rowcount == 0:
                return jsonify({"success": False, "message": "Data tidak ditemukan"}), 404
        
        return jsonify({"success": True, "message": "Data berhasil dihapus"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"message": "Semua field harus diisi"}), 400

    try:
        with engine.begin() as conn:
            # Query cek email jika sudah ada atau belum
            cek_query = text("SELECT * FROM data_user WHERE email = :email")
            result_cek = conn.execute(cek_query, {"email": email}).fetchone()
            
            if result_cek:
                return jsonify({"message": "Email sudah digunakan"}), 409 # status code data tidak lengkap
            
            # simpan data user baru
            insert_query = text("INSERT INTO data_user (username, email, password) VALUES (:username, :email, :password)")
            conn.execute(insert_query, {"username": username, "email": email, "password": password})

        return jsonify({"message": "Register berhasil"}), 200
    
    except Exception as e:
        return jsonify({"message": "Gagal Register", "error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email dan Password wajib diisi'}), 400
    
    try:
        with engine.begin() as conn:
            
            select_query  = text("SELECT username, password FROM data_user WHERE email = :email")
            result = conn.execute(select_query, {"email": email}).fetchone()
            
            if result:
                db_username = result[0]
                db_password = result[1]

                if db_password == password:
                    return jsonify({'status': 'success', 'message': 'Login Berhasil', 'username': db_username}), 200
                else:
                    return jsonify({'status': 'error', 'message': 'Password Salah'}), 401
            else:
                return jsonify({'status': 'error', 'message': 'Email tidak terdaftar'}), 404
            
    except Exception as e:
        return jsonify({"status": "error", "message": "Gagal Login", "error": str(e)}), 500

@app.route('/api/pendaftaran', methods=['POST'])
def pendaftaran_pasien():
    data = request.get_json()
    print("Data yang diterima dari flutter: ", data)
    
    try:
        nama = data.get('nama')
        nik = data.get('nik')
        umur = int(data.get('umur')) if data.get('umur') else None
        jenis_kelamin = data.get('jenis_kelamin')
        alamat = data.get('alamat')
        desa_kelurahan = data.get('desa_kelurahan')
        kecamatan = data.get('kecamatan')
        puskesmas = data.get('puskesmas')
        latitude = float(data.get('latitude')) if data.get('latitude') else None
        longitude = float(data.get('longitude')) if data.get('longitude') else None
        id_desa = int(data.get('id_desa')) if data.get('id_desa') else None

        # validasi 
        if not all([nama, nik, umur, jenis_kelamin, latitude, longitude, id_desa]):
            return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400
        
        # debugging 
        print("Data akan disimpan:", {
            "nama": nama,
            "nik": nik,
            "umur": umur,
            "latitude": latitude,
            "longitude": longitude,
            "id_desa": id_desa
        })
    
        with engine.begin() as conn:
            nik_query = conn.execute(
                text("SELECT 1 FROM data_pasien_sementara WHERE nik = :nik"), {"nik": nik}
            ).fetchone()
            if nik_query:
                return jsonify({
                    "status": "error",
                    "message": "NIK sudah digunakan. Silakan menuju Puskesmas terdekat."
                }), 409
            
            insert_query = text("""
                INSERT INTO data_pasien_sementara (nama, nik, umur, jenis_kelamin, alamat, desa_kelurahan, kecamatan, puskesmas, latitude, longitude, id_desa) VALUES (:nama, :nik, :umur, :jenis_kelamin, :alamat, :desa_kelurahan, :kecamatan, :puskesmas, :latitude, :longitude, :id_desa)
            """)
            conn.execute(insert_query, {
                "nama": nama,
                "nik": nik,
                "umur": umur,
                "jenis_kelamin": jenis_kelamin,
                "alamat": alamat,
                "desa_kelurahan": desa_kelurahan,
                "kecamatan": kecamatan,
                "puskesmas": puskesmas,
                "latitude": latitude,
                "longitude": longitude,
                "id_desa": id_desa
            })
        
        return jsonify({"status": "success", "message": "Pendaftaran Berhasil"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": "Gagal menyimpan data", "error": str(e)}), 500
    
@app.route('/api/get-lokasi', methods=['POST'])
def get_lokasi():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not latitude or not longitude:
        return jsonify({"status": "error", "message": "Koordinat tidak valid"}), 400
    
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
        headers = {'User-Agent': 'MyApp'}
        response = request.get(url, headers=headers)
        lokasi = response.json()

        address = lokasi.get("address", {})
        alamat = lokasi.get("display_name", "")
        desa_kelurahan = address.get("village") or address.get("suburb") or address.get("hamlet")
        kecamatan = address.get("county") or address.get("municipality")
        puskesmas = "Puskesmas Terdekat"

        return jsonify({
            "status": "success",
            "alamat": alamat,
            "desa_kelurahan": desa_kelurahan,
            "kecamatan": kecamatan,
            "puskesmas": puskesmas
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": "Gagal mendapatkan Lokasi", "error": str(e)}), 500

@app.route('/validasi-pasien')
def validasi_pasien():
    return render_template('validasi_pasien.html')

@app.route('/data-pasien-sementara')
def data_sementara():
    query = "SELECT * FROM data_pasien_sementara ORDER BY id DESC;"
    df = pd.read_sql(query, engine)
    return jsonify({"data": df.to_dict(orient="records")})


@app.route('/setuju-pasien/<int:id>', methods=['POST'])
def setuju_pasien(id):
    try:
        with engine.begin() as conn:
            # ambil data dari tabel sementara
            ambil_query = conn.execute(text("SELECT * FROM data_pasien_sementara WHERE id=:id"), {"id": id}).fetchone()

            if not ambil_query:
                return jsonify({"success": False, "message": "Data tidak ditemukan"})
            
            data = dict(ambil_query._mapping)

            # pindahkan data ke tabel pasien permanaen
            conn.execute(text("""
                INSERT INTO data_pasien_permanen (nama, nik, umur, jenis_kelamin, alamat, desa_kelurahan, kecamatan, puskesmas, latitude, longitude, id_desa, tgl) VALUES (:nama, :nik, :umur, :jenis_kelamin, :alamat, :desa_kelurahan, :kecamatan, :puskesmas, :latitude, :longitude, :id_desa, :tgl)
            """), data)

            # hapus data dari tabel pasien sementara
            conn.execute(text("DELETE FROM data_pasien_sementara WHERE id=:id"), {"id": id}),
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/hapus-sementara/<int:id>', methods=['DELETE'])
def hapus_sementara(id):
    try:
        with engine.begin() as conn:
            queryHapus = conn.execute(text("DELETE FROM data_pasien_sementara WHERE id=:id"), {"id": id})

            if queryHapus.rowcount == 0:
                return jsonify({"success": False, "message": "Data tidak ditemukan"})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/tabel-pasien-permanen')
def tabel_pasien_permanen():
    return render_template('data_permanen.html')

@app.route('/data-pasien-permanen')
def data_permanen():
    try:
        query = "SELECT * FROM data_pasien_permanen ORDER BY id_permanen DESC;"
        df = pd.read_sql(query, engine)

        # untuk ubah Nan menjadi None supaya jadi null di JSON
        df = df.replace({np.nan: None})

        # untuk konversi kolom datetime menjadi string
        for col in df.select_dtypes(include=['datetime', 'datetimetz']):
            df[col] = df[col].astype(str)
        
        # untuk memastikan semua numpy tipe ke python native
        df = df.astype(object)
        
        data = df.to_dict(orient="records")

        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"data": [], "error": str(e)})

@app.route('/ambil-data-permanen/<int:id>')
def ambil_data_permanen(id):
    try:
        query = text("SELECT * FROM data_pasien_permanen WHERE id_permanen = :id ORDER BY id_permanen DESC")
        with engine.begin() as conn:
            row = conn.execute(query, {"id": id}).mappings().first()

        if not row:
            return jsonify({"error": "Data tidak ditemukan"}), 404

        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit-pasien-permanen/<int:id>', methods=['POST'])
def edit_pasien_permanen(id):
    try:
        data = request.json
        update_query = text("""
            UPDATE data_pasien_permanen
            SET nama = :nama, nik = :nik, umur = :umur, jenis_kelamin = :jenis_kelamin,
                alamat = :alamat, desa_kelurahan = :desa_kelurahan, kecamatan = :kecamatan,
                puskesmas = :puskesmas, tgl = :tgl, kunjungan = :kunjungan, frek_nafas = :frek_nafas,
                klasifikasi = :klasifikasi, tindak_lanjut = :tindak_lanjut, anti_biotika = :anti_biotika,
                kondisi_saat_kunjungan_ulang = :kondisi_saat_kunjungan_ulang,
                faktor_risiko = :faktor_risiko, keterangan = :keterangan
            WHERE id_permanen = :id
        """)
        with engine.begin() as conn:
            conn.execute(update_query, {**data, "id": id})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@app.route('/hapus-permanen/<int:id>', methods=['DELETE'])
def hapus_permanen(id):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("DELETE FROM data_pasien_permanen WHERE id_permanen = :id"), {"id": id})
            if result.rowcount == 0:
                return jsonify({"success": False, "message": "Data tidak ditemukan"}), 404
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/update-koordinat-permanen/<int:id>', methods=['POST'])
def update_koordinat_permanen(id):
    try:
        data = request.get_json()
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        desa_kelurahan = data.get("desa_kelurahan")
        kecamatan = data.get("kecamatan")
        puskesmas = data.get("puskesmas")
        id_desa = data.get("id_desa")

        if latitude is None or longitude is None:
            return jsonify({"success": False, "message": "Koordinat tidak lengkap"}), 400

        query = text("""
            UPDATE data_pasien_permanen
            SET latitude = :latitude,
                longitude = :longitude,
                desa_kelurahan = :desa_kelurahan,
                kecamatan = :kecamatan,
                puskesmas = :puskesmas,
                id_desa = :id_desa
            WHERE id_permanen = :id
        """)

        with engine.begin() as conn:
            conn.execute(query, {
                "latitude": latitude,
                "longitude": longitude,
                "desa_kelurahan": desa_kelurahan,
                "kecamatan": kecamatan,
                "puskesmas": puskesmas,
                "id_desa": id_desa,
                "id": id
            })

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)