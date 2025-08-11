#%%
import psycopg2
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import geopandas as gpd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from geopy.distance import great_circle
from shapely.geometry import Point
from scipy.spatial.distance import pdist, squareform
from kneed import KneeLocator
from sqlalchemy import create_engine

# connect ke database
#%%
engine = create_engine("postgresql+psycopg2://postgres.qsbtjgxxrinqelrgjotk:Gudangair0407@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres")

#%%
# Query untuk mengambil data pasien
query_pasien = "SELECT * FROM data_pasien;"
df_pasien = pd.read_sql(query_pasien, engine)

# melihat tabel pasien
print(df_pasien.head(100))

#%%
# membentuk variabel baru data pasien menghilangkan kolom no.reg dan keterangan meninggal
df_pasien_lama = df_pasien.drop(columns=['no.reg','ket_(meninggal)'])
print(df_pasien_lama.head(10))

#%%
# membentuk variabel baru dari variabel sebelumnya dan mengambil kolom yang dibutuhkan
df_pasien_baru = df_pasien.drop(columns=['no','tgl','nama','no.reg','desa/kelurahan','kecamatan','klasifikasi','kondisi_saat_kunjungan_ulang','ket_(meninggal)','puskesmas','latitude','longitude','id'])
print(df_pasien_baru.head(10))

#%%
# preprocessing Encoding & MinMaxNormalization
df_ohe = pd.get_dummies(df_pasien_baru, columns=['kunjungan','jenis_kelamin','tindak_lanjut','anti_biotika','faktor_risiko'], dtype=int)

scaler = MinMaxScaler()
df_preproccesing = scaler.fit_transform(df_ohe)
df_preproccesing = pd.DataFrame(df_preproccesing, columns=df_ohe.columns)
print(df_preproccesing.head(10))

#%%
# langkah matriks jarak (euclidean distance)
df_matriks_jarak = pdist(df_preproccesing, metric='euclidean')
print("Matriks Jarak Persegi:\n", squareform(df_matriks_jarak))

#%%
# mencari nilai epsilon
MinPts = 3
neighbors = NearestNeighbors(n_neighbors=MinPts)
neighbors.fit(df_preproccesing)
distances, indices = neighbors.kneighbors(df_preproccesing)

k_distances = distances[:, MinPts - 1]
k_distances = np.sort(k_distances)

kneeds = KneeLocator(range(len(k_distances)), k_distances, curve='convex', direction='increasing')
epsilon_eps = k_distances[kneeds.knee]

plt.figure(figsize=(10, 6))
plt.plot(k_distances)
plt.axhline(y=epsilon_eps, color='red', linestyle='--', label=f'Epsilon (knee point): {epsilon_eps:.2f}')
plt.xlabel('Data Points')
plt.ylabel(f'{MinPts}')
plt.title('Elbow Method')
plt.legend()
plt.grid(True)
plt.show()

print(f'Epsilon (knee point): {epsilon_eps:.2f}')

#%%
# Dbscan
eps = 1.41
minPts = 3

dbscan = DBSCAN(eps=eps, min_samples=minPts, metric="euclidean")
cluster_labels = dbscan.fit_predict(df_preproccesing)

n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
n_noise = list(cluster_labels).count(-1)

print(f"Jumlah Cluster: {n_clusters}")
print(f"Jumlah Noise (Outliers): {n_noise}")

#%%
# melihat hasil jumlah anggota per cluster
jumlah_per_cluster = df_cluster['cluster'].value_counts().sort_index()

print("Jumlah data per cluster:")
print(jumlah_per_cluster)

#%%
# menghitung Silhouette Coefficient
if n_clusters > 1:
  filter = cluster_labels != -1
  filtered_data = df_preproccesing[filter]
  silhouette_scored = silhouette_score(squareform(pdist(filtered_data)), cluster_labels[filter], metric='precomputed')
  print(f"Nilai Silhouette Coefficient: {silhouette_scored:.4f}")
else:
  print("Tidak dapat menghitung nilai Silhouette Coefficient karena mendapatkan 1 cluster.")

#%%
# memasukkan kolom cluster ke dataset
df_cluster = df_pasien_lama.copy()
df_cluster['cluster'] = cluster_labels
df_cluster = pd.DataFrame(df_cluster)
print(df_cluster.head(100))

#%%
# mengecek latitude dan longitude
print(df_cluster[['latitude','longitude']].head())
print(df_cluster.dtypes)

#%%
# mengubah kolom latitude dan longitude menjadi string
df_cluster['latitude'] = df_cluster['latitude'].astype(str)
df_cluster['longitude'] = df_cluster['longitude'].astype(str)

# menghilangkan koma pada kolom latitude dan longitude
df_cluster['latitude'] = df_cluster['latitude'].str.replace(',', '', regex=False)
df_cluster['longitude'] = df_cluster['longitude'].str.replace(',', '', regex=False)

# Latitude: potong satu digit di awal (negatif), lalu titik setelah digit ke-1
df_cluster['latitude'] = df_cluster['latitude'].apply(
    lambda x: '-' + x[1:2] + '.' + x[2:] if x.startswith('-') else x[0] + '.' + x[1:]
)

# Longitude: titik setelah digit ke-3
df_cluster['longitude'] = df_cluster['longitude'].apply(
    lambda x: x[:3] + '.' + x[3:]
)

# mengubah kembali kolom latitude dan longitude menjadi float
df_cluster['latitude'] = df_cluster['latitude'].astype(float)
df_cluster['longitude'] = df_cluster['longitude'].astype(float)

# %%
# mendapatkan isi baru kolom latitude dan longitude
print(df_cluster[['latitude','longitude']].head(10))
print(df_cluster.dtypes)

#%%
# simpan hasil tabel clustering
df_cluster.to_csv("data/hasil_data_cluster.csv", index=False)

# %%
# mengambil data geoJson

gdf_desa = gpd.read_file("data/hasil_desa_bangkalan.geojson")
gdf_kec = gpd.read_file("data/kecamatan_bangkalan.geojson")

# %%
# membuat variable baru mengubah nama kolom desa
gdf_desa1 = gdf_desa.rename(columns={'namobj': 'desa/kelurahan'})
print(gdf_desa1.head(10))

#%%
# membuat variable baru mengubah nama kolom kecamatan
gdf_kec1 = gdf_kec.rename(columns={'nama_kecamatan': 'kecamatan'})
print(gdf_kec1.head(10))

# %%
# menghitung jumlah anggota setiap cluster per desa
df_cluster['desa/kelurahan'] = df_cluster['desa/kelurahan'].str.lower().str.upper()

dominasi_desa = (
    df_cluster.groupby(['desa/kelurahan','cluster'])
    .size()
    .reset_index(name='jumlah')
)

dominasi_desa = (
    dominasi_desa.sort_values('jumlah', ascending=False)
    .drop_duplicates('desa/kelurahan')
)

dominasi_desa.rename(columns={
    'desa/kelurahan': 'nama_desa',
    'cluster': 'cluster_desa'
}, inplace=True)

# mengubah nama kolom desa
gdf_desa1['nama_desa'] = gdf_desa1['desa/kelurahan'].str.lower().str.upper()
gdf_desa1 = gdf_desa1.merge(dominasi_desa, on='nama_desa', how='left')

# %%
# menghitung jumlah anggota setiap cluster per kecamatan
df_cluster['kecamatan'] = df_cluster['kecamatan'].str.lower().str.upper()

dominasi_kec = (
    df_cluster.groupby(['kecamatan','cluster'])
    .size()
    .reset_index(name='jumlah')
)

dominasi_kec = (
    dominasi_kec.sort_values('jumlah', ascending=False)
    .drop_duplicates('kecamatan')
)

dominasi_kec.rename(columns={
    'kecamatan': 'nama_kecamatan',
    'cluster': 'cluster_kec'
}, inplace=True)

gdf_kec1['nama_kecamatan'] = gdf_kec1['kecamatan'].str.lower().str.upper()
gdf_kec1 = gdf_kec1.merge(dominasi_kec, on='nama_kecamatan', how='left')

# %%
# menentukan warna unik
clusters = sorted(df_cluster['cluster'].unique())
cmap = plt.cm.get_cmap('tab20', len(clusters))

warna_clusters = {
    c: '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
    for c, (r, g, b, _) in zip(clusters, cmap(np.arange(len(clusters))))
}
warna_clusters[-1] = 'black'

#%%
maps = folium.Map(location=[-6.9973271, 112.9253102], zoom_start=12)

# layer 1 (setiap pasien)
layer_pasien = folium.FeatureGroup(name='Titik Setiap Pasien')
for idx, row in df_cluster.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=warna_clusters.get(row['cluster'], 'gray'),
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(f"cluster: {row['cluster']}<br>Desa: {row['desa/kelurahan']}<br>Kecamatan: {row['kecamatan']}", max_width=250)
    ).add_to(layer_pasien)
layer_pasien.add_to(maps)

# layer 2 (desa/kelurahan)
layer_desa = folium.FeatureGroup(name='Desa/Kelurahan (Cluster Dominan)')
folium.GeoJson(
    gdf_desa1,
    style_function=lambda d: {
        'fillColor': warna_clusters.get(d['properties']['cluster_desa'], 'lightgray'),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.5
    },
    tooltip=folium.features.GeoJsonTooltip(fields=['desa/kelurahan', 'cluster_desa'], aliases=['Desa/Kelurahan', 'Cluster Dominan'])
).add_to(layer_desa)
layer_desa.add_to(maps)

#layer 3 (Kecamatan)
layer_kec = folium.FeatureGroup(name='Kecamatan (Cluster Dominan)')
folium.GeoJson(
    gdf_kec1,
    style_function=lambda d: {
        'fillColor': warna_clusters.get(d['properties']['cluster_kec'], 'lightgray'),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.5
    },
    tooltip=folium.features.GeoJsonTooltip(fields=['kecamatan', 'cluster_kec'], aliases=['Kecamatan', 'Cluster Dominan'])
).add_to(layer_kec)
layer_kec.add_to(maps)

folium.LayerControl().add_to(maps)

maps.save("hasil_peta.html")
print("Peta berhasil disimpan. Silakan buka 'hasil_peta.html' di browser.")

# %%
