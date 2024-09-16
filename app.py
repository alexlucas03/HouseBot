from flask import Flask, render_template, request, redirect, url_for
import datetime
from dish import Dish

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
active_user = None

dishes = []
startDate = "2024-09-15"
endDate = "2024-12-08"
start_date_obj = datetime.datetime.strptime(startDate, "%Y-%m-%d")
end_date_obj = datetime.datetime.strptime(endDate, "%Y-%m-%d")
lunch = True
dinner = False
x1 = False

delta = datetime.timedelta(days=1/3)
current_date = start_date_obj

while current_date <= end_date_obj:
        if lunch:
            dish = Dish(date=current_date.strftime("%Y-%m-%d"), owner="", type="lunch")
            dishes.append(dish)
            current_date += delta
            lunch = False
            dinner = True
            x1 = False
        elif dinner:
            dish = Dish(date=current_date.strftime("%Y-%m-%d"), owner="", type="dinner")
            dishes.append(dish)
            current_date += delta
            lunch = True
            dinner = False
            x1 = True
        elif x1:
            dish = Dish(date=current_date.strftime("%Y-%m-%d"), owner="", type="x1")
            dishes.append(dish)
            current_date += delta
            lunch = True
            dinner = False
            x1 = False

@app.route('/')
def index():
    return render_template('index.html',
                           dishes=dishes)


def get_day_of_week(date):
    """Gets the day of the week for a given date string."""

    # Get the day of the week as a string
    day_of_week = date.strftime("%A")

    return day_of_week

if __name__ == '__main__':
    app.run(debug=True)