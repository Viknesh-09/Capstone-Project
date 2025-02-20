from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# HTML Page with Embedded Form and JavaScript
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask User Management</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="container mt-5">
    <h2 class="text-center">User Management</h2>

    <div class="card p-4 shadow">
        <form id="userForm">
            <div class="mb-3">
                <label for="name" class="form-label">Enter Name</label>
                <input type="text" id="name" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Add User</button>
        </form>
    </div>

    <h3 class="mt-5">User List</h3>
    <ul id="userList" class="list-group mt-3"></ul>

    <script>
        document.getElementById('userForm').addEventListener('submit', function(event) {
            event.preventDefault();
            let name = document.getElementById('name').value;

            fetch('/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                document.getElementById('name').value = '';
                loadUsers();
            });
        });

        function loadUsers() {
            fetch('/users')
            .then(response => response.json())
            .then(users => {
                let userList = document.getElementById('userList');
                userList.innerHTML = '';
                users.forEach(user => {
                    let li = document.createElement('li');
                    li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
                    li.innerHTML = `${user.name} <button class="btn btn-danger btn-sm" onclick="deleteUser(${user.id})">Delete</button>`;
                    userList.appendChild(li);
                });
            });
        }

        function deleteUser(id) {
            fetch(`/users/${id}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadUsers();
            });
        }

        window.onload = loadUsers;
    </script>
</body>
</html>
"""

# Route to serve HTML page
@app.route('/')
def home():
    return HTML_PAGE

# API to add a user
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    user = User(name=data['name'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User added"}), 201

# API to fetch users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "name": user.name} for user in users]
    return jsonify(user_list)

# API to delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"})
    return jsonify({"message": "User not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)