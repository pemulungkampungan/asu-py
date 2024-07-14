from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No file selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File successfully uploaded')
        return redirect(url_for('process_apriori', filename=filename))
    else:
        flash('Allowed file types are xls, xlsx')
        return redirect(request.url)

@app.route('/process/<filename>', methods=['GET', 'POST'])
def process_apriori(filename):
    if request.method == 'POST':
        try:
            min_support = float(request.form.get('min_support', 0.1))
            min_confidence = float(request.form.get('min_confidence', 0.5))
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')

            print(f"min_support: {min_support}, min_confidence: {min_confidence}")

            # Baca dataset
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            data = pd.read_excel(file_path, engine='xlrd')

            # Menyesuaikan nama kolom agar sesuai dengan data yang ada
            data.columns = ['TransactionID', 'Items']

            # Filtering berdasarkan range tanggal
            data['TransactionID'] = pd.to_datetime(data['TransactionID'])
            data = data[(data['TransactionID'] >= start_date) & (data['TransactionID'] <= end_date)]
            print("Filtered data:\n", data)

            # Membuat data training
            transactions = data['Items'].apply(lambda x: x.split(', ')).tolist()
            print("Transactions:\n", transactions)

            # Cek frekuensi item
            all_items = [item for sublist in transactions for item in sublist]
            item_counts = pd.Series(all_items).value_counts()
            print("Item frequencies:\n", item_counts)

            # Encoding transaksi untuk Apriori
            te = TransactionEncoder()
            te_ary = te.fit(transactions).transform(transactions)
            df = pd.DataFrame(te_ary, columns=te.columns_)
            print("Encoded transactions:\n", df)

            # Menggunakan Apriori untuk menemukan itemset yang sering dengan minimal support
            frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
            print("Frequent itemsets:\n", frequent_itemsets)

            # Menghitung aturan asosiasi dengan minimal confidence
            if not frequent_itemsets.empty:
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
                print("Rules:\n", rules)

                # Memformat hasil
                if not rules.empty:
                    formatted_rules = []
                    for index, row in rules.iterrows():
                        antecedents = ', '.join(list(row['antecedents']))
                        consequents = ', '.join(list(row['consequents']))
                        support = round(row['support'] * 100, 2)
                        confidence = round(row['confidence'] * 100, 2)
                        lift = round(row['lift'], 2)
                        correlation = 'korelasi positif' if lift > 1 else 'korelasi negatif'
                        formatted_rules.append([antecedents, consequents, support, confidence, lift, correlation])

                    rules_df = pd.DataFrame(formatted_rules, columns=['X', 'Y', 'Support X U Y', 'Confidence', 'Nilai Uji lift', 'Korelasi rule'])
                    print("Formatted rules:\n", rules_df)
                else:
                    print("No rules generated.")
                    rules_df = pd.DataFrame(columns=['X', 'Y', 'Support X U Y', 'Confidence', 'Nilai Uji lift', 'Korelasi rule'])

                # Tambahkan analisis hasil
                analysis_results = []
                for index, row in rules_df.iterrows():
                    analysis_results.append(f"Jika konsumen membeli {row['X']}, maka konsumen juga akan membeli {row['Y']}")

                return render_template('results.html', tables=[rules_df.to_html(classes='data')], analysis_results=analysis_results, titles=rules_df.columns.values)
            else:
                print("No frequent itemsets found.")
                return render_template('results.html', tables=[], analysis_results=[], titles=[])
        except Exception as e:
            print(f"Error: {e}")
            return render_template('results.html', tables=[], analysis_results=[], titles=[])
    
    return render_template('process.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
