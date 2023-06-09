from flask import Flask, redirect, url_for, session, request, jsonify,  Markup
from flask_oauthlib.client import OAuth
#from flask_oauthlib.contrib.apps import github #import to make requests to GitHub's OAuth
from flask import render_template
from flask import flash

import pprint
import os

import pymongo
import sys
from bson.objectid import ObjectId

from datetime import date
# This code originally from https://github.com/lepture/flask-oauthlib/blob/master/example/github.py
# Edited by P. Conrad for SPIS 2016 to add getting Client Id and Secret from
# environment variables, so that this will work on Heroku.
# Edited by S. Adams for Designing Software for the Web to add comments and remove flash messaging
connection_string = os.environ["MONGO_CONNECTION_STRING"]
db_name = os.environ["MONGO_DBNAME"]
client = pymongo.MongoClient(connection_string)
db = client[db_name]
collection = db['Posts']

app = Flask(__name__)

app.debug = True #Change this to False for production
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #Remove once done debugging

app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)
oauth.init_app(app) #initialize the app to be able to make requests for user information

#Set up GitHub as OAuth provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)




#context processors run before templates are rendered and add variable(s) to the template's context
#context processors must return a dictionary 
#this context processor adds the variable logged_in to the conext for all templates
@app.context_processor
def inject_logged_in():
    return {"logged_in":('github_token' in session)}

@app.route('/')
def home():
        return render_template('home.html', post=chat())
        
@app.route('/com')
def com():
        return render_template('home.html', post=chat())
        
def chat(): 
    posts=""
    for doc in collection.find():
        posts = posts + Markup('<div class="post">' "<table style='width:100%'>"

        "<tr>" '<th class="user">' + "User:" + doc["Username"] + '</th> </tr> <tr> <td class="date">' + doc['Date'] + '</td> </tr> <tr> <td class="subject">' + doc['Subject'] + '</td> </tr>' + '<tr> <td>'+ doc['Body'] + '</td> </tr> <tr><td>  <button class="comBox"onclick="showCommentForm()">Comment</button>  <div class="inter" style="display: none;"><form action="/com" id="'+str(doc["_id"])+'" method="POST"><textarea rows="4" cols="50" name="comment" form="comment"></textarea><input type="hidden" name="Comment" value="'+str(doc["_id"])+'"></input><br><input type="submit"></form> <form class="likeBtn" action="/like" method ="POST"><input type="submit" class="totalLikes" value="Like"></input><input type = "hidden" name="Like" value="'+ str(doc['_id']) + '">' + str(doc['Likes']) + '</input></form></div></td></tr> </table> </div>') 

    return posts
    
@app.route('/post', methods=["GET","POST"])
def post():
    if 'user_data' in session:
        newpost= {'Username':session['user_data']['login'],
        'Subject':request.form['Subject'],
        'Date':str(date.today()),
        'Body':request.form['Body'],
        'Likes':request.form['Likes']
        }
        collection.insert_one(newpost)
        return render_template('home.html', post=chat())
    else:
        return redirect('/', post=chat())
#redirect to GitHub's OAuth page and confirm callback URL

@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='http')) #callback URL must match the pre-configured callback URL

@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out.')
    return redirect('/')

@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        flash('Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args), 'error')      
    else:
        try:
            session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
            session['user_data']=github.get('user').data
            #pprint.pprint(vars(github['/email']))
            #pprint.pprint(vars(github['api/2/accounts/profile/']))
            flash('You were successfully logged in as ' + session['user_data']['login'] + '.')
        except Exception as inst:
            session.clear()
            print(inst)
            flash('Unable to login, please try again.', 'error')
    return redirect('/')



#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session['github_token']

@app.route('/com', methods=["GET", "POST"])
def comment():

    if request.method == "POST":
        comment_id = request.form.get("Comment")
        if ObjectId.is_valid(comment_id):
            myquery = { "_id": ObjectId(comment_id) }
            print(request.form)
            newvalues = { "$set": { "Comments":request.form.get("newc")} }
            collection.update_one(myquery, newvalues)
            
    return redirect('/')

@app.route('/like', methods=["GET", "POST"])
def like():
    one = {'_id':ObjectId(request.form['Like'])}
    newLikes = {"$inc": {"Likes": 1 } }
    collection.update_one(one, newLikes)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
