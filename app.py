from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager,create_access_token,jwt_required, get_jwt_claims
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'herkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
jwt = JWTManager(app)
with app.app_context():
    db.create_all()
API_KEY = 'lxltzJmPcrGdGf3qIdKNoqzWfrl1v7oA12'



class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    userName = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(100), nullable = False)

class UserHistory(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable = False)
    location = db.Column(db.String(10), nullable = False)
    minimumTemperature = db.Column(db.Integer, nullable = False)
    maximumTemperature = db.Column(db.Integer, nullable = False)
    dayHasPrecipitation = db.Column(db.Boolean, nullable = False)
    nightHasPrecipitation = db.Column(db.Boolean, nullable = False)
    dayIconPhrase = db.Column(db.String(10), nullable = False)
    nightIconPhrase = db.Column(db.String(10), nullable = False)
    PrecipitationType = db.Column(db.String(10), nullable = False)


def getWeatherDataFromAPI(location):
    url = f'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location}?apikey={API_KEY}'
    response = requests.get(url)
    response = response.json()
    return response["DailyForecasts"]

@app.route('/login',methods = ['POST'])
def login():
    userName = request.json.get('username',None)
    password = request.json.get('password',None)
    if not userName or not password:
        return {"statusCode":403,"response":"Invalid username and password"}
    access_token = create_access_token(identity=userName)
    user = User(userName=userName,password=password)
    if user.password == password:
        return {'statusCode': 200, 'access_token':access_token}
    else:
        return {'statusCode':403}



@app.route('/getWeatherData',methods = ['POST'])
@jwt_required
def getWeatherData():
    try:
        current_user = get_jwt_claims()
        url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey=lxltzJmPcrGdGf3qIdKNoqzWfrl1v7oA&q=hosur'
        response = requests.get(url)
        location = response.json()
        weather_data = getWeatherDataFromAPI(location[0]["Key"])
        data = {
            "location": location[0]["LocalizedName"], 
            "minimumTemperature": weather_data[0]["Temperature"]["Minimum"]["Value"],
            "maximumTemperature":weather_data[0]["Temperature"]["Maximum"]["Value"],
            "dayHasPrecipitation" :weather_data[0]["Day"]["HasPrecipitation"] ,
            "nightHasPrecipitation":weather_data[0]["Night"]["HasPrecipitation"] ,
            "dayIconPhrase":weather_data[0]["Day"]["IconPhrase"] ,
            "nightIconPhrase" :weather_data[0]["Night"]["IconPhrase"] ,
            "PrecipitationType":weather_data[0]["Day"]["PrecipitationType"]
        }
        search_entry = UserHistory(user_id = current_user,location = location[0]["LocalizedName"], minimumTemperature = weather_data[0]["Temperature"]["Minimum"]["Value"],maximumTemperature=weather_data[0]["Temperature"]["Maximum"]["Value"],dayHasPrecipitation =weather_data[0]["Day"]["HasPrecipitation"] ,nightHasPrecipitation =weather_data[0]["Night"]["HasPrecipitation"] ,dayIconPhrase =weather_data[0]["Day"]["IconPhrase"] ,nightIconPhrase =weather_data[0]["Night"]["IconPhrase"] ,PrecipitationType = weather_data[0]["Day"]["PrecipitationType"])
        db.session.add(search_entry)
        db.session.commit()
        return {"statusCode": 200 , "response":data}
    except Exception as e:
        print(str(e))
        return {"statusCode": 404 , "response":"Data Not Found"}
     


if __name__ == '__main__':
    db.create_all()
    app.run(debug = True)