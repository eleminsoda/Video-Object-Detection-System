from flask import Flask, render_template, redirect, request
import os
from detect import detect_object
import logging
from cassandra.cluster import Cluster

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_PATH = '../darknet/data'

KEY_SPACE = "myspace"

FLAG_CREATE_KEY_SPACE = 0

cluster = None
session = None


def allowed_file(filename):
    return '.' in filename and \
	   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    create_key_space()
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def get_video():
    if request.method == 'POST':
        video = request.files['videoSource']

        try:
            video.save(os.path.join(UPLOAD_PATH, video.filename))
        except Exception as e:
            print(e)
        

        detect_result = detect_object(video.filename)
        insert_data(video.filename, detect_result)
        return render_template('detect_result.html', result=detect_result, filename=video.filename)
    
    # return render_template('detect_result.html')

def insert_data(filename, objects):
    # cluster = Cluster(contact_points=['127.0.0.1'], port=9042)
    # cluster = Cluster(contact_points=['mynetwork'], port=9042)

    try:
        # cluster = Cluster(contact_points=['0.0.0.0'], port=9042)
        cluster = Cluster(contact_points=['172.18.0.3'], port=9042)
        session = cluster.connect()
        print('connected to cassandra in inserting data')

    except Exception as e:
        print(e)
        print('connetion failed in inserting data...')

    session.set_keyspace(KEY_SPACE)

    print('Inserting data ...')
    try:
        for item in objects:
            session.execute('''
            INSERT INTO objects (filename, id, frame, class, x, y, w, h)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',(filename, str(item[0]), str(item[1]), str(item[2]), str(item[3]), str(item[4]), str(item[5]), str(item[6])))
    except Exception as e:
        print(e)

def create_key_space():
    # nonlocal session, cluster

    try:
        # cluster = Cluster(contact_points=['0.0.0.0'], port=9042)
        cluster = Cluster(contact_points=['172.18.0.3'], port=9042)
        session = cluster.connect()
        print('connected to cassandra')

    except Exception as e:
        print(e)
        print('connetion failed ...')
    

    try:
        session.execute('''
        CREATE KEYSPACE IF NOT EXISTS %s
        WITH replication={'class':'SimpleStrategy', 'replication_factor' : 2}
        '''%KEY_SPACE)

        print('setting key space')
        session.set_keyspace(KEY_SPACE)

        print('creating table')
        session.execute('''
        CREATE TABLE  IF NOT EXISTS objects(
            filename text,
            id text,
            frame text,
            class text,
            x text,
            y text,
            w text,
            h text,
            PRIMARY KEY (filename, id)
        )
        ''')
        print('succeed')
    except Exception as e:
        print('create key space failed')
        print(e)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
