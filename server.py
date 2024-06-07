from flask import Flask, request, jsonify
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

# Register a peer
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    socket = data.get('socket')

    if not username or not socket:
        return jsonify({'error': 'Username and socket are required'}), 400

    # Check if the username exists in Redis
    if r.get(username):
        return jsonify({'error': 'Username already exists'}), 400

    r.set(username, socket)
    return jsonify({'message': 'User registered successfully'}), 201

# Get all peers
@app.route('/peers', methods=['GET'])
def get_all_users():
    all_users = {}
    keys = r.keys('*')
    for key in keys:
        all_users[key.decode()] = r.get(key).decode()
    return jsonify(all_users)

# Get one peer address
@app.route('/peerinfo', methods=['POST'])
def get_one_user():
    data = request.get_json()
    username = data.get("username")
    socket = r.get(username)
    if socket:
        return jsonify({"username": username, "socket": socket.decode()}), 200
    return jsonify({"message": "Can't find any peer with this username!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
