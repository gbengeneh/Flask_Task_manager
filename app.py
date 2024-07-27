from flask import Flask, render_template, redirect, request, flash, url_for
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# app setup 
app = Flask(__name__)
Scss(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.secret_key = 'your_secret_key'  # Needed for flashing messages
db = SQLAlchemy(app)

# data class
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow) 

    def __repr__(self) -> str:
        return f"Task {self.id}"
    
with app.app_context():
        db.create_all()

# routes to webpages
# home page 
@app.route("/", methods=["POST", "GET"])
def index():
    # add a Task 
    if request.method == "POST":
        current_task = request.form['content']
        new_task = MyTask(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR: {e}")
            return f"ERROR: {e}"
    # see all current tasks
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()
        return render_template('index.html', tasks=tasks)

# delete an item 
@app.route("/delete/<int:id>")
def delete(id:int):
    print(f"Delete route hit with id: {id}")  # Debugging statement
    delete_task = MyTask.query.get_or_404(id)
    try:
        print(f"Task to delete: {delete_task}")  # Debugging statement
        db.session.delete(delete_task)
        db.session.commit()
        flash('Task successfully deleted!', 'success')
        return redirect("/")
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {e}', 'danger')
    return redirect("/")


# Edit an item
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id:int):
    task = MyTask.query.get_or_404(id)
    if request.method=="POST":
        task.content=request.form['content']
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Error:{e}"
    else:
        return  render_template('edit.html', task=task)



# Runner and debugger
if __name__ == "__main__":
   
    app.run(debug=True)
