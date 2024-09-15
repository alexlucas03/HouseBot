from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import time
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather, Pause
from callee import Callee
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
account_sid = 'AC597bdd2caf2d68637b0010e1dd3e415c'
auth_token = 'b86c0a388dafcd964c5a57568b41c7e8'
client = Client(account_sid, auth_token)
active_user = None
database = {
    'alex': {'password': '12', 'num': '2066987256'},
}

callees = []
to_call = []
calling = []
called = []
accepted = []
tags = []
custom_issue = ''
terminated = False
prim_num = 0
sec_num = 0
original_data = pd.DataFrame()

@app.route('/')
def index():
    global callees, to_call, calling, called, accepted, tags, custom_issue, original_data, terminated, prim_num, sec_num, database, active_user
    
    if not active_user:
        return redirect(url_for('login'))

    updates()

    return render_template('index.html',
                           to_call=to_call,
                           calling=calling,
                           called=called,
                           accepted=accepted,
                           callees=callees,
                           custom_issue=custom_issue,
                           active_user=active_user)

@app.route('/login', methods=['POST', 'GET'])
def login():
    global active_user
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', info='Form data missing!')
        
        if username not in database:
            return render_template('login.html', info='Invalid User')
        else:
            if database[username]['password'] != password:
                return render_template('login.html', info='Invalid Password')
            else:
                active_user = username
                return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    global active_user
    active_user = None
    return redirect(url_for('login'))

@app.route('/start-calls', methods=['POST'])
def start_calls():
    global callees, to_call, calling, called, terminated

    if len(to_call) == 0:
        return 400

    loop_for_calls(1)
    loop_for_calls(2)

    updates()
    return '', 200

def loop_for_calls(term_round):
    global terminated, to_call, calling, called, callees, round

    round = term_round

    if round == 1:
        terminated = False

    if round == 2 and (not terminated and not sec_handler()):
        for callee in callees:
            if callee not in called:
                to_call.append(callee)

    while len(to_call) > 0 or len(calling) > 0:
        current = to_call.pop(0)
        calling.append(current)

        updates()

        if (round == 1 and prim_handler()) or terminated:
            break

        call_sid = make_call(current.num)

        while True:
            call = client.calls(call_sid).fetch()
            if call.status in ['completed', 'failed', 'canceled', 'no-answer']:
                if current not in called:
                    called.append(current)
                if current in calling:
                    calling.remove(current)
                break
            time.sleep(1)

        if (round == 1 and prim_handler()) or (round == 2 and sec_handler()) or terminated:
            to_call = []
            updates()
            break

        updates()

    return '', 200

def make_call(num):
    call_num = '+1' + str(num)

    call = client.calls.create(
        to=call_num,
        from_="+18444750366",
        url = url_for('process', _external=True),
    )
    return call.sid

@app.route('/process', methods=['POST', 'GET'])
def process():
    return process_calls(outgoing=True)

@app.route('/answer', methods=['POST', 'GET'])
def answer():
    return process_calls(outgoing=False)

def process_calls(outgoing):
    global custom_issue, accepted, caller_number, called, callees, round

    resp = VoiceResponse()
    digits = request.form.get('Digits')
    current = None
    if not outgoing:
        print(request.form.get('From'))
        caller_number = int(request.form.get('From').removeprefix('+1'))
        for callee in callees:
            if int(caller_number) == int(callee.num):
                current = callee
    else:
        current = calling[0]
        caller_number = current.num

    if digits:
        if digits == '1':
            resp.say('You accepted')
            accepted.append(current)
            print(f'accepted list: {accepted}')
            accept_call(current.name)
        elif digits == '2':
            resp.say('You declined')
        else:
            resp.say('Invalid input. Call back to accept or you are considered declined.')
    else:
        if outgoing:
            gather = Gather(input="dtmf", action="/process", timeout=10, numDigits=1)
        else:
            if eligible():
                gather = Gather(input="dtmf", action="/answer", timeout=10, numDigits=1)
            else:
                resp.say(f"Hello, due to union rules, we can not let you come in at this time, we will give you a call back when you are eligible.")
                return str(resp)
        gather.pause(length=1)

        gather.say(f"Hello, PCA has an issue: {custom_issue}. Can you help? Press 1 to accept, Press 2 to decline.")
        resp.append(gather)

    if round == 2:
        round = 0
    updates()
    return str(resp)

def eligible():
    global callees, caller_number

    if terminated and round != 1 and round != 2:
        return True
    if len(calling) == 0:
        inOrderIndex = len(callees)
    else:
        inOrderIndex =callees.index(calling[0])

    print(f'caller number: {caller_number}')
    accepterIndex = [i for i, callee in enumerate(callees) if int(callee.num) == int(caller_number)][0]
    print(f'accepter index: {accepterIndex}')
    if inOrderIndex >= accepterIndex:
        return True
    else:
        for index, callee in enumerate(to_call):
            if callees.index(callee) >= accepterIndex:
                to_call.insert(index, callee)
                break
    updates()
    return False

def accept_call(acceptedName):
    global active_user

    call_num = f"+1{database[active_user]['num']}"
    callback_url = url_for('handle_accept', name=acceptedName, _external=True)
    call = client.calls.create(
        to=call_num,
        from_="+18444750366",
        url=callback_url
    )
    return call.sid

@app.route('/handle_accept', methods=['POST', 'GET'])
def handle_accept():
    name = request.args.get('name')
    response = VoiceResponse()
    response.pause(length=1)
    response.say(f"{name} accepted.")
    return str(response), 200

@app.route('/terminate-calls', methods=['POST'])
def terminate_calls():
    global to_call, terminated

    to_call.clear()
    terminated = True

    updates()
    return '', 200

@app.route('/upload', methods=['POST'])
def upload_file():
    global callees, tags, to_call, calling, called, accepted, original_data

    file = request.files['upload']

    if file and file.filename.endswith('.csv'):
        file_content = io.StringIO(file.read().decode('utf-8'))

        original_data = pd.read_csv(file_content)

        callees = []
        tags = []
        to_call = []
        calling = []
        called = []
        accepted = []

        for index, row in original_data.iterrows():
            callee = Callee(str(row[0]), str(row[1]), str(row[2]))
            if len(callee.num) == 10 and callee not in callees:
                callees.append(callee)
                if '' not in tags:
                    tags.append('')
                if 'all' not in tags:
                    tags.append('all')
                if row[2] not in tags:
                    tags.append(row[2])

        updates()

    return '', 200


@app.route('/filter', methods=['POST'])
def filter():
    global callees, to_call, tags

    data = request.get_json()
    selected_tag = data['tag']
    if selected_tag == 'all':
        to_call = callees
    elif selected_tag != '':
        to_call = [callee for callee in callees if callee.tag == selected_tag]

    if '' in tags:
        tags.remove('')

    updates()
    return '', 200

@app.route('/prim', methods=['POST'])
def prim():
    global prim_num
    data = request.get_json()
    prim_num = int(data.get('prim_num'))
    updates()
    return '', 200

def prim_handler():
    global terminated
    if prim_num == 0 or (prim_num > 0 and len(accepted) >= prim_num) or (not to_call and not calling and len(accepted) < prim_num):
        return True
    return False

@app.route('/sec', methods=['POST'])
def sec():
    global sec_num
    data = request.get_json()
    sec_num = int(data.get('sec_num'))
    updates()
    return '', 200

def sec_handler():
    global terminated
    if (sec_num == 0 and len(accepted) >= prim_num) or (sec_num > 0 and len(accepted) >= prim_num + sec_num):
        return True
    return False

@app.route('/issue', methods=['POST'])
def issue():
    global custom_issue
    data = request.get_json()
    custom_issue = data.get('issue')
    updates()
    return '', 200

def updates():
    data = {
        'to_call': [callee.name for callee in to_call],
        'calling': [callee.name for callee in calling],
        'called': [callee.name for callee in called],
        'accepted': [callee.name for callee in accepted],
        'callees': [callee.to_dict() for callee in callees],
        'custom_issue': custom_issue,
        'tags': tags,
        'prim_num': prim_num,
        'sec_num': sec_num,
    }
    
    channel.publish('update', data)
