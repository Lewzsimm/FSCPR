import os
import math
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from sqlalchemy import false
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta
from cs50 import SQL
from utilFuncs import apology, login_required
from tempfile import mkdtemp


# Get today's date:
theDate = date.today()
 
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 's27d590'
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fscpr.db") #<<<<insert db file here

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure passsword was submitted
        if not request.form.get("password"):
            return apology("invalid password", 400)

        # Ensure passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation do not match", 400)

        # Ensure username not taken
        nameOnFile = db.execute("SELECT * FROM users WHERE username=?", request.form.get("username"))
        if nameOnFile:
            return apology("Sorry, that name has already been registered", 400)

        # Hash Password
        username = request.form.get("username")
        password = request.form.get("password")
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Insert into SQL Database:

        # Insert User
        username = request.form.get("username")
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        return render_template("reg_success.html")
    else: 
        return render_template("register.html")
    
@app.route("/reg_success", methods=["GET"])
@login_required
def reg_success():
    return render_template("reg_success.html")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return redirect(url_for('register'))
    else:
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Username and Password match was unsuccessful", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return render_template("logged_in.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
    
@app.route("/logged_in", methods=["GET"])
@login_required
def logged_in():
    return render_template("logged_in.html")


@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    if request.method == "POST":
        return redirect(url_for('apology')) #change it to whatever...
    else:
        return render_template("main.html")
    
@app.route("/update_success", methods=["GET"])
@login_required
def update_success():
    return render_template("update_success.html")

@app.route("/cooler", methods=["GET", "POST"])
@login_required
def cooler():
    if request.method == "POST":
        session['cooler_choice'] = request.form.get("cooler_id")
        choice = session.get("cooler_choice")
        if choice == None:
            return redirect(url_for('cooler'))
        
        # Get the chosen cooler, the items inside, and the shelves they belong to
        items = db.execute("SELECT * FROM cooler WHERE cooler_unit=? ORDER BY shelf, name", choice)
        my_shelf = db.execute("SELECT DISTINCT shelf FROM cooler WHERE ?=cooler_unit ORDER BY shelf", choice)
        
        # Date conversions - related companions below
        theDate = []
        theDate.append(date.today())
        date_plus4 = theDate[0] + timedelta(days=4)
        date_plus3 = theDate[0] + timedelta(days=3)
        date_plus2 = theDate[0] + timedelta(days=2)
        date_plus1 = theDate[0] + timedelta(days=1)
        
        # Get Prep flags
        prep_flags = db.execute("SELECT prep_flag FROM cooler WHERE cooler_unit=? ORDER BY shelf", choice)
        
        # Get Expiry
        the_expiry_date = []
        get_expiry = db.execute("SELECT expiry FROM cooler WHERE cooler_unit=? ORDER BY shelf", choice)
        get_exp_flag = db.execute("SELECT exp_flag FROM cooler WHERE cooler_unit=? ORDER BY shelf", choice)
        
        i = 0
        for get_expiry in get_expiry:
            # Put expiry in array, convert to string(because Flask doesn't like to operate on datetime values)
            the_expiry_date.append(datetime.strptime(get_expiry["expiry"], "%Y/%m/%d").date())         
            expiry_str = the_expiry_date[i].strftime('%Y/%m/%d')
            
            # Date conversions to str, related companions above
            theDate_str = theDate[0].strftime('%Y/%m/%d')
            date_plus4_str = date_plus4.strftime('%Y/%m/%d')
            date_plus3_str = date_plus3.strftime('%Y/%m/%d')
            date_plus2_str = date_plus2.strftime('%Y/%m/%d')
            date_plus1_str = date_plus1.strftime('%Y/%m/%d')
            
            # Update Flags
            exp_flags = []
            if expiry_str == date_plus3_str:
                db.execute("UPDATE cooler SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus2_str:
                db.execute("UPDATE cooler SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus1_str:
                db.execute("UPDATE cooler SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            elif expiry_str == theDate_str:
                db.execute("UPDATE cooler SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(False)
                
            if expiry_str <= theDate_str:
                db.execute("UPDATE cooler SET exp_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            elif expiry_str > date_plus4_str:
                db.execute("UPDATE cooler SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                db.execute("UPDATE cooler SET exp_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            i = i + 1
        
        return render_template('cooler_content.html', choice=choice, items=items, my_shelf=my_shelf, theDate=theDate, the_expiry_date=the_expiry_date, exp_flags=exp_flags, prep_flags=prep_flags)
        
    else:
        coolers_all = db.execute("SELECT * FROM cooler")
        coolers_db = db.execute("SELECT DISTINCT cooler_unit FROM cooler")
        return render_template('cooler.html', coolers=coolers_db, coolers_all=coolers_all)
    
    
@app.route("/cooler_content", methods=["GET", "POST"])
@login_required
def cooler_content():
    if request.method == "POST":
        session['cooler_choice'] = request.form.get("cooler_id")
        choice = session.get('cooler_choice')
        items = db.execute("SELECT * FROM cooler WHERE ?=cooler_unit ORDER BY shelf", choice)       
        return render_template('cooler_content.html', choice=choice, items=items)
    else:
        choice = session.get('cooler_choice')
        items = db.execute("SELECT * FROM cooler WHERE ?=cooler_unit ORDER BY shelf", choice)       
        return render_template('cooler_content.html', choice=choice, items=items)
    

@app.route("/cooler_content_update", methods=["GET", "POST"])
@login_required
def cooler_content_update():
    if request.method == "POST":
        id_to_name = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])
        choice = session.get('cooler_choice')

        items = db.execute("SELECT * FROM cooler WHERE ?=cooler_unit ORDER BY shelf, name", choice)
        id_f = request.form.getlist("id") 
        shelf_f = request.form.getlist("shelf") 
        production_f = request.form.getlist("production")
        expiry_f = request.form.getlist("expiry") 
        portions_f = request.form.getlist("portions") 
        batches_f = request.form.getlist("batches") 
        batch_size_f = request.form.getlist("batch_size") 
        flag_f = request.form.getlist("flag__prep") 
        delete_f = request.form.getlist("delete") 

        shelf_n = request.form.getlist("shelf_new")
        name_n = request.form.getlist('name_new')
        brand_n = request.form.getlist('brand_new')
        production_n = request.form.getlist('production_new')
        date_n = request.form.getlist('date_new')
        portions_n = request.form.getlist('portions_new')
        batches_n = request.form.getlist('batches_new')
        batch_size_n = request.form.getlist('batch_size_new')
        select_n = request.form.getlist('select_new')
        
        
# Update Form Fields
        
        i = 0
        k = 0
        for id_f in items: 
            if items[i]["shelf"] != int(shelf_f[i]):
                db.execute("UPDATE cooler SET shelf=? WHERE id=? AND cooler_unit=?", shelf_f[i], id_f['id'], choice)                  
                db.execute("UPDATE cooler SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE cooler SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                
        # Production has to get the value from the form's date object if present, iterate over it to convert "-" to "/",
        # and then make a variable with the converted value for uploading to the database, due to how strftime functions    
            if production_f[i]:
                production_f_target = production_f[i]
                j = 0
                converter_production_date_f = []
                for element in production_f[i]:
                    if production_f_target[j] == "-":
                        converter_production_date_f.append("/")
                    else:
                        converter_production_date_f.append(production_f_target[j])
                    j = j + 1
                converted_production_date_f = ''.join(map(str, converter_production_date_f))
                db.execute("UPDATE cooler SET production=? WHERE id=? AND cooler_unit=?", converted_production_date_f, id_f['id'], choice)
                
                db.execute("UPDATE cooler SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE cooler SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                
        # Expiry has to get the value from the form's date object if present, iterate over it to convert "-" to "/",
        # and then make a variable with the converted value for uploading to the database, due to how strftime functions    
            if expiry_f[i]:
                expiry_f_target = expiry_f[i]
                j = 0
                converter_date_f = []
                for element in expiry_f[i]:
                    if expiry_f_target[j] == "-":
                        converter_date_f.append("/")
                    else:
                        converter_date_f.append(expiry_f_target[j])
                    j = j + 1
                converted_date_f = ''.join(map(str, converter_date_f))
                db.execute("UPDATE cooler SET expiry=? WHERE id=? AND cooler_unit=?", converted_date_f, id_f['id'], choice)
                
                db.execute("UPDATE cooler SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE cooler SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
            
            if items[i]["num_portions"] != float(portions_f[i]):
                db.execute("UPDATE cooler SET num_portions=? WHERE id=? AND cooler_unit=?", portions_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE cooler SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                
                db.execute("UPDATE cooler SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)             
                db.execute("UPDATE cooler SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                
            if items[i]["num_batches"] != float(batches_f[i]):
                db.execute("UPDATE cooler SET num_batches=? WHERE id=? AND cooler_unit=?", batches_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE cooler SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                
                db.execute("UPDATE cooler SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)            
                db.execute("UPDATE cooler SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)    
                                 
            if items[i]["batch_size"] != float(batch_size_f[i]):
                db.execute("UPDATE cooler SET batch_size=? WHERE id=? AND cooler_unit=?", batch_size_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE cooler SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                  
                db.execute("UPDATE cooler SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)             
                db.execute("UPDATE cooler SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                                  
            if items[i]["prep_flag"] != flag_f[i]:
                db.execute("UPDATE cooler SET prep_flag=? WHERE id=? AND cooler_unit=?", flag_f[i], id_f['id'], choice)   
                
                db.execute("UPDATE cooler SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE cooler SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)  
                                
            if delete_f[i] == "yes":
                db.execute("DELETE FROM cooler WHERE id=? AND cooler_unit=?", id_f['id'], choice)                      
                db.execute("UPDATE cooler SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE cooler SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)
            i = i + 1
                
            
# Add New Items

        k = 0
        for shelf_n[k] in shelf_n:
            if shelf_n:
                # try this next: 
                print(shelf_n[k], "iterate shelf")
                
                # Hack the production date
                if production_n:
                    production_n_target = production_n[k]
                    j = 0
                    converter_production_date_n = []
                    for element in production_n[k]:
                        if production_n_target[j] == "-":
                            converter_production_date_n.append("/")
                        else:
                            converter_production_date_n.append(production_n_target[j])
                        j = j + 1
                    converted_production_date_n = ''.join(map(str, converter_production_date_n))
                    
                # Hack the exp date
                if date_n:
                    date_n_target = date_n[k]
                    j = 0
                    converter_date_n = []
                    for element in date_n[k]:
                        if date_n_target[j] == "-":
                            converter_date_n.append("/")
                        else:
                            converter_date_n.append(date_n_target[j])
                        j = j + 1
                    converted_date_n = ''.join(map(str, converter_date_n))

                # Get Total Portions
                portions_total_n = float(portions_n[k]) + (float(batches_n[k])*float(batch_size_n[k]))
                
                db.execute("INSERT INTO cooler (cooler_unit, shelf, name, brand, production, expiry, num_portions, num_batches, batch_size, portions_total, prep_flag, updated_on, updated_by) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", choice, shelf_n[k], name_n[k], brand_n[k], converted_production_date_n, converted_date_n, portions_n[k], batches_n[k], batch_size_n[k], portions_total_n, select_n[k], date.today(), id_to_name[0]['username'])
            k = k + 1
                
        return render_template('update_success.html', choice=choice, items=items)
    else:
        choice = session.get("cooler_choice")
        
        # Get the chosen cooler, the items inside, and the shelves they belong to
        items = db.execute("SELECT * FROM cooler WHERE cooler_unit=? ORDER BY name", choice)
        my_shelf = db.execute("SELECT DISTINCT shelf FROM cooler WHERE ?=cooler_unit ORDER BY shelf", choice)
        
        # Date conversions - related companions below
        theDate = []
        theDate.append(date.today())
        date_plus4 = theDate[0] + timedelta(days=4)
        date_plus3 = theDate[0] + timedelta(days=3)
        date_plus2 = theDate[0] + timedelta(days=2)
        date_plus1 = theDate[0] + timedelta(days=1)
        
        
        # Get Prep flags
        prep_flags = db.execute("SELECT prep_flag FROM cooler WHERE cooler_unit=? ORDER BY shelf", choice)
        
        # Get Expiry
        the_expiry_date = []
        get_expiry = db.execute("SELECT expiry FROM cooler WHERE cooler_unit=? ORDER BY shelf", choice)
        get_exp_flag = db.execute("SELECT exp_flag FROM cooler WHERE cooler_unit=? ORDER BY shelf", choice)
        
        i = 0
        for get_expiry in get_expiry:
            # Put expiry in array, convert to string(because Flask doesn't like to operate on datetime values)
            the_expiry_date.append(datetime.strptime(get_expiry["expiry"], "%Y/%m/%d").date())         
            expiry_str = the_expiry_date[i].strftime('%Y/%m/%d')
            
            # Date conversions to str, related companions above
            theDate_str = theDate[0].strftime('%Y/%m/%d')
            date_plus4_str = date_plus4.strftime('%Y/%m/%d')
            date_plus3_str = date_plus3.strftime('%Y/%m/%d')
            date_plus2_str = date_plus2.strftime('%Y/%m/%d')
            date_plus1_str = date_plus1.strftime('%Y/%m/%d')
            
            # Update Flags
            exp_flags = []
            if expiry_str == date_plus3_str:
                db.execute("UPDATE cooler SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus2_str:
                db.execute("UPDATE cooler SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus1_str:
                db.execute("UPDATE cooler SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            elif expiry_str == theDate_str:
                db.execute("UPDATE cooler SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(False)
                
            if expiry_str <= theDate_str:
                db.execute("UPDATE cooler SET exp_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            elif expiry_str > date_plus4_str:
                db.execute("UPDATE cooler SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                db.execute("UPDATE cooler SET exp_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            i = i + 1
        
        return render_template('cooler_content_update.html', choice=choice, items=items, my_shelf=my_shelf, theDate=theDate, the_expiry_date=the_expiry_date, exp_flags=exp_flags, prep_flags=prep_flags)


@app.route("/freezer", methods=["GET", "POST"])
@login_required
def freezer():
    if request.method == "POST":
        session['cooler_choice'] = request.form.get("cooler_id")
        choice = session.get("cooler_choice")
        if choice == None:
            return redirect(url_for('freezer'))
        
        # Get the chosen cooler, the items inside, and the shelves they belong to
        items = db.execute("SELECT * FROM freezer WHERE cooler_unit=? ORDER BY shelf, name", choice)
        my_shelf = db.execute("SELECT DISTINCT shelf FROM freezer WHERE ?=cooler_unit ORDER BY shelf", choice)
        
        # Date conversions - related companions below
        theDate = []
        theDate.append(date.today())
        date_plus4 = theDate[0] + timedelta(days=4)
        date_plus3 = theDate[0] + timedelta(days=3)
        date_plus2 = theDate[0] + timedelta(days=2)
        date_plus1 = theDate[0] + timedelta(days=1)
        
        # Get Prep flags
        prep_flags = db.execute("SELECT prep_flag FROM freezer WHERE cooler_unit=? ORDER BY shelf", choice)
        
        # Get Expiry
        the_expiry_date = []
        get_expiry = db.execute("SELECT expiry FROM freezer WHERE cooler_unit=? ORDER BY shelf", choice)
        get_exp_flag = db.execute("SELECT exp_flag FROM freezer WHERE cooler_unit=? ORDER BY shelf", choice)
        
        i = 0
        for get_expiry in get_expiry:
            # Put expiry in array, convert to string(because Flask doesn't like to operate on datetime values)
            the_expiry_date.append(datetime.strptime(get_expiry["expiry"], "%Y/%m/%d").date())         
            expiry_str = the_expiry_date[i].strftime('%Y/%m/%d')
            
            # Date conversions to str, related companions above
            theDate_str = theDate[0].strftime('%Y/%m/%d')
            date_plus4_str = date_plus4.strftime('%Y/%m/%d')
            date_plus3_str = date_plus3.strftime('%Y/%m/%d')
            date_plus2_str = date_plus2.strftime('%Y/%m/%d')
            date_plus1_str = date_plus1.strftime('%Y/%m/%d')
            
            # Update Flags
            exp_flags = []
            if expiry_str == date_plus3_str:
                db.execute("UPDATE freezer SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus2_str:
                db.execute("UPDATE freezer SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus1_str:
                db.execute("UPDATE freezer SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            elif expiry_str == theDate_str:
                db.execute("UPDATE freezer SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(False)
                
            if expiry_str <= theDate_str:
                db.execute("UPDATE freezer SET exp_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            elif expiry_str > date_plus4_str:
                db.execute("UPDATE freezer SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                db.execute("UPDATE freezer SET exp_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            i = i + 1
        
        return render_template('freezer_content.html', choice=choice, items=items, my_shelf=my_shelf, theDate=theDate, the_expiry_date=the_expiry_date, exp_flags=exp_flags, prep_flags=prep_flags)
        
    else:
        coolers_all = db.execute("SELECT * FROM freezer")
        coolers_db = db.execute("SELECT DISTINCT cooler_unit FROM freezer")
        return render_template('freezer.html', coolers=coolers_db, coolers_all=coolers_all)


@app.route("/freezer_content", methods=["GET", "POST"])
@login_required
def freezer_content():
    if request.method == "POST":
        session['cooler_choice'] = request.form.get("cooler_id")
        choice = session.get('cooler_choice')
        items = db.execute("SELECT * FROM freezer WHERE ?=cooler_unit ORDER BY shelf", choice)       
        return render_template('freezer_content.html', choice=choice, items=items)
    else:
        choice = session.get('cooler_choice')
        items = db.execute("SELECT * FROM freezer WHERE ?=cooler_unit ORDER BY shelf", choice)       
        return render_template('freezer_content.html', choice=choice, items=items)


@app.route("/freezer_content_update", methods=["GET", "POST"])
@login_required
def freezer_content_update():
    if request.method == "POST":
        id_to_name = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])
        choice = session.get('cooler_choice')

        items = db.execute("SELECT * FROM freezer WHERE ?=cooler_unit ORDER BY shelf, name", choice)
        id_f = request.form.getlist("id") 
        shelf_f = request.form.getlist("shelf") 
        production_f = request.form.getlist("production")
        expiry_f = request.form.getlist("expiry") 
        portions_f = request.form.getlist("portions") 
        batches_f = request.form.getlist("batches") 
        batch_size_f = request.form.getlist("batch_size") 
        flag_f = request.form.getlist("flag__prep") 
        delete_f = request.form.getlist("delete") 

        shelf_n = request.form.getlist("shelf_new")
        name_n = request.form.getlist('name_new')
        brand_n = request.form.getlist('brand_new')
        production_n = request.form.getlist('production_new')
        date_n = request.form.getlist('date_new')
        portions_n = request.form.getlist('portions_new')
        batches_n = request.form.getlist('batches_new')
        batch_size_n = request.form.getlist('batch_size_new')
        select_n = request.form.getlist('select_new')
        
        
# Update Form Fields
        
        i = 0
        k = 0
        for id_f in items: 
            if items[i]["shelf"] != int(shelf_f[i]):
                db.execute("UPDATE freezer SET shelf=? WHERE id=? AND cooler_unit=?", shelf_f[i], id_f['id'], choice)                  
                db.execute("UPDATE freezer SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE freezer SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)
                 
        # Production has to get the value from the form's date object if present, iterate over it to convert "-" to "/",
        # and then make a variable with the converted value for uploading to the database, due to how strftime functions    
            if production_f[i]:
                production_f_target = production_f[i]
                j = 0
                converter_production_date_f = []
                for element in production_f[i]:
                    if production_f_target[j] == "-":
                        converter_production_date_f.append("/")
                    else:
                        converter_production_date_f.append(production_f_target[j])
                    j = j + 1
                converted_production_date_f = ''.join(map(str, converter_production_date_f))
                db.execute("UPDATE freezer SET production=? WHERE id=? AND cooler_unit=?", converted_production_date_f, id_f['id'], choice)
                
                db.execute("UPDATE freezer SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE freezer SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                
        # Expiry has to get the value from the form's date object if present, iterate over it to convert "-" to "/",
        # and then make a variable with the converted value for uploading to the database, due to how strftime functions    
            if expiry_f[i]:
                expiry_f_target = expiry_f[i]
                j = 0
                converter_date_f = []
                for element in expiry_f[i]:
                    if expiry_f_target[j] == "-":
                        converter_date_f.append("/")
                    else:
                        converter_date_f.append(expiry_f_target[j])
                    j = j + 1
                converted_date_f = ''.join(map(str, converter_date_f))
                db.execute("UPDATE freezer SET expiry=? WHERE id=? AND cooler_unit=?", converted_date_f, id_f['id'], choice)
                
                db.execute("UPDATE freezer SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE freezer SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
            
            if items[i]["num_portions"] != float(portions_f[i]):
                db.execute("UPDATE freezer SET num_portions=? WHERE id=? AND cooler_unit=?", portions_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE freezer SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                
                db.execute("UPDATE freezer SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)             
                db.execute("UPDATE freezer SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                
            if items[i]["num_batches"] != float(batches_f[i]):
                db.execute("UPDATE freezer SET num_batches=? WHERE id=? AND cooler_unit=?", batches_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE freezer SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                
                db.execute("UPDATE freezer SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)            
                db.execute("UPDATE freezer SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)    
                                 
            if items[i]["batch_size"] != float(batch_size_f[i]):
                db.execute("UPDATE freezer SET batch_size=? WHERE id=? AND cooler_unit=?", batch_size_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE freezer SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                  
                db.execute("UPDATE freezer SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)             
                db.execute("UPDATE freezer SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                                  
            if items[i]["prep_flag"] != flag_f[i]:
                db.execute("UPDATE freezer SET prep_flag=? WHERE id=? AND cooler_unit=?", flag_f[i], id_f['id'], choice)   
                
                db.execute("UPDATE freezer SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE freezer SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)  
                                
            if delete_f[i] == "yes":
                db.execute("DELETE FROM freezer WHERE id=? AND cooler_unit=?", id_f['id'], choice)                      
                db.execute("UPDATE freezer SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE freezer SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)
            i = i + 1
                
            
# Add New Items

        k = 0
        for shelf_n[k] in shelf_n:
            if shelf_n:
                
                # Hack the production date
                if production_n:
                    production_n_target = production_n[k]
                    j = 0
                    converter_production_date_n = []
                    for element in production_n[k]:
                        if production_n_target[j] == "-":
                            converter_production_date_n.append("/")
                        else:
                            converter_production_date_n.append(production_n_target[j])
                        j = j + 1
                    converted_production_date_n = ''.join(map(str, converter_production_date_n))
                 
                # Hack the date
                if date_n:
                    date_n_target = date_n[k]
                    j = 0
                    converter_date_n = []
                    for element in date_n[k]:
                        if date_n_target[j] == "-":
                            converter_date_n.append("/")
                        else:
                            converter_date_n.append(date_n_target[j])
                        j = j + 1
                    converted_date_n = ''.join(map(str, converter_date_n))

                # Get Total Portions
                portions_total_n = float(portions_n[k]) + (float(batches_n[k])*float(batch_size_n[k]))
                
                db.execute("INSERT INTO freezer (cooler_unit, shelf, name, brand, production, expiry, num_portions, num_batches, batch_size, portions_total, prep_flag, updated_on, updated_by) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", choice, shelf_n[k], name_n[k], brand_n[k], converted_production_date_n, converted_date_n, portions_n[k], batches_n[k], batch_size_n[k], portions_total_n, select_n[k], date.today(), id_to_name[0]['username'])
            k = k + 1
                
        return render_template('update_success.html', choice=choice, items=items)
    else:
        choice = session.get("cooler_choice")
        
        # Get the chosen cooler, the items inside, and the shelves they belong to
        items = db.execute("SELECT * FROM freezer WHERE cooler_unit=? ORDER BY name", choice)
        my_shelf = db.execute("SELECT DISTINCT shelf FROM freezer WHERE ?=cooler_unit ORDER BY shelf", choice)
        
        # Date conversions - related companions below
        theDate = []
        theDate.append(date.today())
        date_plus4 = theDate[0] + timedelta(days=4)
        date_plus3 = theDate[0] + timedelta(days=3)
        date_plus2 = theDate[0] + timedelta(days=2)
        date_plus1 = theDate[0] + timedelta(days=1)
        
        
        # Get Prep flags
        prep_flags = db.execute("SELECT prep_flag FROM freezer WHERE cooler_unit=? ORDER BY shelf", choice)
        
        # Get Expiry
        the_expiry_date = []
        get_expiry = db.execute("SELECT expiry FROM freezer WHERE cooler_unit=? ORDER BY shelf", choice)
        get_exp_flag = db.execute("SELECT exp_flag FROM freezer WHERE cooler_unit=? ORDER BY shelf", choice)
        
        i = 0
        for get_expiry in get_expiry:
            # Put expiry in array, convert to string(because Flask doesn't like to operate on datetime values)
            the_expiry_date.append(datetime.strptime(get_expiry["expiry"], "%Y/%m/%d").date())         
            expiry_str = the_expiry_date[i].strftime('%Y/%m/%d')
            
            # Date conversions to str, related companions above
            theDate_str = theDate[0].strftime('%Y/%m/%d')
            date_plus4_str = date_plus4.strftime('%Y/%m/%d')
            date_plus3_str = date_plus3.strftime('%Y/%m/%d')
            date_plus2_str = date_plus2.strftime('%Y/%m/%d')
            date_plus1_str = date_plus1.strftime('%Y/%m/%d')
            
            # Update Flags
            exp_flags = []
            if expiry_str == date_plus3_str:
                db.execute("UPDATE freezer SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus2_str:
                db.execute("UPDATE freezer SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus1_str:
                db.execute("UPDATE freezer SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            elif expiry_str == theDate_str:
                db.execute("UPDATE freezer SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(False)
                
            if expiry_str <= theDate_str:
                db.execute("UPDATE freezer SET exp_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            elif expiry_str > date_plus4_str:
                db.execute("UPDATE freezer SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                db.execute("UPDATE freezer SET exp_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            i = i + 1
        
        return render_template('freezer_content_update.html', choice=choice, items=items, my_shelf=my_shelf, theDate=theDate, the_expiry_date=the_expiry_date, exp_flags=exp_flags, prep_flags=prep_flags)


@app.route("/dry", methods=["GET", "POST"])
@login_required
def dry():
    if request.method == "POST":
        session['cooler_choice'] = request.form.get("cooler_id")
        choice = session.get("cooler_choice")
        if choice == None:
            return redirect(url_for('dry'))
        
        # Get the chosen cooler, the items inside, and the shelves they belong to
        items = db.execute("SELECT * FROM dry WHERE cooler_unit=? ORDER BY shelf, name", choice)
        my_shelf = db.execute("SELECT DISTINCT shelf FROM dry WHERE ?=cooler_unit ORDER BY shelf", choice)
        
        # Date conversions - related companions below
        theDate = []
        theDate.append(date.today())
        date_plus4 = theDate[0] + timedelta(days=4)
        date_plus3 = theDate[0] + timedelta(days=3)
        date_plus2 = theDate[0] + timedelta(days=2)
        date_plus1 = theDate[0] + timedelta(days=1)
        
        # Get Prep flags
        prep_flags = db.execute("SELECT prep_flag FROM dry WHERE cooler_unit=? ORDER BY shelf", choice)
        
        # Get Expiry
        the_expiry_date = []
        get_expiry = db.execute("SELECT expiry FROM dry WHERE cooler_unit=? ORDER BY shelf", choice)
        get_exp_flag = db.execute("SELECT exp_flag FROM dry WHERE cooler_unit=? ORDER BY shelf", choice)
        
        i = 0
        for get_expiry in get_expiry:
            # Put expiry in array, convert to string(because Flask doesn't like to operate on datetime values)
            the_expiry_date.append(datetime.strptime(get_expiry["expiry"], "%Y/%m/%d").date())         
            expiry_str = the_expiry_date[i].strftime('%Y/%m/%d')
            
            # Date conversions to str, related companions above
            theDate_str = theDate[0].strftime('%Y/%m/%d')
            date_plus4_str = date_plus4.strftime('%Y/%m/%d')
            date_plus3_str = date_plus3.strftime('%Y/%m/%d')
            date_plus2_str = date_plus2.strftime('%Y/%m/%d')
            date_plus1_str = date_plus1.strftime('%Y/%m/%d')
            
            # Update Flags
            exp_flags = []
            if expiry_str == date_plus3_str:
                db.execute("UPDATE dry SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus2_str:
                db.execute("UPDATE dry SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus1_str:
                db.execute("UPDATE dry SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            elif expiry_str == theDate_str:
                db.execute("UPDATE dry SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(False)
                
            if expiry_str <= theDate_str:
                db.execute("UPDATE dry SET exp_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            elif expiry_str > date_plus4_str:
                db.execute("UPDATE dry SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                db.execute("UPDATE dry SET exp_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            i = i + 1
        
        return render_template('dry_content.html', choice=choice, items=items, my_shelf=my_shelf, theDate=theDate, the_expiry_date=the_expiry_date, exp_flags=exp_flags, prep_flags=prep_flags)
        
    else:
        coolers_all = db.execute("SELECT * FROM dry")
        coolers_db = db.execute("SELECT DISTINCT cooler_unit FROM dry")
        return render_template('dry.html', coolers=coolers_db, coolers_all=coolers_all)


@app.route("/dry_content", methods=["GET", "POST"])
@login_required
def dry_content():
    if request.method == "POST":
        session['cooler_choice'] = request.form.get("cooler_id")
        choice = session.get('cooler_choice')
        items = db.execute("SELECT * FROM dry WHERE ?=cooler_unit ORDER BY shelf", choice)       
        return render_template('dry_content.html', choice=choice, items=items)
    else:
        choice = session.get('cooler_choice')
        items = db.execute("SELECT * FROM dry WHERE ?=cooler_unit ORDER BY shelf", choice)       
        return render_template('dry_content.html', choice=choice, items=items)


@app.route("/dry_content_update", methods=["GET", "POST"])
@login_required
def dry_content_update():
    if request.method == "POST":
        id_to_name = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])
        choice = session.get('cooler_choice')

        items = db.execute("SELECT * FROM dry WHERE ?=cooler_unit ORDER BY shelf, name", choice)
        id_f = request.form.getlist("id") 
        shelf_f = request.form.getlist("shelf") 
        production_f = request.form.getlist("production") 
        expiry_f = request.form.getlist("expiry") 
        portions_f = request.form.getlist("portions") 
        batches_f = request.form.getlist("batches") 
        batch_size_f = request.form.getlist("batch_size") 
        flag_f = request.form.getlist("flag__prep") 
        delete_f = request.form.getlist("delete") 

        shelf_n = request.form.getlist("shelf_new")
        name_n = request.form.getlist('name_new')
        brand_n = request.form.getlist('brand_new')
        production_n = request.form.getlist('production_new')
        date_n = request.form.getlist('date_new')
        portions_n = request.form.getlist('portions_new')
        batches_n = request.form.getlist('batches_new')
        batch_size_n = request.form.getlist('batch_size_new')
        select_n = request.form.getlist('select_new')
        
# Update Form Fields
        
        i = 0
        k = 0
        for id_f in items: 
            if items[i]["shelf"] != int(shelf_f[i]):
                db.execute("UPDATE dry SET shelf=? WHERE id=? AND cooler_unit=?", shelf_f[i], id_f['id'], choice)                  
                db.execute("UPDATE dry SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE dry SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                
        # Production has to get the value from the form's date object if present, iterate over it to convert "-" to "/",
        # and then make a variable with the converted value for uploading to the database, due to how strftime functions    
            if production_f[i]:
                production_f_target = production_f[i]
                j = 0
                converter_production_date_f = []
                for element in production_f[i]:
                    if production_f_target[j] == "-":
                        converter_production_date_f.append("/")
                    else:
                        converter_production_date_f.append(production_f_target[j])
                    j = j + 1
                converted_production_date_f = ''.join(map(str, converter_production_date_f))
                db.execute("UPDATE dry SET production=? WHERE id=? AND cooler_unit=?", converted_production_date_f, id_f['id'], choice)
                
                db.execute("UPDATE dry SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE dry SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                
        # Expiry has to get the value from the form's date object if present, iterate over it to convert "-" to "/",
        # and then make a variable with the converted value for uploading to the database, due to how strftime functions    
            if expiry_f[i]:
                expiry_f_target = expiry_f[i]
                j = 0
                converter_date_f = []
                for element in expiry_f[i]:
                    if expiry_f_target[j] == "-":
                        converter_date_f.append("/")
                    else:
                        converter_date_f.append(expiry_f_target[j])
                    j = j + 1
                converted_date_f = ''.join(map(str, converter_date_f))
                db.execute("UPDATE dry SET expiry=? WHERE id=? AND cooler_unit=?", converted_date_f, id_f['id'], choice)
                
                db.execute("UPDATE dry SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE dry SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
            
            if items[i]["num_portions"] != float(portions_f[i]):
                db.execute("UPDATE dry SET num_portions=? WHERE id=? AND cooler_unit=?", portions_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE dry SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                
                db.execute("UPDATE dry SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)             
                db.execute("UPDATE dry SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                
            if items[i]["num_batches"] != float(batches_f[i]):
                db.execute("UPDATE dry SET num_batches=? WHERE id=? AND cooler_unit=?", batches_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE dry SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                
                db.execute("UPDATE dry SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)            
                db.execute("UPDATE dry SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)    
                                 
            if items[i]["batch_size"] != float(batch_size_f[i]):
                db.execute("UPDATE dry SET batch_size=? WHERE id=? AND cooler_unit=?", batch_size_f[i], id_f['id'], choice)
                total_math = float(portions_f[i]) + (float(batches_f[i]) * float(batch_size_f[i])) 
                db.execute("UPDATE dry SET portions_total=? WHERE id=? AND cooler_unit=?", total_math, id_f['id'], choice) 
                  
                db.execute("UPDATE dry SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)             
                db.execute("UPDATE dry SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice) 
                                  
            if items[i]["prep_flag"] != flag_f[i]:
                db.execute("UPDATE dry SET prep_flag=? WHERE id=? AND cooler_unit=?", flag_f[i], id_f['id'], choice)   
                
                db.execute("UPDATE dry SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE dry SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)  
                                
            if delete_f[i] == "yes":
                db.execute("DELETE FROM dry WHERE id=? AND cooler_unit=?", id_f['id'], choice)                      
                db.execute("UPDATE dry SET updated_by=? WHERE id=? AND cooler_unit=?", id_to_name[0]['username'], id_f['id'], choice)              
                db.execute("UPDATE dry SET updated_on=? WHERE id=? AND cooler_unit=?", date.today(), id_f['id'], choice)
            i = i + 1
                
            
# Add New Items

        k = 0
        for shelf_n[k] in shelf_n:
            if shelf_n:
                
                # Hack the production date
                if production_n:
                    production_n_target = production_n[k]
                    j = 0
                    converter_production_date_n = []
                    for element in production_n[k]:
                        if production_n_target[j] == "-":
                            converter_production_date_n.append("/")
                        else:
                            converter_production_date_n.append(production_n_target[j])
                        j = j + 1
                    converted_production_date_n = ''.join(map(str, converter_production_date_n))
    
                # Hack the date
                if date_n:
                    date_n_target = date_n[k]
                    j = 0
                    converter_date_n = []
                    for element in date_n[k]:
                        if date_n_target[j] == "-":
                            converter_date_n.append("/")
                        else:
                            converter_date_n.append(date_n_target[j])
                        j = j + 1
                    converted_date_n = ''.join(map(str, converter_date_n))

                # Get Total Portions
                portions_total_n = float(portions_n[k]) + (float(batches_n[k])*float(batch_size_n[k]))
                
                db.execute("INSERT INTO dry (cooler_unit, shelf, name, brand, production, expiry, num_portions, num_batches, batch_size, portions_total, prep_flag, updated_on, updated_by) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", choice, shelf_n[k], name_n[k], brand_n[k], converted_production_date_n, converted_date_n, portions_n[k], batches_n[k], batch_size_n[k], portions_total_n, select_n[k], date.today(), id_to_name[0]['username'])
            k = k + 1
                
        return render_template('update_success.html', choice=choice, items=items)
    else:
        choice = session.get("cooler_choice")
        
        # Get the chosen cooler, the items inside, and the shelves they belong to
        items = db.execute("SELECT * FROM dry WHERE cooler_unit=? ORDER BY name", choice)
        my_shelf = db.execute("SELECT DISTINCT shelf FROM dry WHERE ?=cooler_unit ORDER BY shelf", choice)
        
        # Date conversions - related companions below
        theDate = []
        theDate.append(date.today())
        date_plus4 = theDate[0] + timedelta(days=4)
        date_plus3 = theDate[0] + timedelta(days=3)
        date_plus2 = theDate[0] + timedelta(days=2)
        date_plus1 = theDate[0] + timedelta(days=1)
        
        
        # Get Prep flags
        prep_flags = db.execute("SELECT prep_flag FROM dry WHERE cooler_unit=? ORDER BY shelf", choice)
        
        # Get Expiry
        the_expiry_date = []
        get_expiry = db.execute("SELECT expiry FROM dry WHERE cooler_unit=? ORDER BY shelf", choice)
        get_exp_flag = db.execute("SELECT exp_flag FROM dry WHERE cooler_unit=? ORDER BY shelf", choice)
        
        i = 0
        for get_expiry in get_expiry:
            # Put expiry in array, convert to string(because Flask doesn't like to operate on datetime values)
            the_expiry_date.append(datetime.strptime(get_expiry["expiry"], "%Y/%m/%d").date())         
            expiry_str = the_expiry_date[i].strftime('%Y/%m/%d')
            
            # Date conversions to str, related companions above
            theDate_str = theDate[0].strftime('%Y/%m/%d')
            date_plus4_str = date_plus4.strftime('%Y/%m/%d')
            date_plus3_str = date_plus3.strftime('%Y/%m/%d')
            date_plus2_str = date_plus2.strftime('%Y/%m/%d')
            date_plus1_str = date_plus1.strftime('%Y/%m/%d')
            
            # Update Flags
            exp_flags = []
            if expiry_str == date_plus3_str:
                db.execute("UPDATE dry SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus2_str:
                db.execute("UPDATE dry SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            if expiry_str == date_plus1_str:
                db.execute("UPDATE dry SET age_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            elif expiry_str == theDate_str:
                db.execute("UPDATE dry SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(False)
                
            if expiry_str <= theDate_str:
                db.execute("UPDATE dry SET exp_flag='True' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
                
            elif expiry_str > date_plus4_str:
                db.execute("UPDATE dry SET age_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                db.execute("UPDATE dry SET exp_flag='False' WHERE expiry=? AND cooler_unit=?", expiry_str, choice)
                exp_flags.append(True)
            i = i + 1
        
        return render_template('dry_content_update.html', choice=choice, items=items, my_shelf=my_shelf, theDate=theDate, the_expiry_date=the_expiry_date, exp_flags=exp_flags, prep_flags=prep_flags)


@app.route("/prep", methods=["GET"])
@login_required
def prep():
        cooler_items = db.execute("SELECT * FROM cooler WHERE prep_flag = 'on' ORDER BY cooler_unit")  
        cooler_unit = db.execute("SELECT DISTINCT cooler_unit FROM cooler WHERE prep_flag = 'on' ORDER BY cooler_unit")
             
        freezer_items = db.execute("SELECT * FROM freezer WHERE prep_flag = 'on' ORDER BY cooler_unit")
        freezer_unit = db.execute("SELECT DISTINCT cooler_unit FROM freezer WHERE prep_flag = 'on' ORDER BY cooler_unit")  
             
        dry_items = db.execute("SELECT * FROM dry WHERE prep_flag = 'on' ORDER BY cooler_unit")
        dry_unit = db.execute("SELECT DISTINCT cooler_unit FROM dry WHERE prep_flag = 'on' ORDER BY cooler_unit")       
     
        return render_template('prep.html', cooler_items=cooler_items, cooler_unit=cooler_unit, freezer_items=freezer_items, freezer_unit=freezer_unit, dry_items=dry_items, dry_unit=dry_unit)


@app.route("/first_out", methods=["GET"])
@login_required
def first_out():
        cooler_items = db.execute("SELECT * FROM cooler WHERE age_flag = 'True' OR exp_flag = 'True' ORDER BY cooler_unit")  
        cooler_unit = db.execute("SELECT DISTINCT cooler_unit FROM cooler WHERE age_flag = 'True' OR exp_flag = 'True' ORDER BY cooler_unit")
             
        freezer_items = db.execute("SELECT * FROM freezer WHERE age_flag = 'True' OR exp_flag = 'True' ORDER BY cooler_unit")
        freezer_unit = db.execute("SELECT DISTINCT cooler_unit FROM freezer WHERE age_flag = 'True' OR exp_flag = 'True' ORDER BY cooler_unit")  
             
        dry_items = db.execute("SELECT * FROM dry WHERE age_flag = 'True' OR exp_flag = 'True' ORDER BY cooler_unit")
        dry_unit = db.execute("SELECT DISTINCT cooler_unit FROM dry WHERE age_flag = 'True' OR exp_flag = 'True' ORDER BY cooler_unit")       
     
        return render_template('first_out.html', cooler_items=cooler_items, cooler_unit=cooler_unit, freezer_items=freezer_items, freezer_unit=freezer_unit, dry_items=dry_items, dry_unit=dry_unit)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    session.clear()
    return render_template('index.html')


@app.route("/admin_page", methods=["GET"])
@login_required
def admin_page():
    return render_template('admin_page.html')


@app.route("/cooler_add", methods=["GET", "POST"])
@login_required
def cooler_add():
    if request.method == "POST":
        new_cooler = request.form.get("unit_name")
        db.execute("INSERT INTO cooler (cooler_unit) VALUES(?)", new_cooler)
        return redirect('cooler')
    return render_template('cooler_add.html')


@app.route("/freezer_add", methods=["GET", "POST"])
@login_required
def freezer_add():
    if request.method == "POST":
        new_cooler = request.form.get("unit_name")
        db.execute("INSERT INTO freezer (cooler_unit) VALUES(?)", new_cooler)
        return redirect('freezer')
    return render_template('freezer_add.html')


@app.route("/dry_add", methods=["GET", "POST"])
@login_required
def dry_add():
    if request.method == "POST":
        new_cooler = request.form.get("unit_name")
        db.execute("INSERT INTO dry (cooler_unit) VALUES(?)", new_cooler)
        return redirect('dry')
    return render_template('dry_add.html')


@app.route("/delete_user", methods=["GET", "POST"])
@login_required
def delete_user():
    if request.method == "POST":
        session['user_choice'] = request.form.get("user_id")
        username = session.get('user_choice')
        print(username, "username")
        user_list = db.execute("SELECT * FROM users WHERE id <>1 ORDER BY username")
        db.execute("DELETE FROM users WHERE username=?", username)       
        return render_template('admin_page.html', username=username, user_list=user_list)
    else:
        user_list = db.execute("SELECT * FROM users WHERE id <>1 ORDER BY username")        
        return render_template('delete_user.html', user_list=user_list)
