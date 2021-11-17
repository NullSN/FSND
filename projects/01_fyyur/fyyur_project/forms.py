from datetime import datetime
from logging import raiseExceptions
from os import path
from typing import Optional
from flask.helpers import flash
from flask_wtf import Form
from phonenumbers.phonenumberutil import NumberParseException
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, StopValidation, ValidationError
from urllib.parse import urlsplit
import urllib.request as req
import phonenumbers
from phonenumbers import geocoder
import us


def Is_a_number(form, field):
    data = field.data
    if data.isalpha():
        raise StopValidation(f"This must be a number")


def URL_Check(form, field):
    url = field.data
    split = urlsplit(url)
    if not split.netloc:
        url = 'www.' + url
    if not split.scheme:
        url = 'https://' + url
    try:
        field.data = url
        return(field.data)
    except:
        raise ValidationError("Please enter a valid url.")


def FB_Check(form, field):
    url = field.data
    split = urlsplit(url)
    if 'www.facebook.com' not in split.netloc:
        raise ValidationError("This isn't a facebook link.")


def phone_number_check(form, field):
    try:
        number = phonenumbers.parse(field.data, 'US')
    except NumberParseException:
        raise StopValidation('Not a valid number.')
    if not phonenumbers.is_valid_number(number):
        raise StopValidation(f"Not a valid number.")
    form_numb = phonenumbers.format_number(
        number, phonenumbers.PhoneNumberFormat.NATIONAL)
    field.data = form_numb
    return(field.data)


def phone_in_state(form, field):
    number = phonenumbers.parse(field.data, "US")
    state_info = geocoder.description_for_number(number, 'en')
    state_abr = get_state_abbr(state_info)
    state_on_form = form.state.data
    if state_abr != state_on_form:
        raise ValidationError(
            "The phone number does not match the state selected.")


def get_state_abbr(state_info):
    # The phonenumbers library has been inconsitant in what info it returns.
    # Sometimes geocoder.description_for_number(num, 'en') returns the state in full('Rhode Island'),
    # other times it returns a city and state abbreviation('Providence, RI), and with Washing D.C. no ',' was used.
    #  When the city and state abbreviation was returned, this caused the 'us' library to return a None type.

    if "," in state_info:
        split_state = state_info.split(",")
        state_abr = split_state[1].strip()
    elif 'D.C.' in state_info:
        state_abr = 'DC'
    else:
        state = us.states.lookup(state_info)
        state_abr = state.abbr

    return state_abr


class ShowForm(Form):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired(), Is_a_number]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired(), Is_a_number]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    city = StringField(
        'city',
        validators=[DataRequired(), Length(max=120)]
    )
    state = SelectField(
        'state',
        validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('MA', 'MA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY')
        ]
    )
    address = StringField(
        'address',
        validators=[DataRequired(), Length(max=120)]
    )
    phone = StringField(
        'phone',
        validators=[Optional(), Length(max=120),
                    phone_number_check, phone_in_state]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), Length(max=500), URL_Check]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired()],
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), Length(max=120), URL_Check, FB_Check]
    )
    website_link = StringField(
        'website_link',
        validators=[Optional(), Length(max=120), URL_Check]
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description',
        validators=[Optional(), Length(max=500)]
    )


class ArtistForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    city = StringField(
        'city',
        validators=[DataRequired(), Length(
            max=120, message="The city must be shorter than 120 characters.")]
    )
    state = SelectField(
        'state',
        validators=[DataRequired(message="Please select a state.")],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY')
        ]
    )

    phone = StringField(
        'phone',
        validators=[Optional(), Length(max=120),
                    phone_number_check, phone_in_state]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), Length(max=500), URL_Check]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired()],
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), URL_Check, FB_Check]
    )

    website_link = StringField(
        'website_link',
        validators=[Optional(), Length(max=120), URL_Check]
    )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
        'seeking_description',
        validators=[Optional(), Length(max=500)]
    )
