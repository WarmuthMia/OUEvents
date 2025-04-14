import mysql.connector
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import cgi
from werkzeug.security import check_password_hash, generate_password_hash

UPLOAD_DIR = 'uploads'

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1MISFieldProjectRootPassword123!",
        database="ou_events"
    )
    return conn

def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            print(f"Connected to database: {result[0]}")
        else:
            print("Failed to connect to database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        print(f"Received GET request for path: {self.path}")
        if self.path == '/events':
            self.handle_get_events()
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

    def do_POST(self):
        print(f"Received POST request for path: {self.path}")
        if self.path == '/login':
            self.handle_login()
        elif self.path == '/signup':
            self.handle_signup()
        elif self.path == '/add_event':
            self.handle_create_event()
        elif self.path == '/edit_event':
            self.handle_edit_event()
        elif self.path == '/delete_event':
            self.handle_delete_event()
        elif self.path == '/upload_profile_picture':
            self.handle_profile_picture_upload()
        elif self.path == '/edit_profile':
            self.handle_edit_profile()
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

    def handle_test_db_connection(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'data': result}).encode())
        else:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'message': 'No data found'}).encode())

    def handle_login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        print(f"Handling login for data: {data}")
        username = data['username']
        password = data['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[0], password):
            print("Password is correct")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        else:
            print("Password is incorrect or user not found")
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False}).encode())

    def handle_signup(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        print(f"Handling signup for data: {data}")
        username = data['username']
        password = data['password']
        email = data['email']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        user = cursor.fetchone()

        if user:
            print("Username or email already exists")
            self.send_response(409)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'message': 'Username or email already exists'}).encode())
        else:
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
            conn.commit()
            cursor.close()
            conn.close()

            print("User created successfully")
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())

    def handle_get_events(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        cursor.close()
        conn.close()

        event_list = []
        for event in events:
            event_list.append({
                'id': event[0],
                'name': event[1],
                'host': event[2],
                'time': event[3].strftime('%Y-%m-%d %H:%M:%S'),
                'location': event[4],
                'category': event[5],
                'image': event[6]
            })

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'events': event_list}).encode())

    def handle_create_event(self): 
        '''
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        title = data['title']
        description = data['description']
        date = data['date']
        time = data['time']
        location = data['location']
        email = data['email']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (title, description, date, time, location, email) VALUES (%s, %s, %s, %s, %s, %s)", (title, description, date, time, location, email))
        conn.commit()
        cursor.close()
        conn.close()

        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
        '''
        content_type, pdict = cgi.parse_header(self.headers['Content-Type'])
        if content_type == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            name = form.getvalue('name')
            host = form.getvalue('host')
            time = form.getvalue('time')
            location = form.getvalue('location')
            category = form.getvalue('category')

            # Check if 'image' is in the form
            image_file = form['image'] if 'image' in form else None 

            if image_file is not None and hasattr(image_file, 'filename') and image_file.filename:
                image_path = os.path.join(UPLOAD_DIR, image_file.filename)
                with open(image_path, 'wb') as f:
                    f.write(image_file.file.read())
                image_url = f"/{UPLOAD_DIR}/{image_file.filename}"
            else:
                image_url = None

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO events (name, host, time, location, category, image) VALUES (%s, %s, %s, %s, %s, %s)",
                           (name, host, time, location, category, image_url))
            conn.commit()
            cursor.close()
            conn.close()

            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'message': 'Invalid form data'}).encode())

    def handle_edit_event(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        event_id = data['id']
        title = data['title']
        description = data['description']
        date = data['date']
        time = data['time']
        location = data['location']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET title = %s, description = %s, date = %s, time = %s, location = %s WHERE id = %s", (title, description, date, time, location, event_id))
        conn.commit()
        cursor.close()
        conn.close()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())

    def handle_delete_event(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        event_id = data['id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        conn.commit()
        cursor.close()
        conn.close()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())

    def handle_profile_picture_upload(self):
        content_type, pdict = cgi.parse_header(self.headers['Content-Type'])
        if content_type == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            image_file = form['profile_picture']
            if image_file.filename:
                image_path = os.path.join(UPLOAD_DIR, image_file.filename)
                with open(image_path, 'wb') as f:
                    f.write(image_file.file.read())
                image_url = f"/{UPLOAD_DIR}/{image_file.filename}"

                # Update user's profile picture URL in the database
                email = form.getvalue('email')
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET profile_picture = %s WHERE email = %s", (image_url, email))
                conn.commit()
                cursor.close()
                conn.close()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': 'No file uploaded'}).encode())

    def handle_edit_profile(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        username = data['username']
        password = data['password']
        email = data['email']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET username = %s, password = %s WHERE email = %s", (username, hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())

    def handle_profile_picture_upload(self):
        content_type, pdict = cgi.parse_header(self.headers['Content-Type'])
        if content_type == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            image_file = form['profile_picture']
            if image_file.filename:
                image_path = os.path.join(UPLOAD_DIR, image_file.filename)
                with open(image_path, 'wb') as f:
                    f.write(image_file.file.read())
                image_url = f"/{UPLOAD_DIR}/{image_file.filename}"

                # Update user's profile picture URL in the database
                email = form.getvalue('email')
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET profile_picture = %s WHERE email = %s", (image_url, email))
                conn.commit()
                cursor.close()
                conn.close()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': 'No file uploaded'}).encode())

    def handle_edit_profile(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        username = data['username']
        password = data['password']
        email = data['email']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET username = %s, password = %s WHERE email = %s", (username, hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=5000):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    test_db_connection()
    run()