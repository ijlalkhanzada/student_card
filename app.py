from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import io
import os
from werkzeug.utils import secure_filename
import random
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

background_image_path = 'static\images\card_background.jpeg'  # The new background image path
background = Image.open(background_image_path)
background = background.resize((800, 600))
background = np.array(background)

def generate_card(student_details):
    fig, ax = plt.subplots(figsize=(9, 6))

    # Border styling: Top & bottom green, left & right black
    top_bottom_border = patches.Rectangle((0, 0.98), 1, 0.02, transform=ax.transAxes, color='green', linewidth=0)
    bottom_border = patches.Rectangle((0, 0), 1, 0.02, transform=ax.transAxes, color='green', linewidth=0)
    left_border = patches.Rectangle((0, 0), 0.01, 1, transform=ax.transAxes, color='black', linewidth=0)
    right_border = patches.Rectangle((0.99, 0), 0.01, 1, transform=ax.transAxes, color='black', linewidth=0)

    ax.add_patch(top_bottom_border)
    ax.add_patch(bottom_border)
    ax.add_patch(left_border)
    ax.add_patch(right_border)

    # Background image
    ax.imshow(background, extent=[0, 1, 0, 1], aspect='auto', alpha=0.15)


    # Text and styling
    ax.text(0.05, 0.85, "ID CARD", ha='left', va='top', fontsize=20, color='teal', weight='bold', transform=ax.transAxes)

    # Student details
    text_y = 0.75
    for key, value in student_details.items():
        if key == "Photo":
            continue
        ax.text(0.05, text_y, f"{key}: ", ha='left', va='top', fontsize=14, color='teal', weight='bold', 
                transform=ax.transAxes)
        ax.text(0.35, text_y, value, ha='left', va='top', fontsize=14, color='black', transform=ax.transAxes)
        text_y -= 0.07

    # Student photo
    img = Image.open(student_details['Photo'])
    img = img.resize((120, 150))
    img = np.array(img)

    # Positioning the image to the right
    ax_img = fig.add_axes([0.70, 0.55, 0.2, 0.3])
    ax_img.imshow(img)
    ax_img.axis('off')
    border = patches.Rectangle((0, 0), 1, 1, transform=ax_img.transAxes, fill=False, color='teal', linewidth=2)
    ax_img.add_patch(border)

    # Footer with colors (Q1 and WMD)
    footer_color_1 = patches.Rectangle((0, 0), 0.2, 0.05, transform=ax.transAxes, color='red')
    footer_color_2 = patches.Rectangle((0.2, 0), 0.2, 0.05, transform=ax.transAxes, color='#78c13b')
    ax.add_patch(footer_color_1)
    ax.add_patch(footer_color_2)
    ax.text(0.1, 0.02, "Q1", ha='center', va='center', fontsize=12, color='white', transform=ax.transAxes)
    ax.text(0.3, 0.02, "WMD", ha='center', va='center', fontsize=12, color='white', transform=ax.transAxes)

    # Signature text
    ax.text(0.75, 0.05, "Authorized Signature", ha='center', va='center', fontsize=14, color='teal', weight='bold',
            transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Save the generated card to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_roll_no():
    return f"RL-{random.randint(1000, 9999)}"

def generate_batch():
    current_year = datetime.datetime.now().year
    return f"Batch-{current_year}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        student_photo = request.files.get('photo')
        if student_photo and student_photo.filename:
            # Securely handle file upload
            filename = secure_filename(student_photo.filename)
            
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            student_photo.save(photo_path)

            student_details = {
                "Name": request.form['name'],
                "Roll No": request.form['roll_no'],
                "Distance Learning": request.form['distance_learning'],
                "City": request.form['city'],
                "Center": request.form['center'],
                "Campus": request.form['campus'],
                "Days / Time": request.form['days_time'],
                "Batch": request.form['batch'],
                "Photo": photo_path  # Use the uploaded photo
            }
            card_image = generate_card(student_details)
            flash("Card generated successfully!", "success")
         
            # Dynamic download name using the student's name
            download_name = f"{student_details['Name']}_Piaic.png"
            return send_file(card_image, mimetype='image/png', as_attachment=True, download_name=download_name)
            
        flash("Please upload a valid photo.", "danger")
        return redirect(url_for('index'))

    return render_template('index.html', roll_no=generate_roll_no(), batch=generate_batch())

if __name__ == '__main__':
    app.run(debug=True)
    