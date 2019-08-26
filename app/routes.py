from app import app, db
from flask import request, jsonify
from app.models import User
import time
import jwt

@app.route('/')
def index():
    return ''

@app.route('/authenticate/register', methods=['POST'])
def register():
    try:

        #i believe this is what will be sent through the headers... may disrupt
        token = request.headers.get('token')

        print(token)

        #decode the token back to a dictionary

        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithm=['HS256']
        )

        print(data)

        #create the user and save

        user = User(email=data['email'], username=data['username'], zipcode=data['zipcode'], sexuality=data['sexuality'], gender=data['gender'], religion=data['religion'])


        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'success'})

    except:
        return jsonify({'message': 'Error #001: User not created'})


@app.route('/authenticate/login', methods=['GET'])
def login():
    try:
        token = request.headers.get('token')

        print(token)

        #decode the token back to a dictionary

        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithm=['HS256']
        )

        print(data)

        #query db to get user and check password_hash
        user = User.query.filter_by(email=data['email']).first()

        if user is None or not user.check_password(data['password']):
                return jsonify({'message' : 'Error #002: Invalid Credentials'})

        #create a token for that user and return it

        return jsonify({ 'message' : 'success', 'token': user.get_token()})

    except:
        return jsonify({'message': 'Error #003: Failure to login'})



@app.route('/api/login', methods=['GET'])
def data():
    try:
        token = request.headers.get('token')
        zipcode = request.headers.get('zipcode')
        sexuality = request.headers.get('sexuality')
        gender = request.headers.get('gender')
        religion = request.headers.get('religion')

        #get user id or None

        user = User.verify_token(token)

        if not user:
            return jsonify({ 'message' : 'Error #004: Invalid User'})

        #this is usually where you would query the database with user_id that we got back from the verify token method, and create a new token to be passed back with encrypted information

        data = {

        #you must query all of this data
            'logged - in' : 'yes'
        }

        #check out the event scheduler and how we sent the data

        return jsonify({ 'info': data })

    except:
        return jsonify({ 'message' : 'Error #005: Invalid Token'})




#for querying the users after

@app.route('/api/retrieve', methods=['GET'])
def retrieve():
    username = request.headers.get('username')
    email = request.headers.get('email')
    zipcode = request.headers.get('zipcode')
    sexuality = request.headers.get('sexuality')
    gender = request.headers.get('gender')
    religion = request.headers.get('religion')


    users = []
    if username:
        result = User.query.filter_by(username=username).first()

        if result == None:
            return jsonify({'success': 'No Users Found'})


        user = {
            'username': result.username,
            'email': result.email,
            'zipcode': result.zipcode,
            'sexuality': result.sexuality,
            'gender': result.gender,
            'religion': result.religion
        }

        return jsonify({
            'success': 'Retrieved Users',
            'users': user
        })

        users.append(user)

    else:

        if not zipcode:
            return jsonify({ 'error': 'Error #003: Zipcode Parameter is Required'})
        elif zipcode and not sexuality and not gender and not religion:
            results = User.query.filter_by(zipcode=zipcode).all()
        elif zipcode and sexuality and not gender and not religion:
            results = User.query.filter_by(zipcode=zipcode, sexuality=sexuality).all()
        elif zipcode and gender and not sexuality and not religion:
            results = User.query.filter_by(zipcode=zipcode, gender=gender).all()
        elif zipcode and religion and not gender and not sexuality:
            results = User.query.filter_by(zipcode=zipcode, religion=religion).all()

        elif zipcode and sexuality and gender and not religion:
            results = User.query.filter_by(zipcode=zipcode, sexuality=sexuality, gender=gender).all()
        elif zipcode and sexuality and religion and not gender:
            results = User.query.filter_by(zipcode=zipcode, sexuality=sexuality, religion=religion).all()

        elif zipcode and religion and gender and not sexuality:
            results = User.query.filter_by(zipcode=zipcode, gender=gender, religion=religion).all()

        elif zipcode and gender and religion and sexuality:
            results = User.query.filter_by(zipcode=zipcode, gender=gender,religion=religion).all()

        if results == None:
            return jsonfiy({'success' : 'No Users Found'})

        # loop over results because it is an instance of an event. Save information into new list and return



        for result in results:
            user = {
                'username': result.username,
                'email': result.email,
                'zipcode': result.zipcode,
                'sexuality': result.sexuality,
                'gender': result.gender,
                'religion': result.religion
            }

            users.append(user)

        return jsonify({
            'success': 'Retrieved Events',
            'users': users
            })
