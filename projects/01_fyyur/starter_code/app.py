# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
	abort,
	jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from sqlalchemy import func
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database



# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
Show = db.Table('Show',
				db.Column('Venue_id', db.Integer, db.ForeignKey('Venue.id')),
				db.Column('Artist_id', db.Integer, db.ForeignKey('Artist.id')),
				db.Column('start_time', db.DateTime)
				)

class Venue(db.Model):
	__tablename__ = 'Venue'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String())
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	address = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))

	# TODO: implement any missing fields, as a database migration using Flask-Migrate
	genres = db.Column(db.String(120))
	website = db.Column(db.String(120))
	seeking_talent = db.Column(db.Boolean)
	seeking_description = db.Column(db.String(500))
	venues = db.relationship('Artist', secondary=Show, backref=db.backref('shows', lazy='joined'))


	def venue_info(self):
		return {'id': self.id,
				'name': self.name,
				'genres': self.genres.split(','),
				'city': self.city,
				'state': self.state,
				'phone': self.phone,
				'address': self.address,
				'image_link': self.image_link,
				'facebook_link': self.facebook_link,
				'website': self.website,
				'seeking_talent': self.seeking_talent,
				'seeking_description': self.seeking_description
				}

	def venue_info_with_upcoming_shows_count(self):
		return {'id': self.id,
				'name': self.name,
				'city': self.city,
				'state': self.state,
				'phone': self.phone,
				'address': self.address,
				'image_link': self.image_link,
				'facebook_link': self.facebook_link,
				'website': self.website,
				'seeking_talent': self.seeking_talent,
				'seeking_description': self.seeking_description,
				'num_shows': db.session.query(func.count(Show.c.Venue_id)).filter(Show.c.Venue_id == self.id).
					filter(Show.c.start_time > datetime.now()).all()[0][0]
				}

	def venue_info_with_shows_details(self):
		return {'id': self.id,
				'name': self.name,
				'genres': self.genres.split(','),
				'address': self.address,
				'city': self.city,
				'state': self.state,
				'phone': self.phone,
				'website': self.website,
				'facebook_link': self.facebook_link,
				'seeking_talent': self.seeking_talent,
				'seeking_description': self.seeking_description,
				'image_link': self.image_link,
				'past_shows':db.session.query(
					Artist.id.label("artist_id"),
					Artist.name.label("artist_name"),
					Artist.image_link.label("artist_image_link"),
					Show)
					.join(Artist,Show.c.Artist_id == Artist.id)
					.filter(Show.c.Venue_id == self.id)
					.filter(Show.c.start_time <= datetime.now()).all(),
				'upcoming_shows': db.session.query(
					Artist.id.label("artist_id"),
					Artist.name.label("artist_name"),
					Artist.image_link.label("artist_image_link"),
					Show)
					.join(Artist,Show.c.Artist_id == Artist.id)
					.filter(Show.c.Venue_id == self.id)
					.filter(Show.c.start_time > datetime.now())
					.all(),
				'past_shows_count': (db.session.query(
					func.count(Show.c.Venue_id))
					.filter(Show.c.Venue_id == self.id)
					.filter(Show.c.start_time <= datetime.now())
					.all())[0][0],
				'upcoming_shows_count': (db.session.query(
					func.count(Show.c.Venue_id))
					.filter(Show.c.Venue_id == self.id)
					.filter(Show.c.start_time > datetime.now())
					.all())[0][0]
				}



class Artist(db.Model):
	__tablename__ = 'Artist'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	genres = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))

	# TODO: implement any missing fields, as a database migration using Flask-Migrate
	website = db.Column(db.String(120))
	seeking_venue = db.Column(db.Boolean)
	seeking_description = db.Column(db.String(500))



	def artist_info_with_shows_details(self):
		return {'id': self.id,
				'name': self.name,
				'city': self.city,
				'state': self.state,
				'phone': self.phone,
				'genres': self.genres,
				'image_link': self.image_link,
				'facebook_link': self.facebook_link,
				'seeking_venue': self.seeking_venue,
				'seeking_description': self.seeking_description,
				'website': self.website,
				'upcoming_shows': db.session.query(
					Venue.id.label("venue_id"),
					Venue.name.label("venue_name"),
					Venue.image_link.label("venue_image_link"),
					Show)
					.join(Venue, Show.c.Venue_id == Venue.id)
					.filter(Show.c.Artist_id == self.id)
					.filter(Show.c.start_time > datetime.now())
					.all(),
				'past_shows': db.session.query(
					Venue.id.label("venue_id"),
					Venue.name.label("venue_name"),
					Venue.image_link.label("venue_image_link"),
					Show)
					.join(Venue, Show.c.Venue_id == Venue.id)
					.filter(Show.c.Artist_id == self.id)
					.filter(Show.c.start_time <= datetime.now())
					.all(),
				'upcoming_shows_count': (db.session.query(
					func.count(Show.c.Artist_id))
					.filter(Show.c.Artist_id == self.id)
					.filter(Show.c.start_time > datetime.now())
					.all())[0][0],
				'past_shows_count': (db.session.query(
					func.count(Show.c.Artist_id))
					.filter(Show.c.Artist_id == self.id)
					.filter(Show.c.start_time <= datetime.now())
					.all())[0][0]
				}


	def artist_info(self):
		return {'id': self.id,
				'name': self.name,
				'city': self.city,
				'state': self.state,
				'phone': self.phone,
				'genres': self.genres,
				'image_link': self.image_link,
				'facebook_link': self.facebook_link,
				'website': self.website,
				'seeking_venue': self.seeking_venue,
				'seeking_description':self.seeking_description
				}

	def artist_name(self):
		return {'id': self.id,
				'name': self.name}
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


db.create_all()

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
	date = dateutil.parser.parse(str(value))
	if format == 'full':
		format = "EEEE MMMM, d, y 'at' h:mma"
	elif format == 'medium':
		format = "EE MM, dd, y h:mma"
	return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
	return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.
	unique_city_states = Venue.query.distinct(Venue.city, Venue.state).all()
	data = []
	for item in unique_city_states:
		venue= {'city': item.city,
					'state': item.state,
					'venues': []}
		for v in Venue.query.filter(Venue.city == item.city,Venue.state == item.state).all():
			venue['venues'].append(v.venue_info_with_upcoming_shows_count())
		data.append(venue)
	return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for Hop should return "The Musical Hop".
	# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
	search_term = request.form.get('search_term', '')
	venues = Venue.query.filter(
		Venue.name.ilike("%{}%".format(search_term))).all()
	count_venues = len(venues)

	response = {
		"count": count_venues,
		"data": [v.venue_info() for v in venues]
	}

	return render_template('pages/search_venues.html', results=response,
						   search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	venue = Venue.query.get(venue_id)
	if venue is None:
		abort(404)
	else:data = venue.venue_info_with_shows_details()
	return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	# TODO: insert form data as a new Venue record in the db, instead
	# TODO: modify data to be the data object returned from db insertion
	try:
		venue_form = VenueForm(request.form)
		new_venue = Venue(
			name=venue_form.name.data,
			genres=','.join(venue_form.genres.data),
			address=venue_form.address.data,
			city=venue_form.city.data,
			state=venue_form.state.data,
			phone=venue_form.phone.data,
			facebook_link=venue_form.facebook_link.data,
			image_link=venue_form.image_link.data
		)
		db.session.add(new_venue)
		db.session.commit()
		# on successful db insert, flash success
		flash('Venue ' + request.form['name'] + ' was successfully listed!')
	# TODO: on unsuccessful db insert, flash an error instead.
	except:
		db.session.rollback()
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
	finally:
		db.session.close()
	return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
	# TODO: Complete this endpoint for taking a venue_id, and using
	# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
	try:
		Venue.query.filter_by(id=venue_id).delete()
		db.session.commit()
		flash('Venue ' + venue_id + ' was successfully deleted!')
	except:
		db.session.rollback()
		flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
	finally:
		db.session.close()
	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage
	return jsonify({ 'success': True })


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	# TODO: replace with real data returned from querying the database
	data=[]
	artists = Artist.query.all()
	for item in artists:
		data.append(item.artist_name())
	return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
	# search for "band" should return "The Wild Sax Band".
	search_term = request.form.get('search_term', '')
	artists = Artist.query.filter(
		Artist.name.ilike("%{}%".format(search_term))).all()
	count_artists= len(artists)

	response = {
		"count": count_artists,
		"data": [a.artist_info() for a in artists]
	}

	return render_template('pages/search_artists.html', results=response,
						   search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	# shows the artist page with the given artist_id
	# TODO: replace with real artist data from the artists table, using artist_id
	artist = Artist.query.get(artist_id)
	if artist is None:
		abort(404)
	else:
		data = artist.artist_info_with_shows_details()
	return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()
	artist = Artist.query.get(artist_id)
	if artist is None:
		abort(404)
	else:
		form.name.data = artist.name
		form.city.data = artist.city
		form.state.data = artist.state
		form.phone.data = artist.phone
		form.genres.data = artist.genres
		form.facebook_link.data = artist.facebook_link
	# TODO: populate form with fields from artist with ID <artist_id>
	return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	# TODO: take values from the form submitted, and update existing
	# artist record with ID <artist_id> using the new attributes
	try:
		artist_form = ArtistForm(request.form)
		artist = Artist.query.get(artist_id)
		artist.name=artist_form.name.data,
		artist.genres=','.join(artist_form.genres.data),
		artist.city=artist_form.city.data,
		artist.state=artist_form.state.data,
		artist.phone=artist_form.phone.data,
		artist.facebook_link=artist_form.facebook_link.data,
		artist.image_link=artist_form.image_link.data
		db.session.commit()

		# on successful db insert, flash success
		flash('Artist ' + request.form['name'] + ' was successfully updated!')
	except:
		flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
	finally:
		db.session.close()

	return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()
	venue = Venue.query.get(venue_id)
	if venue is None:
		abort(404)
	else:
		form.name.data = venue.name
		form.city.data = venue.city
		form.state.data = venue.state
		form.address.data = venue.address
		form.phone.data = venue.phone
		form.genres.data = venue.genres
		form.facebook_link.data = venue.facebook_link
	# TODO: populate form with values from venue with ID <venue_id>
	return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	# TODO: take values from the form submitted, and update existing
	# venue record with ID <venue_id> using the new attributes
	try:
		venue_form = VenueForm(request.form)
		venue = Venue.query.get(venue_id)
		venue.name=venue_form.name.data,
		venue.genres=','.join(venue_form.genres.data),
		venue.address=venue_form.address.data,
		venue.city=venue_form.city.data,
		venue.state=venue_form.state.data,
		venue.phone=venue_form.phone.data,
		venue.facebook_link=venue_form.facebook_link.data,
		venue.image_link=venue_form.image_link.data
		db.session.commit()

		# on successful db insert, flash success
		flash('Venue ' + request.form['name'] + ' was successfully updated!')
	except:
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
	finally:
		db.session.close()

	return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
	form = ArtistForm()
	return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	# called upon submitting the new artist listing form
	# TODO: insert form data as a new Venue record in the db, instead
	# TODO: modify data to be the data object returned from db insertion
	try:
		artist_form = ArtistForm(request.form)
		new_artist = Artist(
			name=artist_form.name.data,
			genres=','.join(artist_form.genres.data),
			city=artist_form.city.data,
			state=artist_form.state.data,
			phone=artist_form.phone.data,
			facebook_link=artist_form.facebook_link.data,
			image_link=artist_form.image_link.data
		)
		db.session.add(new_artist)
		db.session.commit()
		# on successful db insert, flash success
		flash('Artist ' + request.form['name'] + ' was successfully listed!')
	# TODO: on unsuccessful db insert, flash an error instead.
	except:
		db.session.rollback()
		flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
	finally:
		db.session.close()

	return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
	# displays list of shows at /shows
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.
	data=(db.session.query(
    Venue.id.label("venue_id"),
    Venue.name.label("venue_name"),
    Artist.id.label("artist_id"),
    Artist.name.label("artist_name"),
    Artist.image_link.label("artist_image_link"),
    Show)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.Artist_id == Artist.id)
    .all())

	return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	# called to create new shows in the db, upon submitting new show listing form
	# TODO: insert form data as a new Show record in the db, instead
	try:
		show_form = ShowForm(request.form)
		new_show = Show.insert().values(
			Artist_id=show_form.artist_id.data,
			Venue_id=show_form.venue_id.data,
			start_time=show_form.start_time.data
		)
		db.session.execute(new_show)
		db.session.commit()
		# on successful db insert, flash success
		flash('Show was successfully listed!')
	# TODO: on unsuccessful db insert, flash an error instead.
	except:
		db.session.rollback()
		flash('An error occurred. Show could not be listed.')
	# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	finally:
		db.session.close()
	return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
	return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
	return render_template('errors/500.html'), 500


if not app.debug:
	file_handler = FileHandler('error.log')
	file_handler.setFormatter(
		Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
	)
	app.logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
	app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
