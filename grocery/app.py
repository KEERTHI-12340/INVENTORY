from flask import Flask, request, redirect, render_template, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def process_csv(file_path):
    df = pd.read_csv(file_path)
    

    required_columns = ['Product', 'QuantitySold', 'SellingPrice', 'CostPrice']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    df['Profit'] = df['SellingPrice'] - df['CostPrice']
    df['ProfitMargin'] = df['Profit'] / df['SellingPrice']
    highest_selling_product = df.loc[df['QuantitySold'].idxmax()]
    highest_profit_margin_product = df.loc[df['ProfitMargin'].idxmax()]
    return highest_selling_product, highest_profit_margin_product

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        try:
            highest_selling, highest_profit_margin = process_csv(file_path)
            result = {
                'highest_selling': {
                    'Product': highest_selling['Product'],
                    'QuantitySold': highest_selling['QuantitySold']
                },
                'highest_profit_margin': {
                    'Product': highest_profit_margin['Product'],
                    'ProfitMargin': f"{highest_profit_margin['ProfitMargin'] * 100:.2f}%"
                }
            }
            return render_template('result.html', result=result)
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
