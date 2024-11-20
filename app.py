from flask import Flask, request, render_template, redirect, url_for
import os
import csv
import subprocess

# Initialize Flask app
app = Flask(__name__)

# Set up the folder to store uploaded files
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Function to check if file is a valid CSV
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to execute the Apriori algorithm
def run_apriori_algorithm(input_file, min_support):
    # Run the apriori_2887786.py script as a subprocess
    result = subprocess.run(
        ['python', 'apriori_2887786.py', '-i', input_file, '-m', str(min_support)],
        capture_output=True,
        text=True
    )
    return result.stdout

# Route to render the file upload form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the file upload and Apriori processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    # If no file is selected, redirect back to the upload form
    if file.filename == '':
        return redirect(request.url)
    
    # Check if the uploaded file is a CSV
    if file and allowed_file(file.filename):
        # Save the uploaded file to the 'uploads' folder
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Get the minimum support value from the form
        min_support = int(request.form['min_support'])
        
        # Run the Apriori algorithm and get the result
        output = run_apriori_algorithm(filename, min_support)
        
        # Render the result page with output
        return render_template('results.html', output=output, filename=file.filename, min_support=min_support)
    else:
        return "Invalid file format. Please upload a CSV file."

# Route to display results page (this is used after processing the file)
@app.route('/results')
def results():
    return render_template('results.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
