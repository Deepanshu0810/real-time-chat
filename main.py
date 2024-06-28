from flask import Flask, request, session, render_template, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
from dotenv import load_dotenv
import os
import random
import string
from datetime import datetime

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)


rooms = {}

def generate_room_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(string.ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route('/',methods=['GET','POST'])
def index():
    session.clear()
    if request.method == 'POST':
        name= request.form.get('username')
        code= request.form.get('roomcode')
        join = request.form.get('join',False)
        create = request.form.get('create',False)
        
        if not name:
            return render_template('home.html',error='Please enter a name',roomcode=code, name=name)
        
        if join != False and not code:
            return render_template('home.html',error='Please enter a room code',roomcode=code, name=name)
        
        room = code
        if create != False:
            room = generate_room_code(4)
            rooms[room] = {'members':0, "messages":[]}

        elif code not in rooms:
            return render_template('home.html',error='Room does not exist',roomcode=code, name=name)
        
        session['name'] = name
        session['room'] = room
        return redirect(url_for('chatroom'))

    return render_template('home.html')

@app.route('/chatroom')
def chatroom():
    name = session.get('name')
    room = session.get('room')
    if room is None or name is None or room not in rooms:
        return redirect(url_for('index'))
    
    return render_template('chatroom.html',name=name,roomcode=room)

@socketio.on('connect')
def connect(auth):
    name = session.get('name')
    room = session.get('room')
    if room is None or name is None or room not in rooms:
        return False
    
    if room not in rooms:
        leave_room(room)
        return False
    
    join_room(room)
    rooms[room]['members'] += 1
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send({"name":name,"message":f"{name} has joined the chat","timestamp":dt},to=room)
    print(f"{name} has joined room {room}")

@socketio.on('disconnect')
def disconnect():
    name = session.get('name')
    room = session.get('room')
    if room is None or name is None or room not in rooms:
        return False
    
    leave_room(room)

    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] <= 0:
            del rooms[room]
            print(f"Room {room} has been deleted")

    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send({"name":name,"message":f"{name} has left the chat","timestamp":dt},to=room)
    print(f"{name} has left room {room}")

if __name__ == '__main__':
    socketio.run(app,debug=True)