from flask import Flask, jsonify, request, redirect, url_for, render_template_string, session
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db, User, Team, SportType, Tryout, Player

app = Flask(__name__)

# SQLAlchemy Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Mihir:Mihir%4020@localhost/tryouts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '2963d38761f8725b847d5c6452ec8108'

# Initialize SQLAlchemy, Migrate, and Flask-Login
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_view = 'player_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.user_loader
def load_player(player_id):
    return Player.query.get(int(player_id))

@app.route('/')
def index():
    return render_template_string('''
            <h1>Tryouts</h1>
            <p><a href="/player_login">Looking for tryouts as a player?</a></p>
            <p><a href="/login">Login for team management</a></p>
            
            
        ''')

@app.route('/player_register', methods=['GET', 'POST'])
def player_register():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            date_of_birth = request.form.get('date_of_birth')
            experience = request.form.get('experience')
            position = request.form.get('position')
            phone_number = request.form.get('phone_number')

            # Ensure all required fields are provided
            if not all([email, password, first_name, last_name, date_of_birth, phone_number]):
                return jsonify({"error": "All required fields must be provided"}), 400

            # Hash the password
            hashed_password = generate_password_hash(password)

            # Convert date_of_birth to datetime object
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d')

            # Create a new player instance
            new_player = Player(
                email=email,
                password_hash=hashed_password,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                experience=experience,
                position=position,
                phone_number=phone_number
            )

            db.session.add(new_player)
            db.session.commit()

            return jsonify({"message": "Player registration successful!"}), 201

        except Exception as e:
            db.session.rollback()
            # Print the specific error to the console for debugging
            print(f"Error during player registration: {e}")
            return jsonify({"error": f"An error occurred: {e}"}), 500

    # Render registration form
    return '''
        <form method="post">
            First Name: <input type="text" name="first_name" required><br>
            Last Name: <input type="text" name="last_name" required><br>
            Email: <input type="email" name="email" required><br>
            Password: <input type="password" name="password" required><br>
            Date of Birth: <input type="date" name="date_of_birth" required><br>
            Experience: <textarea name="experience"></textarea><br>
            Position: <input type="text" name="position"><br>
            Phone Number: <input type="text" name="phone_number" required><br>
            <input type="submit" value="Register">
        </form>
    '''

# Player Login Route
@app.route('/player_login', methods=['GET', 'POST'])
def player_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        player = Player.query.filter_by(email=email).first()
        if player and check_password_hash(player.password_hash, password):
            login_user(player)
            return redirect(url_for('player_dashboard'))
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    return '''
        <form method="post">
            Email: <input type="email" name="email" required><br>
            Password: <input type="password" name="password" required><br>
            <input type="submit" value="Login">
        </form>
        <p>New player? <a href="/player_register">Register here</a></p>
    '''


# Player Dashboard Route
@app.route('/player_dashboard')
@login_required
def player_dashboard():
    # Filter live tryouts based on the deadline
    today = datetime.now().date()
    live_tryouts = Tryout.query.filter(Tryout.deadline >= today).all()

    return render_template_string('''
        <h1>Welcome to your Dashboard, {{ current_user.first_name }} {{ current_user.last_name }}</h1>
        <p>Email: {{ current_user.email }}</p>
        <p>Phone Number: {{ current_user.phone_number }}</p>
        <p><a href="{{ url_for('player_logout') }}">Logout</a></p>

        <h2>Apply for tryouts</h2>
        {% if live_tryouts %}
            <ul>
                {% for tryout in live_tryouts %}
                    <li>
                        <strong>Date:</strong> {{ tryout.date.strftime('%d-%m-%Y') }} <br>
                        <strong>Location:</strong> {{ tryout.location }} <br>
                        <strong>Description:</strong> {{ tryout.description }} <br>
                        <strong>Application Deadline:</strong> {{ tryout.deadline.strftime('%d-%m-%Y') }} <br>
                        <strong>Registration Link:</strong> 
                        <a href="{{ tryout.register_link }}" target="_blank">{{ tryout.register_link }}</a> <br>

                    </li>
                    <hr>
                {% endfor %}
            </ul>
        {% else %}
            <p>No live tryouts available.</p>
        {% endif %}
    ''', current_user=current_user, live_tryouts=live_tryouts)



# Player Logout Route
@app.route('/player_logout')
@login_required
def player_logout():
    logout_user()
    return redirect(url_for('player_login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    return '''
        <form method="post">
            Email: <input type="email" name="email"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
        <p>New here? <a href="/register">Click here to register</a></p>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password_hash=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "Registration successful!"}), 201
        except Exception as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e) or "IntegrityError" in str(e):
                return jsonify({"error": "Email already exists"}), 400
            return jsonify({"error": "An error occurred"}), 500

    return '''
        <form method="post">
            Email: <input type="email" name="email"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Register">
        </form>
    '''


@app.route('/dashboard')
@login_required
def dashboard():
    # Query only the teams created by the logged-in user
    teams = Team.query.filter_by(user_id=current_user.id).all()

    # Format the team data as HTML with the "Manage Tryouts" button
    teams_html = "<h2>Your Teams</h2><ul>"
    for team in teams:
        teams_html += f"""
            <li>
                <strong>Name:</strong> {team.name}, 
                <strong>Sport:</strong> {team.sport.value}, 
                <strong>League:</strong> {team.league}, 
                <strong>Division:</strong> {team.division}, 
                <strong>Unique Code:</strong> {team.unique_id}
                <form action="/manage_tryouts/{team.unique_id}" method="get" style="display:inline;">
                    <button type="submit">Manage Tryouts</button>
                </form>
            </li>
        """
    teams_html += "</ul>"

    # Add the Create Team button with a link to /create_team
    return f'''
        <h1>Welcome to the Dashboard!</h1>
        <form action="/create_team" method="get">
            <button type="submit">Create New Team</button>
        </form>
        {teams_html}
        <p><a href="/logout">Log Out</a></p>
    '''


@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():


    if request.method == 'POST':
        team_name = request.form['name']
        sport = request.form['sport']
        league = request.form['league']
        division = request.form.get('division')
        user_id = session['user_id']

        # Check if a team with the same name already exists
        existing_team = Team.query.filter_by(name=team_name).first()
        if existing_team:
            return "A team with this name already exists. Please choose a different name.", 400

        # Create a new team with a unique_id
        new_team = Team(name=team_name, sport=SportType[sport], league=league, division=division, user_id=user_id)

        try:
            db.session.add(new_team)
            db.session.commit()
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            return f"Error creating team: {e}"

    return render_template_string('''
        <h1>Create a New Team</h1>
        <form method="post">
            Team Name: <input type="text" name="name" required><br>
            Sport: 
            <select name="sport">
                <option value="Football">Football</option>
                <option value="Cricket">Cricket</option>
                <option value="Basketball">Basketball</option>
            </select><br>
            League: <input type="text" name="league"><br>
            Division: <input type="text" name="division"><br>
            <input type="submit" value="Create Team">
        </form>
        <p><a href="/dashboard">Back to Dashboard</a></p>
    ''')


@app.route('/manage_tryouts/<string:unique_id>')
@login_required
def manage_tryouts(unique_id):
    team = Team.query.filter_by(unique_id=unique_id).first()
    if not team:
        return "Team not found", 404

    # Include the status in the tryouts list
    tryouts = [
        {
            "id": tryout.id,
            "date": tryout.date,
            "location": tryout.location,
            "description": tryout.description,
            "deadline": tryout.deadline,
            "register_link": tryout.register_link,
            "status": check_application_status(tryout)
        }
        for tryout in Tryout.query.filter_by(team_id=team.id).all()
    ]

    return render_template_string('''
        <h1>Manage Tryouts for {{ team.name }}</h1>
        <form action="{{ url_for('create_tryout', unique_id=team.unique_id) }}" method="get">
            <button type="submit">Create New Tryout</button>
        </form>

        <h2>Existing Tryouts</h2>
        {% if tryouts %}
            <ul>
                {% for tryout in tryouts %}
                    <li>
                        <strong>Date:</strong> {{ tryout.date.strftime('%d-%m-%Y') }} <br>
                        <strong>Location:</strong> {{ tryout.location }} <br>
                        <strong>Description:</strong> {{ tryout.description }} <br>
                        <strong>Application Deadline:</strong> {{ tryout.deadline.strftime('%d-%m-%Y') }} <br>
                        <strong>Registration Link:</strong>
                        {% if tryout.register_link %}
                            <a href="{{ tryout.register_link }}" target="_blank">{{ tryout.register_link }}</a>
                        {% else %}
                            Not provided
                        {% endif %}
                        <br>
                        <strong>Status:</strong>
                        <span style="color: {{ 'red' if tryout.status == 'Expired' else 'green' }}">
                            {{ tryout.status }}
                        </span>
                        <form action="{{ url_for('edit_tryout', unique_id=team.unique_id, tryout_id=tryout.id) }}" method="get" style="display:inline;">
                            <button type="submit">Edit</button>
                        </form>
                    </li>
                    <hr>
                {% endfor %}
            </ul>
        {% else %}
            <p>No tryouts created for this team yet.</p>
        {% endif %}
        <p><a href="{{ url_for('dashboard') }}">Back to Dashboard</a></p>
    ''', team=team, tryouts=tryouts)


@app.route('/manage_tryouts/<string:unique_id>/create_tryout', methods=['GET', 'POST'])
@login_required
def create_tryout(unique_id):
    team = Team.query.filter_by(unique_id=unique_id).first()
    if not team:
        return "Team not found", 404

    if request.method == 'POST':
        date = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        register_link = request.form.get('register_link')

        try:
            tryout_date = datetime.strptime(date, '%Y-%m-%d')
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
        except ValueError:
            return "Invalid date format.", 400

        new_tryout = Tryout(
            date=tryout_date,
            location=location,
            description=description,
            deadline=deadline_date,
            register_link=register_link,
            team_id=team.id
        )

        try:
            db.session.add(new_tryout)
            db.session.commit()
            return redirect(url_for('manage_tryouts', unique_id=unique_id))
        except Exception as e:
            db.session.rollback()
            return f"Error creating tryout: {e}"

    return render_template_string('''
        <h1>Create a Tryout for {{ team.name }}</h1>
        <form method="post">
            Date: <input type="date" name="date" required><br>
            Location: <input type="text" name="location" required><br>
            Description: <textarea name="description"></textarea><br>
            Application Deadline: <input type="date" name="deadline" required><br>
            Registration Link: <input type="url" name="register_link"><br>
            <input type="submit" value="Create Tryout">
        </form>
        <p><a href="{{ url_for('manage_tryouts', unique_id=team.unique_id) }}">Back to Manage Tryouts</a></p>
    ''', team=team)



@app.route('/manage_tryouts/<string:unique_id>/edit_tryout/<int:tryout_id>', methods=['GET', 'POST'])
@login_required
def edit_tryout(unique_id, tryout_id):
    team = Team.query.filter_by(unique_id=unique_id).first()
    if not team:
        return "Team not found", 404

    tryout = Tryout.query.filter_by(id=tryout_id, team_id=team.id).first()
    if not tryout:
        return "Tryout not found", 404

    if request.method == 'POST':
        tryout.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        tryout.location = request.form['location']
        tryout.description = request.form['description']
        tryout.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
        tryout.register_link = request.form.get('register_link')

        try:
            db.session.commit()
            return redirect(url_for('manage_tryouts', unique_id=unique_id))
        except Exception as e:
            db.session.rollback()
            return f"Error updating tryout: {e}"

    return render_template_string('''
        <h1>Edit Tryout for {{ team.name }}</h1>
        <form method="post">
            Date: <input type="date" name="date" value="{{ tryout.date.strftime('%Y-%m-%d') }}" required><br>
            Location: <input type="text" name="location" value="{{ tryout.location }}" required><br>
            Description: <textarea name="description">{{ tryout.description }}</textarea><br>
            Application Deadline: <input type="date" name="deadline" value="{{ tryout.deadline.strftime('%Y-%m-%d') }}" required><br>
            Registration Link: <input type="url" name="register_link" value="{{ tryout.register_link }}"><br>
            <input type="submit" value="Update Tryout">
        </form>
        <p><a href="{{ url_for('manage_tryouts', unique_id=team.unique_id) }}">Back to Manage Tryouts</a></p>
    ''', team=team, tryout=tryout)


def check_application_status(tryout):
    """Check if the tryout application deadline has passed."""
    today = datetime.now()  # Keep as datetime for comparison
    return "Expired" if tryout.deadline < today else "Live"



# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
