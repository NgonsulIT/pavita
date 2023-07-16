from flask import Flask, render_template, send_file, request, redirect, session, jsonify
import os
import glob
import cv2
import pickle

app = Flask(__name__)
app.secret_key = 'secret_key'
status = "Tidak Aktif"

# Data pengguna (misalnya di database)
users = {
    'Pavita_NMCU32UNOML': 'ESP32C_ccPav',
    'namri': '23Meilahirku'
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Username atau password salah')

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username, status=status)
    else:
        return redirect('/')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/images')
def get_images():
    image_folder = 'static/hasil_cam'
    image_files = glob.glob(os.path.join(image_folder, '*.jpg')) + glob.glob(os.path.join(image_folder, '*.png'))
    sorted_images = sorted(image_files, key=os.path.getmtime, reverse=False)

    return jsonify(images=sorted_images)

@app.route("/status")
def get_status():
    return status

@app.route("/update")
def update_status():
    global status
    status = request.args.get('status', '')
    return "Status diperbarui: " + status

@app.route('/getesp', methods=['GET'])
def GetEsp():
    image_folder = 'static/hasil_cam'
    image_files = glob.glob(os.path.join(image_folder, '*.jpg')) + glob.glob(os.path.join(image_folder, '*.png'))
    sorted_images = sorted(image_files, key=os.path.getmtime, reverse=True)
    hasil_prediksi = klasifikasi(sorted_images)
    
    return jsonify(result=hasil_prediksi)

def get_latest_image(folder_path):
    image_files = glob.glob(os.path.join(folder_path, '*.jpg'))
    image_files = sorted(image_files, key=os.path.getmtime, reverse=True)
    if image_files:
        latest_image = max(image_files, key=os.path.getctime)
        return latest_image
    return None

@app.route('/latest_image')
def latest_image():
    folder_path = 'static/hasil_cam'  # Ganti dengan path yang benar ke folder gambar
    latest_image = get_latest_image(folder_path)
    if latest_image:
        return jsonify({'image': latest_image})
    else:
        return jsonify({'image': None})

@app.route('/predict')
def predict():
    print("predict terpanggil")
    folder_path = 'static/hasil_cam'  # Ganti dengan path yang benar ke folder gambar
    latest_image = get_latest_image(folder_path)
    if latest_image:
        prediction_result = klasifikasi(latest_image)
        return jsonify({'result': prediction_result})
    else:
        return jsonify({'result': 'Tidak ada gambar yang tersedia'})

def delete_image(image_path):
    try:
        os.remove(image_path)
        return True
    except Exception as e:
        print(f"Error saat menghapus gambar: {str(e)}")
        return False

@app.route('/delete/<path:image_path>', methods=['POST'])
def delete(image_path):
    print("terpanggil")
    image_path = image_path.replace("$", "/")
    result = delete_image(image_path)
    if result:
        return jsonify({'status': 'sukses', 'message': 'Gambar berhasil dihapus'})
    else:
        return jsonify({'status': 'gagal', 'message': 'Gagal menghapus gambar'})

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    if file:
        filename = file.filename
        filepath = os.path.join('static', 'hasil_cam', filename)
        file.save(filepath)
        return 'File uploaded successfully.'

with open('./model/model_m_knn.pkl', 'rb') as file:
    model = pickle.load(file)
with open('./model/standarscaller.pkl', 'rb') as scl:
    scaller = pickle.load(scl)
with open('./model/pca.pkl', 'rb') as sclpca:
    pca = pickle.load(sclpca)

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    resized_image = cv2.resize(image, (32, 32))
    preprocessed_image = resized_image.flatten()  # Menjadi vektor 1D
    return preprocessed_image

def klasifikasi(image_path):
    preprocessed_image = preprocess_image(image_path)
    images_scaled = scaller.transform([preprocessed_image])
    images_pca = pca.transform(images_scaled)

    prediction = model.predict(images_pca)

    # Mendapatkan label kelas dari prediksi
    class_labels = {0: 'Baik', 1: 'Busuk'}
    predicted_class = class_labels[prediction[0]]

    # Menampilkan hasil prediksi
    print('Hasil prediksi:', predicted_class)
    return predicted_class

if __name__ == '__main__':
    app.run()
