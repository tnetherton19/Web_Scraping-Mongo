from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pymongo
import scrape_mars

#instance of Flask
app = Flask(__name__)
conn = 'mongodb://localhost:27017/'
client = pymongo.MongoClient(conn)
db = client.marsscrape_db

# Route to render index.html template using data from Mongo
@app.route("/")
def home():

    # Find one record of data from the mongo database
    data = db.items.find_one()
    #print("THIS IS WHERE YOUR PRINT STMNT IS")
    #print(data)
    # Return template and data
    return render_template("index.html", data=data)

@app.route("/scrape")
def scrape():

    data = db.items
    scraped_data = scrape_mars.scrape()
    data.update({}, scraped_data, upsert=True)

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)