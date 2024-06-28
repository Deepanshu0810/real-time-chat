from flask import Flask, request, session, render_template, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
from dotenv import load_dotenv
import os
import random
import string

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

if __name__ == '__main__':
    socketio.run(app,debug=True)