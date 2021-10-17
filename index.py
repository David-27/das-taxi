from flask import Flask
from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio.platform.flask import webio_view
import dataset as dt
import pandas as pd
import plotly.express as px
import taxi_cluster_profits as tcp
import datetime
import plotly.graph_objects as go

app = Flask(__name__)
op = {}
op['New Request'] = 'window.location.reload()'


# def validate_month(info):
#     if (info['month'] in dt.month_29) & (info['day_month'] > 29):
#         return ('day_month', 'Bad Month number')
#     if (info['month'] in dt.month_30) & (info['day_month'] > 30):
#         return ('day_month', 'Bad Month number')
#     if (info['month'] in dt.month_31) & (info['day_month'] > 31):
#         return ('day_month', 'Bad Month number')
#     if info['day_month'] < 1:
#         return ('day_month', 'Please Choose Positive Numbers')

def validate_hour(hour):
    if hour < 0:
        return ('hour', 'Please use positive number')
    if hour > 24:
        return ('hour', 'Please use valid hours')


def main():
    set_env(title='MAADD Taxi')
    img = open('img/logo.png', 'rb').read()
    img2 = open('img/poweredbygoogle.png', 'rb').read()

    put_row([
        put_image(img, width='450px', height='90px'),
        None,
        put_image(img2, width='200px', height='70px')
    ], size='60% 10px 40%')
    info = input_group("Data Input", [
        #        input('Write Day Of The Month', type=NUMBER, name='day_month'),
        #        select('Choose Month', dt.month, name='month'),
        input('Choose Time:', type=DATE, name='date'),
        input('Choose a full hour:', type=NUMBER, name='hour', validate=validate_hour),

    ])
    datee = datetime.datetime.strptime(info['date'], "%Y-%m-%d")

    # hotspots1, clusters1 = tcp.predict_for_weekday_hour(2016, datee.month, datee.day,
    #                                                     info['hour'])  # TODO Will not be used in presentation
    if datee.month == 10:
        hotspots = pd.read_csv('model.csv')
    elif datee.month == 3:
        hotspots = pd.read_csv('model1.csv')
    else:
        hotspots, clusters = tcp.predict_for_weekday_hour(2016, datee.month, datee.day,
                                                          info['hour'])

    fig = px.scatter_mapbox(hotspots, lat="startLatitude", lon="startLongitude", hover_data=['profit'],
                            color_discrete_sequence=["orange"], zoom=11, height=800, color="profit",
                            size="profit",
                            color_continuous_scale=px.colors.cyclical.Phase, size_max=15)
    fig.update_layout(mapbox_style="carto-darkmatter")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    #  fig.show()
    html = fig.to_html(include_plotlyjs="require", full_html=False, default_width='1000px', default_height='800px')
    put_html(html).send()
    op = {}
    op['New Request'] = 'window.location.reload()'

    put_html("<br></br")
    put_buttons(op.keys(), onclick=tab_operation)
    hold()


def tab_operation(choice):
    run_js(op[choice])


app.add_url_rule('/', 'webio_view', webio_view(main), methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    app.run(host='localhost')
