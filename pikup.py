from flask import Flask, request, make_response, redirect, url_for, Response
from flask import render_template, Markup, flash, session, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash, gen_salt
import flask_login
import requests
import os
from io import StringIO
from datetime import datetime
import database as db
import helpers as hlp
from bson.objectid import ObjectId

TEMPLATE_DIR = './templates'
STATIC_DIR = './static'

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

if 'mapbox_token' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()
    MAPBOX_TOKEN = os.environ.get('mapbox_token')
else:
    MAPBOX_TOKEN = os.environ['mapbox_token']


@app.route('/', methods=['GET'])
def index():

  html = render_template('index.html')
  return make_response(html)

@app.route('/req', methods=['GET', 'POST'])
def req():

  if request.method=='POST':
    # make a new dict to insert in database
    newJob = {
      "latOrig" : float(request.form["latOrig"]),
      "lonOrig" : float(request.form["lonOrig"]),
      "latDest" : float(request.form["latDest"]),
      "lonDest" : float(request.form["lonDest"]),
      "deliverBy" : request.form["deliverBy"],
      "size" : request.form["size"],
      "weight" : request.form["weight"],
      "covered" : int(request.form["covered"]),
      "starting" : int(request.form["offer"]),
      "offer" : int(request.form["offer"]),
      "notes" : request.form["notes"]
    }
    db.insertOne("jobs", newJob)
    distTo = hlp.distance(newJob["latOrig"], newJob['latDest'], newJob['lonOrig'], newJob['lonDest'])
    html = render_template('confirm.html', mapbox_token=MAPBOX_TOKEN, job=newJob, distTo=distTo)
    return make_response(html)

  html = render_template('request.html', mapbox_token=MAPBOX_TOKEN)
  return make_response(html)

@app.route('/offer', methods=['GET'])
def offer():

  html = render_template('offer.html')
  return make_response(html)

@app.route('/available', methods=['GET'])
def available():

  # get the user's location from cookies
  userLat = float(request.cookies.get("userLat"))
  userLon = float(request.cookies.get("userLon"))

  # get jobs from database query
  jobs = [j for j in db.getAll("jobs", "deliverBy")]
  # for each job, calculate distance from user and between points
  dists = []
  if userLat and userLon:
    for j in jobs:
      distAway = hlp.distance( j["latOrig"], userLat, j["lonOrig"], userLon)
      distBetween = hlp.distance(j["latOrig"], j["latDest"], j["lonOrig"], j["lonDest"])
      dists.append((distAway,distBetween))
  # if there are no location cookies, prompt the user for them 
  else:
    return redirect("/getLocation")

  html = render_template('available.html', jobs=jobs, dists=dists)
  return make_response(html)


@app.route('/getLocation', methods=['GET'])
def getLocation():

  html = render_template('getLocation.html')
  return make_response(html)

@app.route('/bid', methods=['GET','POST'])
def bid():

  # get the job from the databse 
  jobId = ObjectId(request.args.get("id"))
  job = db.getOne('jobs', "_id", jobId)

  if request.method == "POST":
    # if bid is less than starting, give it to them
    newBid = int(request.form["bid"])
    if newBid < job["offer"]:
      db.updateOne("jobs", job["_id"], "offer", newBid)
      return redirect('/bid?id=' + str(job["_id"]))
    elif job["offer"] == job["starting"]:
      db.updateOne("jobs", job["_id"], "offer", newBid)
      return redirect('/bid?id=' + str(job["_id"]))


  # get current location from cookies
  userLat = request.cookies.get("userLat")
  userLon = request.cookies.get("userLon")

  # calc distances
  if userLat and userLon:
    distAway = hlp.distance( job["latOrig"], float(userLat), job["lonOrig"], float(userLon))
    distBetween = hlp.distance(job["latOrig"], job["latDest"], job["lonOrig"], job["lonDest"])
  else:
    return redirect("/getLocation")


  html = render_template('bid.html', job=job, mapbox_token=MAPBOX_TOKEN, distAway=distAway, distTo=distBetween)
  return make_response(html)
