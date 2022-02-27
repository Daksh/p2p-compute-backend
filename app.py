from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from flask import request

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode)

@app.route('/')
def index():
    return render_template('index.html', async_mode=socket_.async_mode)


@socket_.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socket_.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socket_.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)

@socket_.on('join', namespace='/test')
def on_join(data):
    username = data['username']
    room = data['room']
    print("request.sid is ",request.sid)
    print('join got this (username, room):', username, room)
    join_room(room)
    # emit('my_response', {'data':username+' has joined the room.'}, broadcast=True)
    emit('my_response', {'[sent from server] data':username+' has joined the room.'}, to='myroomname')
    # print("DONE SENDING")

# @socket_.on('leave', namespace='/test')
# def on_leave(data):
#     username = data['username']
#     room = data['room']
#     leave_room(room)
#     emit('room_response', {'data':username+' has left the room.'}, to=room, broadcast=True)

@socket_.on('room_response', namespace='/test')
def on_myroom(data):
    print("LOOOK OUT FOR THIS i got this message", request.sid)
    emit('my_response', data)

@socket_.on('my_response_some', namespace='/test')
def log(data):
    print("LOG:",data)

if __name__ == '__main__':
    socket_.run(app, debug=True, host='0.0.0.0', port='5255')
