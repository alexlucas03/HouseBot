from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import datetime
from collections import defaultdict
from dish import Dish
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

dishes = []
total_points = 0
start_date_str = "2024-09-24"
end_date_str = "2024-12-13"
start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

types = ['lunch', 'dinner', 'x1']
type_index = 0

delta = datetime.timedelta(days=1)
current_date = start_date
today = datetime.date.today().strftime('%Y-%m-%d')
duration = (end_date - start_date).days
ownersArray = [None] * duration * 3

#September
ownersArray[0] = 'ted'
ownersArray[1] = 'ted'
ownersArray[2] = 'dimov'
ownersArray[3] = 'az'
ownersArray[4] = 'ted'
ownersArray[5] = 'dimov'
ownersArray[6] = 'john'
ownersArray[7] = 'truman'
ownersArray[8] = 'dimov'
ownersArray[10] = 'truman'
ownersArray[11] = 'christian'
ownersArray[12] = 'ted'
ownersArray[13] = 'ted'
ownersArray[14] = 'ted'
ownersArray[15] = 'ted'
ownersArray[16] = 'christian'

#October
ownersArray[17] = 'dominic'
ownersArray[18] = 'dominic'
ownersArray[19] = 'dimov'
ownersArray[20] = 'az'
ownersArray[21] = 'christian'
ownersArray[22] = 'christian'
ownersArray[24] = 'truman'
ownersArray[25] = 'dimov'
ownersArray[26] = 'diego'
ownersArray[27] = 'truman'
ownersArray[28] = 'christian'
ownersArray[29] = 'david'
ownersArray[30] = 'dimov'
ownersArray[31] = 'dominic'
ownersArray[32] = 'christian'
ownersArray[33] = 'christian'
ownersArray[34] = 'dominic'
ownersArray[35] = 'dominic'
ownersArray[36] = 'dimov'
ownersArray[38] = 'david'
ownersArray[39] = 'diego'
ownersArray[41] = 'truman'
ownersArray[42] = 'dimov'
ownersArray[43] = 'diego'
ownersArray[44] = 'mat'
ownersArray[45] = 'leif'
ownersArray[46] = 'david'
ownersArray[47] = 'dimov'
ownersArray[48] = 'dominic'
ownersArray[49] = 'christian'
ownersArray[50] = 'diego'
ownersArray[51] = 'tony'
ownersArray[52] = 'dominic'
ownersArray[53] = 'dimov'
ownersArray[54] = 'az'
ownersArray[55] = 'david'
ownersArray[56] = 'leif'
ownersArray[58] = 'truman'
ownersArray[59] = 'dimov'
ownersArray[60] = 'diego'
ownersArray[61] = 'truman'
ownersArray[62] = 'leif'
ownersArray[63] = 'mat'
ownersArray[64] = 'dimov'
ownersArray[65] = 'arohan'
ownersArray[67] = 'eyen'
ownersArray[68] = 'tony'
ownersArray[69] = 'az'
ownersArray[70] = 'diego'
ownersArray[71] = 'az'
ownersArray[72] = 'david'
ownersArray[73] = 'leif'
ownersArray[75] = 'az'
ownersArray[76] = 'diego'
ownersArray[77] = 'diego'
ownersArray[78] = 'arohan'
ownersArray[79] = 'leif'
ownersArray[80] = 'christian'
ownersArray[81] = 'stanley'
ownersArray[82] = 'arohan'
ownersArray[84] = 'eyen'
ownersArray[85] = 'tony'
ownersArray[87] = 'leif'
ownersArray[88] = 'az'
ownersArray[90] = 'leif'
ownersArray[93] = 'eyen'

#November
ownersArray[94] = 'diego'
ownersArray[95] = 'stanley'
ownersArray[96] = 'stanley'
ownersArray[97] = 'john'
ownersArray[98] = 'dimov'
ownersArray[102] = 'tony'
ownersArray[104] = 'dimov'
ownersArray[106] = 'david'
ownersArray[107] = 'leif'
ownersArray[108] = 'eyen'
ownersArray[110] = 'leif'
ownersArray[111] = 'john'
ownersArray[113] = 'leif'
ownersArray[114] = 'mat'
ownersArray[115] = 'stanley'
ownersArray[116] = 'arohan'
ownersArray[119] = 'tony'
ownersArray[121] = 'leif'
ownersArray[122] = 'eyen'
ownersArray[131] = 'mat'
ownersArray[133] = 'arohan'
ownersArray[136] = 'tony'
ownersArray[138] = 'leif'
ownersArray[144] = 'leif'
ownersArray[141] = 'leif'
ownersArray[145] = 'john'
ownersArray[147] = 'eyen'
ownersArray[148] = 'stanley'
ownersArray[149] = 'stanley'
ownersArray[150] = 'arohan'
ownersArray[153] = 'tony'
ownersArray[160] = 'eyen'
ownersArray[162] = 'john'

#December
ownersArray[165] = 'john'
ownersArray[166] = 'stanley'
ownersArray[167] = 'arohan'
ownersArray[169] = 'stanley'
ownersArray[172] = 'stanley'
ownersArray[175] = 'stanley'
ownersArray[181] = 'eyen'
ownersArray[186] = 'eyen'
ownersArray[188] = 'eyen'
ownersArray[198] = 'stanley'

owner_to_userid = {
    'ted': '86703628',
    'dominic': '104427870',
    'truman': '106396551',
    'dimov': '104722123',
    'david': '68279200',
    'mat': '107719028',
    'christian': '93350644',
    'diego': '118125359',
    'az': '105887162',
    'leif': '89734509',
    'john': '104094443', #aussie user id
    'tony': '115601455', #every tuesday from 8/15 for 7 weeks
    'arohan': '115802749',
    'stanley': '65365057',
    'eyen': '115945245',
    'brandon': '117008618',
    'jo': '125330287',
    'jase': '123732691',
    'sam': '119855908',
    'tanner': '125114421',
    'noah': '107162478',
    'aidan': '23716109',
    'kim': '123717364',
    'admin': '1'
}

pick_order = ['ted', 'dominic', 'truman', 'dimov', 'david', 'mat', 'christian', 'diego', 'az', 'leif', 'john', 'tony', 'arohan', 'stanley', 'eyen', 'brandon', 'jo', 'jase', 'sam', 'tanner', 'noah', 'aidan', 'kim']

i = 0
while current_date <= end_date:
    day_of_week = current_date.strftime("%A")
    
    if day_of_week != "Saturday":
        if day_of_week == "Sunday" and type_index == 0:
            type_index = 1
            total_points += 1

        owner = ownersArray[i]
        
        dish = Dish(date=current_date, owner=owner, type=types[type_index])
        dishes.append(dish)
        i += 1
        
        if types[type_index] == 'x1':
            current_date += delta
        
        type_index = (type_index + 1) % len(types)
 
    else:
        current_date += delta

grouped_dishes = defaultdict(lambda: defaultdict(list))
for dish in dishes:
    if dish.type == 'dinner' or dish.type == 'lunch':
        total_points += 2
    elif dish.type == 'x1':
        total_points += 1
    month = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%B")
    day = datetime.datetime.strptime(dish.date, "%Y-%m-%d").strftime("%d")
    grouped_dishes[month][day].append(dish)

points = total_points / len(owner_to_userid)
points_order = [int(points)] * len(pick_order)
original_points = [int(points)] * len(pick_order)
summed_points = int(points) * len(pick_order)

count = 0
while(summed_points < total_points):
    points_order[len(points_order) - 1 - count] += 1
    summed_points += 1
    count += 1

@app.route('/send-messages', methods=['POST'])
def send_groupme_messages():
    lunch_userid = owner_to_userid.get(lunch_owner, None)
    dinner_userid = owner_to_userid.get(dinner_owner, None)
    x1_userid = owner_to_userid.get(x1_owner, None)
    
    url = "https://api.groupme.com/v3/bots/post"

    def send_message(message, owner, owner_userid, owner_loci_start, owner_loci_end):
        data = {
            "text": message,
            "bot_id": "c9ed078f3de7c89547308a050a",
        }
        if owner != 'Not Assigned':
            data["attachments"] = [
                {
                    "type": "mentions",
                    "user_ids": [owner_userid],
                    "loci": [[owner_loci_start, owner_loci_end]]
                }
            ]
        response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        return response

    # Send lunch message
    lunch_message = f"Lunch: @{lunch_owner}"
    send_message(lunch_message, lunch_owner, lunch_userid, 7, 7 + len(lunch_owner))

    # Send dinner message
    dinner_message = f"Dinner: @{dinner_owner}"
    send_message(dinner_message, dinner_owner, dinner_userid, 8, 8 + len(dinner_owner))

    # Send x1 message
    x1_message = f"x1: @{x1_owner}"
    send_message(x1_message, x1_owner, x1_userid, 4, 4 + len(x1_owner))

    return redirect(url_for('index'))

@app.route('/')
def index():
    global lunch_owner, dinner_owner, x1_owner
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    if start_date.strftime('%Y-%m-%d') <= today <= end_date.strftime('%Y-%m-%d'):
        today_lunch = None
        today_dinner = None
        today_x1 = None

        for dish in dishes:
            if dish.date == today:
                if dish.type == "lunch":
                    today_lunch = dish
                elif dish.type == "dinner":
                    today_dinner = dish
                elif dish.type == "x1":
                    today_x1 = dish
        
        lunch_owner = today_lunch.owner if today_lunch and today_lunch.owner else 'Not Assigned'
        dinner_owner = today_dinner.owner if today_dinner and today_dinner.owner else 'Not Assigned'
        x1_owner = today_x1.owner if today_x1 and today_x1.owner else 'Not Assigned'

    recalculate_points()
    return render_template('index.html', grouped_dishes=grouped_dishes, user=user, points_order=points_order, pick_order=pick_order)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['user'] = username
        if username in pick_order or username == 'admin':
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/change-owner', methods=['POST'])
def change_owner():
    data = request.get_json()
    dish_date = data.get('date')
    dish_type = data.get('type')
    new_owner = data.get('owner')

    for index, dish in enumerate(dishes):
        if dish.date == dish_date and dish.type == dish_type:
            dish.owner = new_owner
            ownersArray[index] = new_owner
            return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Dish not found'}), 404

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def recalculate_points():
    global total_points, points_order

    points_order = original_points.copy()
    for dish in dishes:
        if dish.owner:
            index = pick_order.index(dish.owner)
            if dish.weekday == 'Sunday' and dish.type == 'dinner':
                points_order[index] -= 3
            elif dish.weekday != 'Sunday' and dish.type == 'dinner' or dish.type == 'lunch':
                points_order[index] -= 2
            elif dish.type == 'x1':
                points_order[index] -= 1