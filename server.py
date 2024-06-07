from flask import Flask, request, jsonify


app = Flask(__name__)
peers_data = []


# Register a peer
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    socket = data.get('socket')

    # Check the both peer name and socket been presence
    if not username or not socket:
        return jsonify({'error': 'Username and socket are required'}), 400

    # Check the user and socket don't used before
    for peer in peers_data:
        if username == peer.get("username") or socket == peer.get("socket"):
            return jsonify({'error': 'Username and socket should be uniqued'}), 400

    # Store new peer
    peers_data.append({"username": username, "socket": socket})
    return jsonify({'message': 'User registered successfully'}), 201


# Get all peers
@app.route('/peers', methods=['GET'])
def get_all_users():
    return jsonify(peers_data)


# Get one peer address
@app.route('/peerinfo', methods=['POST'])
def get_one_user():
    data = request.get_json()
    for peer in peers_data:
        if data.get("username") == peer.get("username"):
            return jsonify({"username": peer.get("username"), "socket": peer.get("socket")}), 201
    return jsonify({"message": "Can't find any peer wiht this username!"})


if __name__ == '__main__':
    app.run(debug=True)
