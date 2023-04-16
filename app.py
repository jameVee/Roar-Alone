#Import Library
import os
from flask import Flask
from flask import request
from flask import make_response,render_template
from function_chatbot import *
from requests.exceptions import HTTPError
from flask_restful import Api,Resource,abort,marshal_with,fields,reqparse #สร้าง API และ Resource และ abort คือตัวกำหนดข้อความที่เราต้องการให้ตอบกลับไป
from flask_sqlalchemy import SQLAlchemy
from SQLite_RoarDatabase import Query

#---- Google Sheet ----
import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
cerds = ServiceAccountCredentials.from_json_keyfile_name("cerds.json", scope)
client = gspread.authorize(cerds)
sheet = client.open("Chatbot_notify").worksheet('Sheet1')

#-------------------------------------

# Flask
app = Flask(__name__)

####################### Save data #######################

# Database
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database3.db"
api = Api(app) # ทำให้ app กลายเป็น api

class RecordModel(db.Model):
    User_ID = db.Column(db.String(9000),primary_key=True)
    Trip_name = db.Column(db.String(9000),nullable=False)
    Participants_name = db.Column(db.String(9000),nullable=False)
    Accommodation_name = db.Column(db.String(9000),nullable=False)
    Restaurant_name = db.Column(db.String(9000),nullable=False)
    Expenses_total = db.Column(db.String(9000),nullable=False)
    def __repr__(self): # จัดรูปแบบของ object ให้อยู่ในรูปแบบที่เราต้องการ โดยใช้ฟังก์ชัน represent object (repr)
        return f"Record(Trip_name={Trip_name},Participants_name={Participants_name},Accommodation_name={Accommodation_name},Restaurant_name={Restaurant_name},Expenses_total={Expenses_total})"

db.create_all() # คำสั่งนี้จะต้องเขียนต่อท้าย Model (RecordModel) เท่านั้น เพราะ Model คือการกำหนดโครงสร้างมาก่อน

# Request Parser for record data
record_add_args = reqparse.RequestParser()
record_add_args.add_argument("Trip_name",type=str) # help จะส่งการแจ้งเตือนกลับในกรณีที่เราระบุ argument ไม่ตรง type
record_add_args.add_argument("Participants_name",type=str)
record_add_args.add_argument("Accommodation_name",type=str)
record_add_args.add_argument("Restaurant_name",type=str)
record_add_args.add_argument("Expenses_total",type=str)

# เป็นการนิยามขึ้นมา แต่ยังไม่ถูกเรียกใช้ (จัดเตรียมกฏเกณฑ์ไว้ก่อน)
resource_field = {
    "User_ID":fields.String,
    "Trip_name":fields.String,
    "Participants_name":fields.String,
    "Accommodation_name":fields.String,
    "Restaurant_name":fields.String,
    "Expenses_total":fields.String
}

# Check validate request
def notFoundID(User_ID):
    if User_ID not in record:
        abort(404,message = "ไม่พบข้อมูลที่คุณร้องขอ")

# Design
class Record(Resource):
    @marshal_with(resource_field)
    def get(self,User_ID): # เรียกดูข้อมูล
        notFoundID(User_ID)
        return record[User_ID] # {"key","value"}

    @marshal_with(resource_field) # เรียกใช้งาน resource_field
    def post(self,User_ID): # เพิ่มข้อมูลเข้าไปหรือบันทึกข้อมูล

        args = record_add_args.parse_args()
        record = RecordModel(User_ID=User_ID,Trip_name=args["Trip_name"], Participants_name=args["Participants_name"] , Accommodation_name=args["Accommodation_name"] , Restaurant_name=args["Restaurant_name"] , Expenses_total=args["Expenses_total"]) ##### บันทึก
        db.session.add(record) #####
        db.session.commit() # เปลี่ยนแปลงข้อมูลในฐานข้อมูล #####
        return record,201 # 201 คือการเพิ่มข้อมูลลงฐานข้อมูล #####

# Call
api.add_resource(Record,"/record/<string:User_ID>")

####################### Save data #######################


@app.route('/ACCOMMODATION/<place_id>')
def index(place_id):
    url = f"https://tatapi.tourismthailand.org/tatapi/v5/accommodation/{place_id}"

    try:
        Ac = requests.get(url,headers=my_headers).json()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

    return render_template("GetAccommodationDetail.html",Ac=Ac['result'])


@app.route('/ATTRACTION/<place_id>')
def GetAttractionDetail(place_id):
    url = f"https://tatapi.tourismthailand.org/tatapi/v5/attraction/{place_id}"

    try:
        At = requests.get(url,headers=my_headers).json()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6


    return render_template("GetAttractionDetail.html",At=At['result'])


@app.route('/RESTAURANT/<place_id>')
def GetRestaurantDetail(place_id):
    url = f"https://tatapi.tourismthailand.org/tatapi/v5/restaurant/{place_id}"

    try:
        Re = requests.get(url,headers=my_headers).json()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

    return render_template("GetRestaurantDetail.html",Re=Re['result'])

@app.route('/Route/<place_id>')
def GetRecommendedRouteDetail(place_id):
    url = f"https://tatapi.tourismthailand.org/tatapi/v5/routes/{place_id}"

    try:
        R = requests.get(url,headers=my_headers).json()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

    return render_template("GetRecommendedRouteDetail.html",R = R['result'])

@app.route('/', methods=['POST']) #Using post as a method
def MainFunction():

    #Getting intent from Dailogflow
    question_from_dailogflow_raw = request.get_json(silent=True, force=True)
    if question_from_dailogflow_raw["queryResult"]["intent"]["displayName"] == 'place_request':
        answer_from_bot = place_request(question_from_dailogflow_raw)
    elif question_from_dailogflow_raw["queryResult"]["intent"]["displayName"] == 'place_recommendation':
        answer_from_bot = place_recommendation(question_from_dailogflow_raw)
    elif question_from_dailogflow_raw["queryResult"]["intent"]["displayName"] == 'trip_recommendation':
        answer_from_bot = trip_recommendation(question_from_dailogflow_raw)
    else:
        #Call generating_answer fun
        answer_from_bot = generating_answer(question_from_dailogflow_raw)
    #Make a respond back to Dailogflow
    r = make_response(answer_from_bot)
    r.headers['Content-Type'] = 'application/json' #Setting Content Type
    return r


def generating_answer(question_from_dailogflow_dict):

    #Print intent that recived from dialogflow.
    print(json.dumps(question_from_dailogflow_dict, indent=4 ,ensure_ascii=False))

    #Getting intent name form intent that recived from dialogflow.
    intent_group_question_str = question_from_dailogflow_dict["queryResult"]["intent"]["displayName"]

    #Select function for answering question
    if intent_group_question_str == 'หิวจัง':
        answer_str = menu_recormentation()
    elif intent_group_question_str == 'คำนวนน้ำหนัก':
        answer_str = BMI_calculation(question_from_dailogflow_dict)
    elif intent_group_question_str == 'info_schedule':
        answer_str = info_schedule(question_from_dailogflow_dict)
    elif intent_group_question_str == 'save_schedule - yes':
        answer_str = save_schedule(question_from_dailogflow_dict)
    elif intent_group_question_str == 'info_data':
        answer_str = info_data(question_from_dailogflow_dict)
    elif intent_group_question_str == 'save_data - yes':
        answer_str = save_data(question_from_dailogflow_dict)
    elif intent_group_question_str == 'request_data':
        answer_str = request_data(question_from_dailogflow_dict)
    else: answer_str = "ขอโทษนะคะ ไม่เข้าใจ คุณต้องการอะไร"

    #Build answer dict
    answer_from_bot = {"fulfillmentText": answer_str}

    #Convert dict to JSON
    answer_from_bot = json.dumps(answer_from_bot, indent=4)
    return answer_from_bot


def menu_recormentation(): #ฟังก์ชั่นสำหรับเมนูแนะนำ
    menu_name = 'ข้าวขาหมู'
    answer_function = menu_name + ' สิ น่ากินนะ'
    return answer_function

def BMI_calculation(respond_dict): #Function for calculating BMI

    #Getting Weight and Height
    weight_kg = float(respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Weight.original"])
    height_cm = float(respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Height.original"])

    #Calculating BMI
    BMI = weight_kg/(height_cm/100)**2
    if BMI < 18.5 :
        answer_function = "คุณผอมเกินไปนะ"
    elif 18.5 <= BMI < 23.0:
        answer_function = "คุณมีน้ำหนักปกติ"
    elif 23.0 <= BMI < 25.0:
        answer_function = "คุณมีน้ำหนักเกิน"
    elif 25.0 <= BMI < 30:
        answer_function = "คุณอ้วน"
    else :
        answer_function = "คุณอ้วนมาก"
    return answer_function

def info_schedule(respond_dict):
     time = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["time"][11:16]
     destination = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["destination"]
     date = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["date"][0:10]
     return f'คุณจะไปวันที่ {date} เวลา {time} น. ที่ {destination} ใช่มั้ยคะ?'


def save_schedule(respond_dict):
    time = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["time"][11:16]
    destination = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["destination"]
    date = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["date"][0:10]
    userId = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    sheet.insert_row([userId,destination,date,time],2)
    return "บันทึกการแจ้งเตือนเรียบร้อยแล้วค่ะ"

def info_data(respond_dict):
    Trip = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Trip"]
    Participants = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Participants"]
    Accommodation = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Accommodation"]
    Restaurant = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Restaurant"] # ['business-name'] ใช้ในกรณี Restaurant เซ็ตใน Dialogflow เป็น location
    Expenses = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Expenses"]
    # return f'คุณจะบันทึกชื่อทริปกับชื่อโรงแรมว่า {Trip} กับ {Hotel} ใช่มั้ยค่ะ?'
    return f'คุณจะบันทึกชื่อทริปกับชื่อโรงแรมว่า {Trip} กับ {Participants} กับ {Accommodation} กับ {Restaurant} กับ {Expenses} ใช่มั้ยค่ะ?'

def save_data(respond_dict):
    userId = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    Trip = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Trip"]
    Participants = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Participants"]
    Accommodation = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Accommodation"]
    Restaurant = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Restaurant"]
    Expenses = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Expenses"]
    # record
    URL = f"https://roarchatbot.herokuapp.com/record/{userId}"
    myobj = {'Trip_name':Trip , 'Participants_name':Participants , 'Accommodation_name':Accommodation , 'Restaurant_name':Restaurant , 'Expenses_total':Expenses}
    x = requests.post(URL, data = myobj)
    # sheet2.insert_row([Trip,Hotel],2)
    return "บันทึกเรียบร้อยแล้วค่ะ"

def request_data(respond_dict):
    User_ID = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    list_Trip = Query(User_ID)
    if list_Trip == []:
        return "ไม่พบชื่อทริปที่คุณบันทึกเข้ามาค่ะ"
    answer = ""
    for i in list_Trip:
        answer += f"ชื่อทริป : {i[1]} และชื่อผู้ร่วมทริป : {i[2]} และสถานที่พัก : {i[3]} และชื่อร้านอาหาร : {i[4]} และยอดรวมค่าใช้จ่ายทั้งหมด : {i[5]}\n"
    return answer

#Flask
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
