from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
import random

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode)
available_compute_sockets = set()
tasks_mapping = {}

@app.route('/')
def index():
    return render_template('index.html', async_mode=socket_.async_mode)

@socket_.on('register_compute')
def register_compute():
    available_compute_sockets.add(request.sid)
    print(f"{request.sid} registered")
    print(f"[after append] available_compute_sockets: {available_compute_sockets}")
    
# Global host server (this guy) receives a file from local server
@socket_.on('send_file_to_global')
def receive_file(file):
    choose_from = list(available_compute_sockets)
    if request.sid in choose_from:
        choose_from.remove(request.sid)
    chosen_socket = random.choice(choose_from)
    print(f'The chosen one: {chosen_socket}')
    print(f'My socket: {request.sid}')
    # print(f'My request.namespace: {request.namespace}')
    tasks_mapping[chosen_socket] = request.sid
    emit('send_file_to_local', file, room=chosen_socket)

@socket_.on('send_result_to_global')
def receive_result(result):
    local = tasks_mapping[request.sid]
    del tasks_mapping[request.sid]
    emit('send_result_to_local', result, room=local)

@socket_.on('unregister_compute')
def unregsiter_compute():
    if request.sid in available_compute_sockets:
        available_compute_sockets.remove(request.sid)
    print(f"{request.sid} unregistered")
    print(f"[after remove] available_compute_sockets: {available_compute_sockets}")

@socket_.on('disconnect')
def disconnect():
    if request.sid in available_compute_sockets:
        available_compute_sockets.remove(request.sid)
    print(f"{request.sid} disconnected, so I will unregister")
    print(f"[after remove] available_compute_sockets: {available_compute_sockets}")


if __name__ == '__main__':
    socket_.run(app, debug=True, host='0.0.0.0', port='5252')
