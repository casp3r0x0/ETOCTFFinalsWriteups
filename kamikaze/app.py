from flask import Flask, render_template_string, request, redirect, url_for, session
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

users = {}
items = {
    'item1': {'name': 'بطيخ', 'price': 500},
    'item2': {'name': 'فروله', 'price': 500},
    'item3': {'name': 'حبي لالك 🌹', 'price': 500},
    'flag': {'name': 'FLAG', 'price': 9999999}
}

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Shop{% endblock %}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #333;
        }
        form {
            margin: 20px 0;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 3px;
            box-sizing: border-box;
        }
        button, input[type="submit"] {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            margin: 5px 0;
        }
        button:hover, input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .error {
            color: red;
            margin: 10px 0;
        }
        .success {
            color: green;
            margin: 10px 0;
        }
        .info {
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 3px;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        table th, table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .nav {
            margin-bottom: 20px;
        }
        .nav a {
            margin-right: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
'''

INDEX_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <h1>Welcome to the Shop</h1>
        <div class="nav">
            <a href="{{ url_for('login') }}">Login</a>
            <a href="{{ url_for('register') }}">Register</a>
        </div>
        <p>Please login or register to continue.</p>
''')

REGISTER_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <h1>Register</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Register">
        </form>
        <p><a href="{{ url_for('login') }}">Already have an account? Login</a></p>
''')

LOGIN_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <h1>Login</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Login">
        </form>
        <p><a href="{{ url_for('register') }}">Need an account? Register</a></p>
''')

SHOP_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <h1>Shop</h1>
        <div class="nav">
            <a href="{{ url_for('shop') }}">Shop</a>
            <a href="{{ url_for('inventory') }}">My Inventory</a>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
        <div class="info">
            <strong>Credits:</strong> {{ credits }}
        </div>
        {% if message %}
        <div class="success">{{ message }}</div>
        {% endif %}
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <h2>Available Items</h2>
        <h3>please buy at least 3 items so you can get the flag!</h3>
        <table>
            <tr>
                <th>Item</th>
                <th>Price</th>
                <th>Action</th>
            </tr>
            {% for item_id, item_data in items.items() %}
            <tr>
                <td>{{ item_data.name }}</td>
                <td>{{ item_data.price }} credits</td>
                <td>
                    <form method="POST" action="{{ url_for('buy', item_id=item_id) }}" style="margin: 0;">
                        <button type="submit">Buy</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
''')

INVENTORY_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <h1>My Inventory</h1>
        <div class="nav">
            <a href="{{ url_for('shop') }}">Shop</a>
            <a href="{{ url_for('inventory') }}">My Inventory</a>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
        <div class="info">
            <strong>Credits:</strong> {{ credits }}
        </div>
        {% if flag %}
        <div class="success">
            <h2>Congratulations!</h2>
            <p>FLAG: {{ flag }}</p>
        </div>
        {% endif %}
        <h2>Your Items</h2>
        {% if inventory %}
        <table>
            <tr>
                <th>Item</th>
            </tr>
            {% for item in inventory %}
            <tr>
                <td>{{ item }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>You have no items yet.</p>
        {% endif %}
''')

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('shop'))
    return render_template_string(INDEX_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users:
            return render_template_string(REGISTER_TEMPLATE, error='Username already exists')
        
        users[username] = {
            'password': password,
            'credits': 1000,
            'inventory': []
        }
        
        session['username'] = username
        return redirect(url_for('shop'))
    
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username not in users or users[username]['password'] != password:
            return render_template_string(LOGIN_TEMPLATE, error='Invalid credentials')
        
        session['username'] = username
        return redirect(url_for('shop'))
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/shop')
def shop():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    credits = users[username]['credits']
    message = request.args.get('message')
    error = request.args.get('error')
    
    return render_template_string(SHOP_TEMPLATE, credits=credits, items=items, message=message, error=error)

@app.route('/buy/<item_id>', methods=['POST'])
def buy(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users[username]
    
    if item_id not in items:
        return redirect(url_for('shop', error='Item not found'))
    
    item = items[item_id]
    
    # Check if user bought 2 items and trying to buy flag
    if item_id == 'flag' and len(user['inventory']) >= 3:
        user['inventory'].append(item['name'])
        return redirect(url_for('inventory'))
    
    # VULNERABLE: Race condition - check credits first
    if user['credits'] < item['price']:
        return redirect(url_for('shop', error='Not enough credits'))
    
    # VULNERABLE: Sleep to widen the race condition window
    time.sleep(0.1)
    
    # VULNERABLE: Then deduct credits - multiple requests can pass the check above
    user['credits'] -= item['price']
    user['inventory'].append(item['name'])
    
    return redirect(url_for('shop', message=f'Successfully purchased {item["name"]}'))

@app.route('/inventory')
def inventory():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users[username]
    
    flag = None
    if 'FLAG' in user['inventory']:
        flag = 'cybereto{r4C3C0nD1710nbYC45P3R0X0}'
    
    return render_template_string(INVENTORY_TEMPLATE, 
                                 credits=user['credits'], 
                                 inventory=user['inventory'],
                                 flag=flag)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=1177)
