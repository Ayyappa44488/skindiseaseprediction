from flask import Flask,render_template,redirect,url_for,request,session,jsonify
import mysql.connector,os
import numpy as np
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
import base64
import datetime
from googletrans import Translator
from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import numpy as np
import bcrypt
import time
import random
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'Your_key'
conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
cursor = conn.cursor(dictionary=True) 
saved_path=''
data=pd.read_csv(r"Book1.csv")
# Define email sender and receiver
email_sender = 'your_mail'
email_password = 'your_password'
def process_and_predict(image_path):
    # model = tf.keras.models.load_model(r"6claass (1).h5")
    # img = cv2.imread(image_path)
    # if img is None:return None
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # img = cv2.resize(img, (180, 180))
    # img = np.expand_dims(img, axis=0)
    # img=np.array(img)
    # features_test=vgg_model.predict(img)
    # num_test=img.shape[0]
    # x_test=features_test.reshape(num_test,-1)
    # pred = model.predict(x_test)[0]
    # predicted_class = np.argmax(pred)
    # return cat[predicted_class]
    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)
    model = load_model("keras_Model.h5", compile=False)
    class_names = open("labels.txt", "r").readlines()
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open(image_path).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    return class_name[2:]
def save_uploaded_image(uploaded_file):
    # Define the directory where you want to save the uploaded image
    save_dir = 'uploads'
    os.makedirs(save_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Save the uploaded file to the directory
    save_path = os.path.join(save_dir, uploaded_file.filename)
    with open(save_path, 'wb') as f:
        f.write(uploaded_file.read())
    return save_path
def translate_to(text,language):
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest=language).text
    return translated_text
def send_otp():
    # Generate a random 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    # Get the current timestamp
    timestamp = int(time.time())  # Current Unix timestamp
    return otp, timestamp
@app.route('/')
def hello_world():
    return render_template('home.html')
@app.route('/login')
def login():
    return render_template('newlogin.html')
@app.route('/start')
def start():
    if 'logged_in' in session and session['logged_in']==True:
        return render_template('camerapg (1).html')
    else:
        return render_template('newlogin.html',message="Please Login to continue")
@app.route('/forgot')
def forgot():
    return render_template('forgot.html')
@app.route('/otp',methods=['POST','GET'])
def otp():
    session['email']=request.form['user_email']
    session['otp'],session['time_stamp']=send_otp()
    session['otp']=str(session['otp'])
    mail=session['email']
    subject="OTP for EpidermX"
    body="""<html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>OTP</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-image: #f5f1f1; margin: 0; padding: 0;">
        <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f0f0;">
            <tr>
                <td align="center" style="padding: 20px;">
                    <table cellpadding="0" cellspacing="0" width="600"  style=" background-color:#2f7e7fa4;border-radius: 10px; box-shadow: 0 2px 4px rgba(249, 249, 249, 0.938);">
                        <tr >
                            <td colspan="2" style="background-color: #090909; text-align: center; padding: 20px; border-top-left-radius: 10px; border-top-right-radius: 10px;">
                                <h1 style="color: #f9f7f7; margin: 0;">OTP for EpidermX</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px;">
                                <p style="font-size: 16px; color: #faf9f9; font-weight: bold;font-size: large;text-align: center;margin-top: 10px;">Your OTP is """+session['otp']+"""</p>
                            </td>
                        </tr>
                        <tr>
                        <td style="padding: 20px;">
                            <p style="font-size: 16px; color: tomato; font-weight: bold;font-size: large;text-align: center;margin-top: 10px;">OTP will expire in 5 minutes</p>
                        </td>
                        </tr>
                        <tr>
                            <td colspan="2" style="background-color: #0b0b0b; text-align: center; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                                <p style="color: #f8f5f5; margin: 0;font-weight:Bold;">THANK YOU</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>"""
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = mail
    em['Subject'] = subject
    em.set_content(body,subtype="html")
    context = ssl.create_default_context()
    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender,mail, em.as_string())
    return render_template('otp.html')
@app.route('/verify_otp',methods=['POST','GET'])
def verify_otp():
    otp1=request.form['otp1']
    otp2=request.form['otp2']
    otp3=request.form['otp3']
    otp4=request.form['otp4']
    otp5=request.form['otp5']
    otp6=request.form['otp6']
    otp=otp1+otp2+otp3+otp4+otp5+otp6
    if otp==session['otp'] and int(time.time()) - session['time_stamp'] < 300:
        session['otp']=''
        return render_template('resetpassword.html')
    else:
        return render_template('otp.html',message="Invalid OTP")
@app.route('/resend_otp')
def resend_otp():
    session['otp'],session['time_stamp']=send_otp()
    session['otp']=str(session['otp'])
    mail=session['email']
    subject="OTP for EpidermX"
    body="""<html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>OTP</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-image: #f5f1f1; margin: 0; padding: 0;">
        <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f0f0;">
            <tr>
                <td align="center" style="padding: 20px;">
                    <table cellpadding="0" cellspacing="0" width="600"  style=" background-color:#2f7e7fa4;border-radius: 10px; box-shadow: 0 2px 4px rgba(249, 249, 249, 0.938);">
                        <tr >
                            <td colspan="2" style="background-color: #090909; text-align: center; padding: 20px; border-top-left-radius: 10px; border-top-right-radius: 10px;">
                                <h1 style="color: #f9f7f7; margin: 0;">OTP for EpidermX</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px;">
                                <p style="font-size: 16px; color: #faf9f9; font-weight: bold;font-size: large;text-align: center;margin-top: 10px;">Your OTP is """+session['otp']+"""</p>
                            </td>
                        </tr>
                        <tr>
                        <td style="padding: 20px;">
                            <p style="font-size: 10px; color: tomato; font-weight: bold;font-size: large;text-align: center;margin-top: 10px;">OTP will expire in 5 minutes</p>
                        </td>
                        </tr>
                        <tr>
                            <td colspan="2" style="background-color: #0b0b0b; text-align: center; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                                <p style="color: #f8f5f5; margin: 0;font-weight:Bold;">THANK YOU</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>"""
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = mail
    em['Subject'] = subject
    em.set_content(body,subtype="html")
    context = ssl.create_default_context()
    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender,mail, em.as_string())
    return render_template('otp.html')
@app.route('/resetpassword',methods=['POST','GET'])
def resetpassword():
    pass1=request.form['pass1']
    pass2=request.form['pass2']
    if pass1==pass2:
        pass1=bcrypt.hashpw(pass1.encode('utf-8'), bcrypt.gensalt())
        sql="UPDATE register SET password=%s WHERE email=%s"
        cursor.execute(sql,(pass1,session['email']))
        conn.commit()
        return redirect(url_for('login'))
    else:
        return render_template('resetpassword.html',message="Password and Confirm Password should be same")  
@app.route('/signup',methods=['POST','GET'] )
def signup():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    name=request.form['name']
    email=request.form['email']
    pass1=request.form['pass1']
    pass2=request.form['conpass']
    age=request.form['age']
    age=int(age)
    if pass1==pass2: 
        print(name,email,pass1,pass2,age)
        if age<18:
            return render_template('newlogin.html',message="Age should be greater than 18")
        sql="SELECT * FROM register WHERE email = %s"
        cursor.execute(sql,(email,))
        result=cursor.fetchall()
        if len(result)>0:
            return render_template('newlogin.html',message="Email already exists/please signin")
        sql = "INSERT INTO register VALUES (%s, %s,%s,%s)"
        pass1=bcrypt.hashpw(pass1.encode('utf-8'), bcrypt.gensalt())
        val = (email,pass1,name,age)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        conn.close()
        session['logged_in']=True
        session['email']=email
        session['name']=name
        cursor.close()
        conn.close()
        return redirect(url_for('loggedin'))
    else:
        cursor.close()
        conn.close()
        return redirect(url_for('conpass'))
@app.route('/conpass')
def conpass():
    return render_template('newlogin.html',message="Password and Confirm Password should be same")
# @app.route('/hello')
# def hello():
#     return render_template('login1.html')
@app.route('/signin',methods=['POST','GET'])
def signin():
    email=request.form['email']
    pass1=request.form['pass1']
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor() 
    # Define a SQL query to check if a row exists (example query)
    sql = "SELECT * FROM register WHERE email = %s"
    # Provide a value for the condition (replace %s with the actual value)
    sql1="SELECT * FROM doctors WHERE email = %s"
    condition_value = (email,)
    # Execute the SQL query with the provided condition
    cursor.execute(sql, condition_value)
    # Fetch the result (in this case, a single integer representing the count)
    result = cursor.fetchall()
    cursor.execute(sql1, condition_value)
    result1=cursor.fetchall()
    if len(result1)==1 and bcrypt.checkpw(pass1.encode('utf-8'), result1[0][1].encode('utf-8')):
        session['logged_in']=True
        session['doctor']=True
        session['email']=email
        session['name']=result1[0][3]
        cursor.close()
        conn.close()
        return redirect(url_for('loggedin'))
    elif len(result) == 1 and bcrypt.checkpw(pass1.encode('utf-8'), result[0][1].encode('utf-8')):
        session['logged_in']=True
        session['email']=email
        session['name']=result[0][2]
        cursor.close()
        conn.close()
        return redirect(url_for('loggedin'))
    else:
        session['logged_in']=False
        cursor.close()
        conn.close()
        return redirect(url_for('not_success'))
# @app.route('/success')
# def success():
#     return render_template('index.html',user="/static/logo2.png",logged_in=True)    
@app.route('/not_success')
def not_success():
    return render_template('newlogin.html',message="Invalid Email/Password") 
@app.route('/upload',methods=['POST','GET']) 
def upload():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    global saved_path,uploaded_file
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        saved_path = save_uploaded_image(uploaded_file)
        res = process_and_predict(saved_path)
        res=res.strip()
        print(res)
        result=data[data["Disease"]==res]
        description=result["Description"].values[0]
        remedies=result["Basic Remedies"].values[0]
        session['res']=res.upper()
        session['description']=description
        session['remedies']=remedies
        path = os.path.normpath(saved_path) 
        email=session['email']
        disease=session['res']
        filepath=path
        with open(filepath,"rb") as File:
            image=File.read()
        insert_query = "INSERT INTO results (email, photo, disease) VALUES (%s, %s, %s)"
        data1 = (email, image, disease)
        cursor.execute(insert_query, data1)
        conn.commit()
        cursor.close()
        conn.close()
        last_inserted_id = cursor.lastrowid
        session['unique_id']=last_inserted_id
        # Email subject and content
        subject = 'Mail from EpidermX'
        body = """
       <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Disease Result</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-image: #f5f1f1; margin: 0; padding: 0;">
            <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f0f0;">
                <tr>
                    <td align="center" style="padding: 20px;">
                        <table cellpadding="0" cellspacing="0" width="600"  style=" background-color:#2f7e7fa4;border-radius: 10px; box-shadow: 0 2px 4px rgba(249, 249, 249, 0.938);">
                            <tr >
                                <td colspan="2" style="background-color: #090909; text-align: center; padding: 20px; border-top-left-radius: 10px; border-top-right-radius: 10px;">
                                    <h1 style="color: #f9f7f7; margin: 0;">Disease Result</h1>
                                </td>
                            </tr>
                            <tr>
                                <td rowspan="3" style="text-align: center;">
                                    
                                    <h5 style="text-align: left;margin-left: 25px;font-weight: bold;font-size: 16px;color: #f6f4f4;text-align: center;font-size: large;margin-top: 10px;">Skin Image</h5>
                                    <img src="disease.jpg" alt="Disease Image" style="width: 100; height: 100;margin-bottom: 10px;">
                                </td>
                                <td style="padding: 20px;">
                                    <h2 style="color: #fbfafa;text-align: center;">Disease Name</h2>
                                    <h3 style="text-align: center;">"""+res+"""</h3></td></tr>
                                <tr><td style="padding: 20px;">
                                    <p style="font-size:15px;"><h4 style="font-weight: bold;color:#f8f6f6;text-align: center;font-size:large;margin-top: 10px;">Description</h4>
                                    </p>
                                    <h3 style="text-align: center;">"""+description+"""</h3></td></tr>
                                <tr><td style="padding: 20px;">
                                    <p style="font-size: 16px; color: #faf9f9; font-weight: bold;font-size: large;text-align: center;margin-top: 10px;">Remedies
                                    </p>
                                    <h3 style="text-align: center;">"""+remedies+"""</h3>
                                </td>
                            </tr>
                            <tr>
                                <td colspan="2" style="background-color: #0b0b0b; text-align: center; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                                    <p style="color: #f8f5f5; margin: 0;font-weight:Bold;">THANK YOU</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>"""
        cid = "disease_image"

        # Modify the HTML body to include the CID in the img tag
        body = body.replace('<img src="disease.jpg"', f'<img src="cid:{cid}"')
        # Create an EmailMessage
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = session['email']
        em['Subject'] = subject
        em.set_content(body, subtype='html')

        # Add the image attachment
        with open(path, 'rb') as image_file:
            image_data = image_file.read()
            em.add_related(
                image_data,
                maintype='image',
                subtype='jpg',
                cid=cid,# Adjust the subtype based on your image type (e.g., png, jpeg)
                filename='disease.jpg' 
                # The filename that the recipient will see
            )
        # Add SSL (layer of security)
        context = ssl.create_default_context()
        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, session['email'], em.as_string())
        res = session['res']
        description=session['description']
        remedies=session['remedies']
        disease="Disease"
        description1="Description"
        remedies1="Remedies"
        return jsonify({
            'res':res,
            'description': description,
            'remedies': remedies,'disease':disease,'description1':description1,'remedies1':remedies1})
@app.route('/camera')
def camera():
    return render_template('cam.html')    
@app.route('/capture', methods=['POST'])
def capture():
    # Get the uploaded image file
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    image = request.files['image']
    temp_image_path = 'temp_image.jpg'
    image.save(temp_image_path)
    save_path = temp_image_path 
    res = process_and_predict(save_path)
    res=res.strip()
    print(res)
    result=data[data["Disease"]==res]
    description=result["Description"].values[0]
    remedies=result["Basic Remedies"].values[0]
    session['res'] =res.upper()     
    session['description'] = description
    session['remedies'] = remedies
    email=session['email']
    disease=session['res']
    filepath=save_path
    with open(filepath,"rb") as File:
        image=File.read()
    insert_query = "INSERT INTO results (email, photo, disease) VALUES (%s, %s, %s)"
    data1 = (email, image, disease)
    cursor.execute(insert_query, data1)
    conn.commit()
    cursor.close()
    conn.close()
    last_inserted_id = cursor.lastrowid
    session['unique_id']=last_inserted_id
    subject = 'Mail from EpidermX'
    body = """
       <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Disease Result</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-image: #f5f1f1; margin: 0; padding: 0;">
            <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f0f0;">
                <tr>
                    <td align="center" style="padding: 20px;">
                        <table cellpadding="0" cellspacing="0" width="600"  style=" background-color:#2f7e7fa4;border-radius: 10px; box-shadow: 0 2px 4px rgba(249, 249, 249, 0.938);">
                            <tr >
                                <td colspan="2" style="background-color: #090909; text-align: center; padding: 20px; border-top-left-radius: 10px; border-top-right-radius: 10px;">
                                    <h1 style="color: #f9f7f7; margin: 0;">Disease Result</h1>
                                </td>
                            </tr>
                            <tr>
                                <td rowspan="3" style="text-align: center;">
                                    
                                    <h5 style="text-align: left;margin-left: 25px;font-weight: bold;font-size: 16px;color: #f6f4f4;text-align: center;font-size: large;margin-top: 10px;">Skin Image</h5>
                                    <img src="disease.jpg" alt="Disease Image" style="width: 100; height: 100;margin-bottom: 10px;">
                                </td>
                                <td style="padding: 20px;">
                                    <h2 style="color: #fbfafa;text-align: center;">Disease Name</h2>
                                    <h3 style="text-align: center;">"""+res+"""</h3></td></tr>
                                <tr><td style="padding: 20px;">
                                    <p style="font-size:15px;"><h4 style="font-weight: bold;color:#f8f6f6;text-align: center;font-size:large;margin-top: 10px;">Description</h4>
                                    </p>
                                    <h3 style="text-align: center;">"""+description+"""</h3></td></tr>
                                <tr><td style="padding: 20px;">
                                    <p style="font-size: 16px; color: #faf9f9; font-weight: bold;font-size: large;text-align: center;margin-top: 10px;">Remedies
                                    </p>
                                    <h3 style="text-align: center;">"""+remedies+"""</h3>
                                </td>
                            </tr>
                            <tr>
                                <td colspan="2" style="background-color: #0b0b0b; text-align: center; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                                    <p style="color: #f8f5f5; margin: 0;font-weight:Bold;">THANK YOU</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>"""
    cid = "disease_image"

    # Modify the HTML body to include the CID in the img tag
    body = body.replace('<img src="disease.jpg"', f'<img src="cid:{cid}"')
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = session['email']
    em['Subject'] = subject
    em.set_content(body, subtype='html')
    # Add the image attachment
    with open(save_path, 'rb') as image_file:
        image_data = image_file.read()
        em.add_related(
            image_data,
            maintype='image',
            subtype='jpg', 
            cid=cid,# Adjust the subtype based on your image type (e.g., png, jpeg)
            filename='disease.jpg'  # The filename that the recipient will see
        )
    # Add SSL (layer of security)
    context = ssl.create_default_context()
    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, session['email'], em.as_string())
    res = session['res']
    description=session['description']
    remedies=session['remedies']
    disease="Disease"
    description1="Description"
    remedies1="Remedies"
    return jsonify({
        'res': res,
        'description': description,
        'remedies': remedies,'disease':disease,'description1':description1,'remedies1':remedies1})
@app.route('/loggedin')
def loggedin():
    session['logged_in']=True
    return render_template('home.html')
@app.route('/results')
def results():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    email = session['email']
    # Fetch data from the 'results' table based on the email
    cursor.execute("SELECT * FROM results WHERE email = %s", (email,))
    data2 = cursor.fetchall()
    # Count the number of records with 'disease' column value equal to 'Normal'
    cursor.execute("SELECT COUNT(disease) FROM results WHERE disease = 'Normal' and email = %s", (email,))
    normal = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM results where email = %s", (email,))
    total = cursor.fetchall()
    total = total[0]['COUNT(*)']
    normal = normal[0]['COUNT(disease)']
    # Calculate the percentage of 'Normal' records
    if total > 0:
        normal_percentage = (normal / total) * 100
        normal_percentage = round(normal_percentage, 2)
        total_percentage = 100 - normal_percentage
        total_percentage = round(total_percentage, 2)
    else:
        normal_percentage = 0.0
        total_percentage=0.0
    # Calculate the percentage of records that are not 'Normal'
   
    # Convert BLOB image data to Base64 strings
    
    for row in data2:
        row['photo']=base64.b64encode(row['photo']).decode('utf-8')
    # Render the HTML template and pass the data to it
    cursor.close()
    conn.close()
    return render_template('newdash.html', data1=data2,message="User")
@app.route('/admin')
def admin():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT * FROM results")
    data3 = cursor.fetchall()
    # Count the number of records with 'disease' column value equal to 'Normal'
    cursor.execute("SELECT COUNT(disease) FROM results WHERE disease = 'Normal'")
    normal = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM results ")
    total = cursor.fetchall()
    total = total[0]['COUNT(*)']
    normal = normal[0]['COUNT(disease)']

    # Calculate the percentage of 'Normal' records
    if total > 0:
        normal_percentage = (normal / total) * 100
        normal_percentage = round(normal_percentage, 2)
    else:
        normal_percentage = 0.0

    # Calculate the percentage of records that are not 'Normal'
    total_percentage = 100 - normal_percentage
    total_percentage = round(total_percentage, 2)
    # Convert BLOB image data to Base64 strings
    for row in data3:
        row['photo']=base64.b64encode(row['photo']).decode('utf-8')
    # Render the HTML template and pass the data to it
    cursor.close()
    conn.close()
    return render_template('newdash.html', data1=data3)
@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html')
@app.route('/consult')
def consult():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    sql_query = """
    SELECT doctors.email, COUNT(waiting.email) AS occurrences
    FROM doctors
    LEFT JOIN waiting ON doctors.email = waiting.email
    GROUP BY doctors.email
    ORDER BY occurrences ASC;
    """
    cursor.execute(sql_query)
    results = cursor.fetchall()
    mail=results[0]['email']
    insert_query = "INSERT INTO waiting (unique_number, date,time,email) VALUES (%s, %s, %s,%s)"
    data1 = (session['unique_id'], current_date, current_time,mail)
    cursor.execute(insert_query, data1)
    conn.commit()
    cursor.close()
    conn.close()
    subject = 'Mail from EpidermX'
    body="""
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Disease Result</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-image: #f5f1f1; margin: 0; padding: 0;">
        <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f0f0;">
            <tr>
                <td align="center" style="padding: 20px;">
                    <table cellpadding="0" cellspacing="0" width="600" style=" background-color:#2f7e7fa4;border-radius: 10px; box-shadow: 0 2px 4px rgba(249, 249, 249, 0.938);">
                        <tr >
                            <td colspan="2" style="background-color: #090909; text-align: center; padding: 20px; border-top-left-radius: 10px; border-top-right-radius: 10px;">
                                <h1 style="color: #f9f7f7; margin: 0;">You Got an Appointment</h1>
                            </td>
                        </tr>
                            <tr >
                                <td style="padding: 20px; text-align: center;">
                                   
                                        <a href="http://127.0.0.1:5000/login">Click here to login</a>                                 
                                </td>
                            </tr>
                            
                    
                        <tr>
                            <td colspan="2" style="background-color: #0b0b0b; text-align: center; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                                <p style="color: #f8f5f5; margin: 0;font-weight:Bold;">THANK YOU</p>
                            </td>
                        </tr>
                    
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = mail
    em['Subject'] = subject
    em.set_content(body,subtype="html")
    context = ssl.create_default_context()
    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender,mail, em.as_string())
    return "consulted"
@app.route('/consulted')  
def consulted():
    return render_template('consult.html')
@app.route('/backpredict')
def backpredict():
    return render_template('camerapg (1).html')
@app.route('/doctor',methods=['POST','GET'])
def doctor():
    if request.method == 'POST':
        conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
        cursor = conn.cursor(dictionary=True) 
        data = request.get_json()
        unique_number = data.get('uniqueNumber')
        session['unique_number'] = unique_number
        cursor.execute("SELECT photo, disease FROM results WHERE unique_number = %s", (unique_number,))
        data3 = cursor.fetchall()
        # Assuming data3 is a list of dictionaries containing photo and disease information
        for row in data3:
            row['photo']=base64.b64encode(row['photo']).decode('utf-8')
            cursor.close()
            conn.close()
        return data3
    return "Invalid Request Method"
@app.route('/prescription',methods=['POST','GET'])
def prescription():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    prescription=request.form['prescription']
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    # SQL query to delete a row based on unique_number
    delete_query = "DELETE FROM waiting WHERE unique_number = %s"
    cursor.execute(delete_query, (session['unique_number'],))
    insert_query = "INSERT INTO reviewed (unique_number,description,date,time,email) VALUES (%s, %s, %s,%s,%s)"
    data1 = (session['unique_number'],prescription,current_date,current_time,session['email'])
    cursor.execute(insert_query, data1)
    conn.commit()
    mail_query="SELECT email,photo,disease FROM results WHERE unique_number = %s"
    cursor.execute(mail_query, (session['unique_number'],))
    results=cursor.fetchall()
    patient_email=results[0]['email']
    disease=results[0]['disease']
    image_data=results[0]['photo']
    subject = 'Mail from EpidermX'
    body="""
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Disease Result</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-image: #f5f1f1; margin: 0; padding: 0;">
        <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f0f0;">
            <tr>
                <td align="center" style="padding: 20px;">
                    <table cellpadding="0" cellspacing="0" width="600"  style="background-color:#2f7e7fa4;border-radius: 10px; box-shadow: 0 2px 4px rgba(249, 249, 249, 0.938);">
                        <tr >
                            <td colspan="2" style="background-color: #090909; text-align: center; padding: 20px; border-top-left-radius: 10px; border-top-right-radius: 10px;">
                                <h1 style="color: #f9f7f7; margin: 0;">Doctors Prescription</h1>
                            </td>
                        </tr>
                        <tr>
                            <td rowspan="2" style="text-align: center;">
                                
                                <h5 style="text-align: left;margin-left: 50px;font-weight: bold;font-size: 16px;color: #f6f4f4;text-align: center;font-size: large;margin-top: 10px;">Skin Image</h5>
                                <img src="disease.jpg" alt="Disease Image" style="width: 200; height: 200;margin-bottom: 10px;">
                            </td>
                            <td style="padding: 20px;">
                                <h2 style="color: #fbfafa;text-align: center;">Disease Got</h2>
                                <h3 style="text-align: center;">"""+disease+"""</h3></td></tr>
                            <tr >
                                <td style="padding: 20px; text-align: center;">
                                    <h2 style="color: #fbfafa;text-align: center;">Disease Prescription</h2>
                                    <div style="border: 1px solid #f7f4f4; padding: 10px; width: 200px;margin-left: 50px;">
                                        <p>"""+prescription+"""</p>
                                    </div>
                                </td>
                            </tr>
                        <tr>
                            <td colspan="2" style="background-color: #0b0b0b; text-align: center; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                                <p style="color: #f8f5f5; margin: 0;font-weight:Bold;">THANK YOU</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    cid = "disease_image"

    # Modify the HTML body to include the CID in the img tag
    body = body.replace('<img src="disease.jpg"', f'<img src="cid:{cid}"')
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = patient_email
    em['Subject'] = subject
    em.set_content(body, subtype='html')
    # Add the image attachment
    
    em.add_related(
        image_data,
        maintype='image',
        subtype='jpg', 
        cid=cid,# Adjust the subtype based on your image type (e.g., png, jpeg)
        filename='disease.jpg'  # The filename that the recipient will see
    )
    # Add SSL (layer of security)
    context = ssl.create_default_context()
    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, patient_email, em.as_string())
    cursor.close()
    conn.close()    
    return "prescribed"
@app.route('/godoctor')
def godoctor():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    msg = request.args.get('alert', '')
    cursor.execute("SELECT unique_number,date,time FROM waiting WHERE email = %s", (session['email'],))
    data3 = cursor.fetchall()
    for row in data3:
        row['date']=str(row['date'].strftime("%d-%m-%Y"))
        row['time']=str(row['time'])
    cursor.close()
    conn.close()    
    return render_template('doctor.html',data1=data3,alert_message=msg)
@app.route('/registerdoctor')
def registerdoctor():
    return render_template('doctorregister.html') 
@app.route('/doctorregister',methods=['POST','GET'])
def doctorregister():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    name=request.form['user']
    email=request.form['email']
    pass1=request.form['pass1']
    pass2=request.form['pass2']
    experience=request.form['experience']
    experience=int(experience)
    qualification=request.form['qualification']
    phone=request.form['phone']
    if pass1==pass2: 
        conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
        cursor = conn.cursor()
        sql="SELECT * FROM doctors WHERE email = %s"
        cursor.execute(sql,(email,))
        result=cursor.fetchall()
        if len(result)>0:
            return render_template('doctorregister.html',message="Email already exists/please signin")
        sql = "INSERT INTO doctors VALUES (%s, %s,%s,%s,%s,%s)"
        pass1=bcrypt.hashpw(pass1.encode('utf-8'), bcrypt.gensalt())
        val = (email,pass1,phone,name,qualification,experience)
        cursor.execute(sql, val)
        conn.commit()
        session['logged_in']=True
        session['doctor']=True
        session['email']=email
        session['name']=name
        cursor.close()
        conn.close()
        return redirect(url_for('loggedin'))
    else:
        cursor.close()
        conn.close()
        return render_template('doctorregister.html',message="Passwords should be same")
@app.route('/patientsreviewed')
def patientsreviewed():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    query = """
    SELECT r.unique_number, r.description, res.photo, res.disease
    FROM reviewed r
    JOIN results res ON r.unique_number = res.unique_number
    WHERE r.email = %s;
    """
    # Execute the query with the email parameter
    cursor.execute(query, (session['email'],))

    # Fetch all the results from the query
    data3 = cursor.fetchall()

    # Convert the 'photo' column from bytes to base64 encoded string
    for row in data3:
        row['photo'] = base64.b64encode(row['photo']).decode('utf-8')

    # Close the cursor and connection
    cursor.close()
    conn.close()
    # Pass the data to the template and render it
    return render_template('reviewed.html', data1=data3)
@app.route('/doctorconsulted')
def doctorconsulted():
    conn=mysql.connector.connect(host="localhost",user="root",password="",database="test")
    cursor = conn.cursor(dictionary=True) 
    query = """
    SELECT r.unique_number, r.description, res.photo, res.disease
    FROM reviewed r
    JOIN results res ON r.unique_number = res.unique_number
    WHERE res.email = %s;
    """
    # Execute the query with the email parameter
    cursor.execute(query, (session['email'],))

    # Fetch all the results from the query
    data3 = cursor.fetchall()

    # Convert the 'photo' column from bytes to base64 encoded string
    for row in data3:
        row['photo'] = base64.b64encode(row['photo']).decode('utf-8')

    # Close the cursor and connection
    cursor.close()
    conn.close()
    # Pass the data to the template and render it
    return render_template('doctorconsulted.html', data1=data3)
@app.route("/translate/<lang>")
def translate(lang):
        res = translate_to(session['res'],lang)
        description=translate_to(session['description'],lang)
        remedies=translate_to(session['remedies'],lang)
        disease=translate_to("Disease",lang)
        description1=translate_to("Description",lang)
        remedies1=translate_to("Remedies",lang)
        return jsonify({
            'res': res,
            'description': description,
            'remedies': remedies,'disease':disease,'description1':description1,'remedies1':remedies1})