# Definisikan lokasi file Excel
# path_to_file = '/Users/nurhamim/Documents/apriori-project/dataset-skripsi.xls'  # Ganti dengan lokasi sebenarnya dari file Excel Anda

# Import library yang diperlukan
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# Definisikan lokasi file Excel
path_to_file = '/Users/nurhamim/Documents/apriori-project/dataset-skripsi.xls'  # Ganti dengan lokasi sebenarnya dari file Excel Anda

# Membaca data dari file Excel menggunakan xlrd
try:
    data = pd.read_excel(path_to_file, engine='xlrd')
    print("Data loaded successfully!")
    print("Kolom yang tersedia di dataset:", data.columns.tolist())
except Exception as e:
    print("Error loading the Excel file:", e)
    exit()

# Cetak beberapa baris pertama untuk memahami struktur data
print("Preview dari data yang dimuat:")
print(data.head())

# Menyesuaikan nama kolom agar sesuai dengan data yang ada
data.columns = ['TransactionID', 'Items']

# Cleaning data - contoh menghapus baris di mana seluruh data hilang
data.dropna(how='all', inplace=True)

# Membuat data training
try:
    transactions = data['Items'].apply(lambda x: x.split(',')).tolist()
except KeyError:
    print("Kesalahan dalam pengelompokan data. Periksa nama kolom untuk 'TransactionID' dan 'Items'.")
    exit()

# Encoding transaksi untuk Apriori
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)

# Menggunakan Apriori untuk menemukan itemset yang sering dengan minimal support
frequent_itemsets = apriori(df, min_support=0.05, use_colnames=True)

# Menghitung aturan asosiasi dengan minimal confidence
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)

# Menampilkan hasil perhitungan
print("Hasil dari analisis Apriori:")
print(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
