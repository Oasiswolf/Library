from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    genre = db.Column(db.String)
    dewey_dec = db.Column(db.String, nullable=False, unique=True)
    author = db.Column(db.String, nullable=False)

    def __init__(self, title, genre, dewey_dec, author):
        self.title = title
        self.genre = genre
        self.dewey_dec = dewey_dec
        self.author = author

class BookSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'genre', 'dewey_dec', 'author')

book_schema = BookSchema()
multi_book_schema = BookSchema(many=True)

@app.route('/book/add', methods=["POST"])
def add_book():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')

    post_data = request.get_json()
    title = post_data.get('title')
    genre = post_data.get('genre')
    dewey_dec = post_data.get('dewey_dec')
    author = post_data.get('author')


    if title == None:
        return jsonify("Error: You must provide a 'Title' key")
    if dewey_dec == None:
        return jsonify("Error: You must provide a 'Genre' key")
    
    new_record = Library(title, genre, dewey_dec, author)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(book_schema.dump(new_record))

@app.route('/book/get', methods=["GET"])
def get_all_books():
    all_records = db.session.query(Library).all()
    return jsonify(multi_book_schema.dump(all_records))


@app.route('/book/get/<id>', methods=["GET"])
def get_book_id(id):
    one_book = db.session.query(Library).filter(Library.id == id).first()
    return jsonify(book_schema.dump(one_book))

@app.route('/book/update/<id>', methods=["PUT"])
def update_book_id(id):
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')
    
    put_data = request.get_json()
    title = put_data.get('title')
    genre = put_data.get('genre')
    dewey_dec = put_data.get('dewey_dec')
    author = put_data.get('author')

    book_to_update = db.session.query(Library).filter(Library.id == id).first()

    if title != None:
        book_to_update.title = title
    if genre != None:
        book_to_update.genre = genre
    if dewey_dec != None:
        book_to_update.dewey_dec = dewey_dec
    if author != None:
        book_to_update.author = author

    db.session.commit()

    return jsonify(book_schema.dump(book_to_update))

@app.route('/book/delete/<id>', methods=["DELETE"])
def book_to_delete(id):
    delete_book = db.session.query(Library).filter(Library.id == id).first()
    db.session.delete(delete_book)

    db.session.commit()

    return jsonify("book got Erased!")




if __name__ == "__main__":
    app.run(debug = True)