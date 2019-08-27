from app import app, db
from flask import request, jsonify
from app.models import User, Messages, Room
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

        return jsonify({ 'message' : 'success', 'username': user.username, 'token': user.get_token()})

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
    id = request.headers.get('id')
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
            'id': result.id,
            'username': result.username,
            'email': result.email,
            'zipcode': result.zipcode,
            'sexuality': result.sexuality,
            'gender': result.gender,
            'religion': result.religion
        }

        users.append(user)

        return jsonify({
            'success': 'Retrieved Users',
            'users': users
        })



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
                'id': result.id,
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


@app.route('/api/message', methods=['POST'])
def message():
    try:

        date_sent = request.headers.get('date_sent')
        user_id = request.headers.get('user_id')
        reciever_id = request.headers.get('reciever_id')
        message = request.headers.get('message')





        message=Messages(date_sent=date_sent,user_id=user_id,reciever_id=reciever_id,message=message)



        db.session.add(message)
        db.session.commit()

        return jsonify({'message': 'success'})

    except:
        return jsonify({'message': 'Was unable to send a message.'})


@app.route('/api/retrievemessage', methods=['GET'])
def retrievemessage():


    message_id = request.headers.get('message_id')
    date_sent = request.headers.get('date_sent')
    user_id = request.headers.get('user_id')
    reciever_id = request.headers.get('reciever_id')
    message = request.headers.get('message')

    results = Messages.query.filter_by(reciever_id=reciever_id).all()


    messages = []
    if results == None:
        return jsonfiy({'success': 'No Messages Found'})



        for result in results:
            message = {
                'message_id': result.message_id,
                'date_sent': result.date_sent,
                'user_id': result.user_id,
                'reciever_id': result.reciever_id,
                'message': result.message,
                'religion': result.religion
            }

            messsages.append(message)

        return jsonify({
            'success': 'messages',
            'messages': messages
            })

@app.route('/api/saveroom', methods=['POST'])
def saveroom():
    room = request.headers.get('room')
    user1 = request.headers.get('user1')
    user2 = request.headers.get('user2')


    chat = Room(room=room,user1=user1,user2=user2)

    db.session.add(chat)
    db.session.commit()

@app.route('/api/retrieveroom', methods=['GET'])
def retrieveroom():
    room = request.headers.get('room')
    user1 = request.headers.get('user1')
    user2 = request.headers.get('user2')

    if not user1 or not user2:
        return jsonify({ 'success': 'User has no chats'})
    elif user1:
        results = Room.query.filter_by(user1=user1).all()
    elif user2:
        results = Room.query.filter_by(user2=user2).all()

    if results == []:
        return jsonify({ 'success': 'No Chat Rooms'})

    rooms = []

    for result in results:
        room = {
            'room': result.room,
            'user1': result.user1,
            'user2': result.user2
        }

        rooms.append(room)

    return jsonfiy({
        'success': 'Retrieved Rooms',
        'rooms': rooms
    })
