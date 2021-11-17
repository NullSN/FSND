#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from enum import unique
import json
from typing import final
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import csrf
from flask_wtf.csrf import CSRFProtect
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from sqlalchemy import or_
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)
csrf = CSRFProtect(app)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(200))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    show_id = db.relationship('Show', backref='venue', cascade="all,delete")
    joined = db.Column(db.DateTime)

    __table_args__ = (
        UniqueConstraint('city', 'state', 'address', name='unique_address'),
    )


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(200))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    show_id = db.relationship('Show', backref='artist', cascade='all,delete')
    joined = db.Column(db.DateTime)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    artist_list = Artist.query.limit(10).all()
    venue_list = Venue.query.limit(10).all()
    combined_list = artist_list + venue_list
    recent_action = sorted(combined_list, key=lambda x: x.joined, reverse=True)
    return render_template('pages/home.html', recent_action=recent_action[:10])


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    return render_template('pages/venues.html',
                           venues=Venue.query.all())


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term')
    formated_search_term = "%{}%".format(search_term)
    response = Venue.query.filter(or_(Venue.name.ilike(formated_search_term), Venue.city.ilike(formated_search_term),
                                      Venue.state.ilike(formated_search_term), Venue.genres.ilike(formated_search_term))).all()
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    today_date = datetime.today()
    upcoming_shows = []
    previous_shows = []
    venue = venue = Venue.query.get_or_404(venue_id)

    for show in venue.show_id:
        if show.start_time > today_date:
            upcoming_shows.append(show)
        else:
            previous_shows.append(show)

    return render_template('pages/show_venue.html',
                           venue=venue, upcoming_shows=upcoming_shows, previous_shows=previous_shows)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate_on_submit():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                joined=datetime.today()
            )
            db.session.add(venue)
            db.session.commit()
            flash(f'Welcome, {venue.name} to the site.')
            return render_template('pages/home.html')
        except IntegrityError:
            flash('This location already exist.')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash(form.errors)
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<int:venue_id>', methods=['post'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash(f'Venue {venue.name} was successfully deleted.')
    except:
        db.session.rollback()
        flash(f"An error occured. Venue {venue_id} could not be deleted.")
        return render_template('venues/<int:venue_id>')
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    return render_template('pages/artists.html',
                           artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    formated_search_term = "%{}%".format(search_term)
    response = Artist.query.filter(or_(Artist.name.ilike(formated_search_term), Artist.city.ilike(formated_search_term),
                                       Artist.state.ilike(formated_search_term), Artist.genres.ilike(formated_search_term))).all()
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    today_date = datetime.today()
    upcoming_shows = []
    previous_shows = []
    artist = Artist.query.get_or_404(artist_id)

    for show in artist.show_id:
        if show.start_time > today_date:
            upcoming_shows.append(show)
        else:
            previous_shows.append(show)

    return render_template('pages/show_artist.html',
                           artist=artist, today_date=today_date, upcoming_shows=upcoming_shows, previous_shows=previous_shows)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    form.populate_obj(artist)
    form.genres.data = ''.join(artist.genres)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    if form.validate():
        try:
            form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
            flash(f'Success')
            return redirect(url_for('show_artist', artist_id=artist_id))
        except IntegrityError:
            flash('This artist already exist')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash(form.errors)
    return redirect(url_for('edit_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    form.populate_obj(venue)
    form.genres.data = ''.join(venue.genres)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    if form.validate():
        try:
            form.populate_obj(venue)
            db.session.add(venue)
            db.session.commit()
            flash('Success')
            return redirect(url_for('show_venue', venue_id=venue_id))
        except IntegrityError:
            flash('This location already exist.')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash(form.errors)
    return redirect(url_for('edit_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    if form.validate_on_submit():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
                joined=datetime.today()
            )
            db.session.add(artist)
            db.session.commit()
            flash(f'Artist: {artist.name} was successfully listed!')
            return render_template('pages/home.html')
        except IntegrityError:
            flash("This artist already exist")
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash(form.errors)
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    today_date = date.today()

    return render_template('pages/shows.html',
                           shows=Show.query.filter(Show.start_time >= today_date).all())


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    artists = Artist.query.all()
    venues = Venue.query.all()
    return render_template('forms/new_show.html', form=form, artists=artists, venues=venues)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    if form.validate():
        try:
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
        except IntegrityError as error:
            e = error.orig.diag.message_detail
            if "artist" in e:
                flash("This artist id doesn't exist")
            elif "venue" in e:
                flash("This venue id doesn't exist.")
            else:
                flash(e)
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash(form.errors)
    return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
