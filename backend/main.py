# backend/main.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, func, distinct, desc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Detail, Summary
from datetime import date
# from add_routes import add_bp

# Tell Flask where to find templates and static files
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
# app.register_blueprint(add_bp)

app.secret_key = "your_secret_key_here"

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)  # This gets the absolute path to the backend/ folder
DB_PATH = os.path.join(BASE_DIR, "database", "casedb.sqlite3")  # Path to your DB file
# Database setup
engine = create_engine(f"sqlite:///database/casedb.sqlite3")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Simple Admin credentials to protect register route
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        comId = request.form['comId']
        password = request.form['password']

        user = db_session.query(User).filter_by(comId=comId, password=password).first()

        if user:
            session['user'] = comId
            return redirect(url_for('home'))
        else:
            error = "User not registered or wrong credentials."
    return render_template('login.html', error=error)


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('register'))
        else:
            return "Unauthorized Admin Access!"
    return '''
        <form method="POST">
            Admin Username: <input type="text" name="username"><br><br>
            Admin Password: <input type="password" name="password"><br><br>
            <input type="submit" value="Login as Admin">
        </form>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'admin'not in session:
        return redirect(url_for('admin_login'))

    message = None
    if request.method == 'POST':
        comId = request.form['comId']
        password = request.form['password']
        programmer = request.form['programmer']

        # Check if user already exists
        existing_user = db_session.query(User).filter_by(comId=comId).first()
        if existing_user:
            message = "User already exists!"
        else:
            new_user = User(comId=comId, password=password, programmer=programmer)
            db_session.add(new_user)
            db_session.commit()
            message = "User registered successfully!"
    return render_template('register.html', message=message)


@app.route('/add', methods=['GET', 'POST'])
def add_case():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get data posted by the form, from the form
        #.get() is used to safely get optional fields
        dateentered = request.form['date']
        region = request.form['region']
        casenum_raw = request.form.get('casenum', '').strip()
        status = request.form.get('status', '').strip()
        comments = request.form.get('comments', '').strip()
        comId = request.form['comId'].strip()

       # Validate: Either casenum or comments must be filled
        if not casenum_raw and not comments:
            #flash('Please fill either Case Number or Comments (at least one).', 'error')
            return redirect(url_for('add_case'))

        # Validate: If casenum is provided, status must also be provided
        if casenum_raw and not status:
            #flash('Please fill case status if you enter a Case Number.', 'error')
            return redirect(url_for('add_case'))
        
        # Convert casenum to int if not empty
        casenum = int(casenum_raw) if casenum_raw else None
        status = status if casenum else None  # Only accept status if casenum exists
        comments = comments if comments else '' # Set None for blank comments

        # Get user by comId
        user = db_session.query(User).filter_by(comId=comId).first()
        if not user:
            flash('Invalid user.', 'error')
            return redirect(url_for('add_case'))
        
        # Get summary
        summary = db_session.query(Summary).filter_by(date=date.fromisoformat(dateentered), region=region).first()

        # Create new case
        new_case = Detail(
            hsummary=summary.hmy if summary else None,
            date=date.fromisoformat(dateentered),
            region=region,
            casenum=casenum,
            status=status,
            comments=comments,
            userid=user.id  # Store actual user ID
        )

        db_session.add(new_case)
        db_session.commit()

        flash('Case added successfully!', 'success')
        return redirect(url_for('home'))

    # GET request — render form with user list (else part of upper code block)
    users = db_session.query(User).all()
    today = date.today().isoformat() 
    return render_template('add.html', users=users, today=today)


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    #return f"Welcome {session['user']} to Caseomatic Home!"
    comId = session['user']
    # Fetch the user to get the programmer name
    user = db_session.query(User).filter_by(comId=comId).first()
    if user:
        programmer = user.programmer
    else:
        programmer = comId  # fallback if user somehow not found

    # Fetch all details for today from the database
    today = date.today()
    details = db_session.query(Detail).filter(Detail.date == today).all()
    #details = db_session.query(Detail).filter(Detail.date == '2025-04-28').all()
    return render_template('home.html', programmer=programmer, details=details)

@app.route('/summary', methods=['GET', 'POST'])
def summary_page():
    if 'user' not in session:
        return redirect(url_for('login'))

    regions = ['APAC','ME','TA']
    rawdate = date.today()
    today = rawdate.strftime('%A - %d %b, %Y')

    if request.method == 'POST':
        for region in regions:
            # 1. Get unassigned and pending values from form
            unassigned = int(request.form.get(f"{region}_unassigned", 0))
            pending = int(request.form.get(f"{region}_pending", 0))

            # 2. Placeholders for calculated values (replace with real logic later)
            existing = calculate_existing(region, rawdate)
            assigned = calculate_assigned(region, rawdate)
            delivered = calculate_delivered(region, rawdate)
            returned = calculate_returned(region, rawdate)
            resources = calculate_resources(region, rawdate)

            # 3. Check if an entry already exists for this region & date
            existing_summary = db_session.query(Summary).filter_by(date=rawdate, region=region).first()

            if existing_summary:
                # Update existing row
                existing_summary.existing = existing
                existing_summary.assigned = assigned
                existing_summary.delivered = delivered
                existing_summary.returned = returned
                existing_summary.resources = resources
                existing_summary.unassigned = unassigned
                existing_summary.pending = pending
                summary_row = existing_summary
            else:
                # Insert new row
                new_summary = Summary(
                    date=rawdate,
                    region=region,
                    existing=existing,
                    assigned=assigned,
                    delivered=delivered,
                    returned=returned,
                    resources=resources,
                    unassigned=unassigned,
                    pending=pending
                )
                db_session.add(new_summary)
                db_session.flush()  # To generate `summary.hmy` before using it below
                summary_row = new_summary

            # 4. Update existing details in Detail table
            if region == 'APAC':
                # Update both ANZ and ASIA rows
                db_session.query(Detail).filter(
                    Detail.date == rawdate, Detail.region.in_(["ANZ", "ASIA"])
                ).update({Detail.hsummary: summary_row.hmy}, synchronize_session=False)
            else:
                db_session.query(Detail).filter_by(date=rawdate, region=region).update(
                    {Detail.hsummary: summary_row.hmy}, synchronize_session=False)

        db_session.commit()        

    # 5. Retrieve today's summary data to display
    summary_data = db_session.query(Summary).filter_by(date=rawdate).all()

    return render_template('summary.html', today=today, regions=regions, summary_data=summary_data)


# ------------------------------
# Functions - formulas
# ------------------------------
def calculate_existing(region, current_date):
    # Get the latest previous summary entry (by date) for this region
    previous_summary = (
        db_session.query(Summary)
        .filter(Summary.region == region, Summary.date < current_date)
        .order_by(desc(Summary.date))
        .first()
    )
    if previous_summary:
        return previous_summary.pending or 0
    else:
        return 0


def calculate_assigned(region, date):
    # 1. Get values using existing functions
    delivered = calculate_delivered(region, date)
    returned = calculate_returned(region, date)
    existing = calculate_existing(region, date)

    # 2. Get today's pending value from Summary (if exists)
    summary_today = (
        db_session.query(Summary).filter_by(date=date, region=region).first()
    )
    pending = summary_today.pending if summary_today else 0
    # 3. Apply formula
    assigned = delivered + returned + pending - existing
    return max(assigned, 0)  # Ensure non-negative


def calculate_delivered(region, date):
    if region == 'APAC':
        # Sum of 'Delivered' from 'ANZ' and 'ASIA' for today
        count = db_session.query(func.count()).filter(
            Detail.date == date,
            Detail.status == 'Delivered',
            Detail.region.in_(['ANZ', 'ASIA'])
        ).scalar()
    else:
        # For ME or TA, directly count for the given region
        count = db_session.query(func.count()).filter(
            Detail.date == date,
            Detail.status == 'Delivered',
            Detail.region == region
        ).scalar()
    return count or 0

def calculate_returned(region, date):
    if region == "APAC":
        # Sum of 'Returned' from 'ANZ' and 'ASIA' for today
        count = (
            db_session.query(func.count())
            .filter(
                Detail.date == date,
                Detail.status == "Returned",
                Detail.region.in_(["ANZ", "ASIA"]),
            )
            .scalar()
        )
    else:
        # For ME or TA, directly count for the given region
        count = (
            db_session.query(func.count())
            .filter(
                Detail.date == date,
                Detail.status == "Returned",
                Detail.region == region,
            )
            .scalar()
        )
    return count or 0

def calculate_resources(region, date):
        if region == 'APAC':      # Count distinct users who delivered in ANZ or ASIA
            count = db_session.query(func.count(distinct(Detail.userid))).filter(
                Detail.date == date,
                Detail.status == 'Delivered',
                Detail.region.in_(['ANZ', 'ASIA'])
                ).scalar()
        else:
        # Count distinct users who delivered in this region
            count = db_session.query(func.count(distinct(Detail.userid))).filter(
                Detail.date == date,
                Detail.status == 'Delivered',
                Detail.region == region
                ).scalar()    
        return count or 0


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
