from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import os
from datetime import datetime 

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "data", "library.sqlite")}'
app.secret_key = 'your-secret-key-here'  # Required for flash messages
db.init_app(app)


@app.route('/add_author', methods=['GET'])
def add_author():
    return render_template('add_author.html')

@app.route('/', methods=['GET'])
def homepage():
    # Get sort parameters from query string
    sort_by = request.args.get('sort_by', 'title')  # default sort by title
    order = request.args.get('order', 'asc')  # default ascending order
    

    print('Author.name.desc()->', Author.name.desc())

    # Build the query based on sort parameters
    if sort_by == 'author':
        # Join with Author table and sort by author name
        if order == 'desc':
            books = Book.query.join(Author).order_by(Author.name.desc()).all()
        else:
            books = Book.query.join(Author).order_by(Author.name.asc()).all()
    else:
        # Sort by book attributes (title or publication_year)
        column_to_be_sorted = getattr(Book, sort_by)
        print('column_to_be_sorted.desc()', column_to_be_sorted.desc())

        if order == 'desc':
            books = Book.query.order_by(column_to_be_sorted.desc()).all()
        else:
            books = Book.query.order_by(column_to_be_sorted.asc()).all()
    
    return render_template('home.html', books=books, sort_by=sort_by, order=order)


@app.route('/add_author', methods=['POST'])
def add_author_post():
    name = request.form['name']
    birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
    date_of_death = datetime.strptime(request.form['date_of_death'], '%Y-%m-%d').date() if request.form['date_of_death'] else None
    
    new_author = Author(
        name=name,
        birth_date=birthdate,
        date_of_death=date_of_death
    )
    
    db.session.add(new_author)
    db.session.commit()
    
    flash(f'Author {name} was successfully added!')
    return redirect(url_for('add_author'))


@app.route('/add_book', methods=['GET'])
def add_book():
    # Get all authors to populate the dropdown
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    book_title = book.title
    
    db.session.delete(book)
    db.session.commit()
    
    flash(f'Book "{book_title}" was successfully deleted!')
    return redirect(url_for('homepage'))



@app.route('/add_book', methods=['POST'])
def add_book_post():
    title = request.form['title']
    publication_year = request.form['publication_year']
    author_id = request.form['author_id']
    
    new_book = Book(
        title=title,
        publication_year=publication_year,
        author_id=author_id
    )
    
    db.session.add(new_book)
    db.session.commit()
    
    flash(f'Book {title} was successfully added!')
    return redirect(url_for('add_book'))  # This will trigger the GET route which handles authors


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)