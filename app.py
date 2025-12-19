from flask import Flask, request, render_template, redirect, url_for, session
import recommender
import db

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo'  # for sessions

# Demo "user database"
USERS = {
    'student': 'password123',
    'admin': 'admin123'
}

# Initialize DB and import phones at app startup
db.init_db()
# db.seed_phones_from_csv('data/phones.csv')


def _parse_int(value):
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_float(value):
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


@app.context_processor
def inject_current_user():
    return dict(current_user=session.get('user'))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', title="Phone Selector")


@app.route('/recommend', methods=['POST'])
def recommend_view():
    selected_prefs = request.form.getlist('preferences')

    price_max = _parse_int(request.form.get('price_max'))
    ram_min = _parse_int(request.form.get('ram_min'))
    screen_min = _parse_float(request.form.get('screen_min'))
    screen_max = _parse_float(request.form.get('screen_max'))

    # Get phones from DB
    phones_data = db.get_all_phones()

    recommended_phones = recommender.recommend(
        selected_prefs,
        phones_data,
        k=3,
        price_max=price_max,
        ram_min=ram_min,
        screen_min=screen_min,
        screen_max=screen_max
    )

    user_id = session.get('user')
    db.log_interaction(user_id, selected_prefs, recommended_phones)

    # Mapping preferences to English names for display
    pref_names = {
        'photo': 'Photography',
        'gaming': 'Gaming',
        'video': 'Video Watching',
        'social': 'Social Media & Messaging',
        'work': 'Work & Productivity',
        'budget': 'Budget Friendly'
    }
    preferences_en = [pref_names[p] for p in selected_prefs if p in pref_names]

    filters = {
        'price_max': price_max,
        'ram_min': ram_min,
        'screen_min': screen_min,
        'screen_max': screen_max
    }

    return render_template(
        'result.html',
        title="Recommendations",
        recommended=recommended_phones,
        preferences=preferences_en,
        filters=filters
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect(url_for('user_page'))
        else:
            error = "Invalid username or password"

    return render_template('login.html', title="Login", error=error)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/user', methods=['GET'])
def user_page():
    user_id = session.get('user')
    history = db.get_user_history(user_id, limit=10) if user_id else []

    return render_template(
        'user.html',
        title="User Page",
        user=user_id,
        history=history
    )


if __name__ == '__main__':
    app.run(debug=True)
