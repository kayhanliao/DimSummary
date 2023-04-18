from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template

# <!DOCTYPE html>
# <head>
#     <title>Simple Search Engine</title>
# </head>
# <body>
#     <form action="/search" method="POST">
#         {{form.csrf_token}}
#         {{form.ids}}
#         {{form.submit}}
#     </form>
# </body>

class BasicForm(FlaskForm):
    ids = StringField("ID",validators=[DataRequired()])
    submit = SubmitField("Submit")

# when you hit submit, url: /search
    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'leonardo'

@app.route("/",methods =['POST','GET'])
def main():
    form = BasicForm()
    return render_template("index.html",form = form)

if __name__ == "__main__":
    app.run(debug=True)