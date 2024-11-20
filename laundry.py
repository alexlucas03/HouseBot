class Laundry:
    def __init__(self, name, appliance, rank, checksleft):
        self.name = name
        self.appliance = appliance
        self.rank = rank
        self.checksleft = checksleft

    def to_dict(self):
        return {
            'name': self.name,
            'userID': self.appliance,
            'pickOrder': self.rank,
            'checksleft': self.checksleft
        }

# add this to app.py
"""
@app.route("/laundry", methods=['POST', 'GET'])
def laundry():
    global dryer1, washer, dryer2, nextid, nextrank
    laundry_rows = db.session.execute(text("SELECT * FROM laundry"))
    dryer1 = []
    washer = []
    dryer2 = []
    nextid = 0
    nextrank = 0
    for row in laundry_rows:
        laundry_obj = Laundry(name=row.name, appliance=row.appliance, rank=row.rank, checksleft=row.checksleft)
        nextid = max(nextid, int(row.id) + 1)
        nextrank = max(nextrank, int(row.rank) + 1)
        if laundry_obj.appliance == 'dryer1':
            dryer1.append(laundry_obj)
        elif laundry_obj.appliance == 'washer':
            washer.append(laundry_obj)
        elif laundry_obj.appliance == 'dryer2':
            dryer2.append(laundry_obj)

    dryer1 = sorted(dryer1, key=lambda x: x.rank)
    washer = sorted(washer, key=lambda x: x.rank)
    dryer2 = sorted(dryer2, key=lambda x: x.rank)
    max_length = max(len(dryer1), len(washer), len(dryer2))

    return render_template('laundry.html', dryer1=dryer1, washer=washer, dryer2=dryer2, max_length=max_length)

@app.route('/addtodryer1', methods=['POST'])
def addtodryer1():
    global dryer1, nextid, nextrank
    id = nextid
    name = request.form['namedryer1']
    db.session.execute(text(f"INSERT INTO laundry VALUES ('{str(name)}', 'dryer1', '{str(nextrank)}', '{str(id)}', '1')"))
    db.session.commit()
    return redirect(url_for('laundry'))

@app.route('/addtowasher', methods=['POST'])
def addtowasher():
    global washer, nextid, nextrank
    id = nextid
    name = request.form['namewasher']
    db.session.execute(text(f"INSERT INTO laundry VALUES ('{str(name)}', 'washer', '{str(nextrank)}', '{str(id)}', '1')"))
    db.session.commit()
    return redirect(url_for('laundry'))

@app.route('/addtodryer2', methods=['POST'])
def addtodryer2():
    global dryer2, nextid, nextrank
    id = nextid
    name = request.form['namedryer2']
    db.session.execute(text(f"INSERT INTO laundry VALUES ('{str(name)}', 'dryer2', '{str(nextrank)}', '{str(id)}', '1')"))
    db.session.commit()
    return redirect(url_for('laundry'))

@app.route('/deletecurrentdryer1')
def deletecurrentdryer1():
    global dryer1
    minrank = min(dryer1, key=lambda x: x.rank)
    minrank_obj = db.session.execute(text(f"SELECT * FROM laundry WHERE rank = :rank AND appliance = 'dryer1'"),{"rank": minrank.rank}).fetchone()
    if minrank_obj:
        if minrank_obj.checksleft == '0':
            db.session.execute(text(f"DELETE FROM laundry WHERE rank = :rank AND appliance = 'dryer1'"),{"rank": minrank.rank})
        elif minrank_obj.checksleft == '1':
            db.session.execute(text(f"UPDATE laundry SET checksleft = '0' WHERE rank = :rank AND appliance = 'dryer1'"),{"rank": minrank.rank})
        db.session.commit()

        return jsonify({"message": "Success"})
    else:
        return jsonify({"message": "No matching dryer1 found"}), 404

@app.route('/deletecurrentwasher')
def deletecurrentwasher():
    global washer
    minrank = min(washer, key=lambda x: x.rank)
    minrank_obj = db.session.execute(text(f"SELECT * FROM laundry WHERE rank = :rank AND appliance = 'washer'"),{"rank": minrank.rank}).fetchone()
    if minrank_obj:
        if minrank_obj.checksleft == '0':
            db.session.execute(text(f"DELETE FROM laundry WHERE rank = :rank AND appliance = 'washer'"),{"rank": minrank.rank})
        elif minrank_obj.checksleft == '1':
            db.session.execute(text(f"UPDATE laundry SET checksleft = '0' WHERE rank = :rank AND appliance = 'washer'"),{"rank": minrank.rank})
        db.session.commit()
        
        return jsonify({"message": "Success"})
    else:
        return jsonify({"message": "No matching washer found"}), 404

@app.route('/deletecurrentdryer2')
def deletecurrentdryer2():
    global dryer2
    minrank = min(dryer2, key=lambda x: x.rank)
    minrank_obj = db.session.execute(text(f"SELECT * FROM laundry WHERE rank = :rank AND appliance = 'dryer2'"),{"rank": minrank.rank}).fetchone()
    if minrank_obj:
        if minrank_obj.checksleft == '0':
            db.session.execute(text(f"DELETE FROM laundry WHERE rank = :rank AND appliance = 'dryer2'"),{"rank": minrank.rank})
        elif minrank_obj.checksleft == '1':
            db.session.execute(text(f"UPDATE laundry SET checksleft = '0' WHERE rank = :rank AND appliance = 'dryer2'"),{"rank": minrank.rank})
        db.session.commit()

        return jsonify({"message": "Success"})
    else:
        return jsonify({"message": "No matching dryer2 found"}), 404
"""