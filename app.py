from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
import datetime
import time
import random

app = Flask(__name__)

# Define a function to calculate the average difference
def calculate_avg_difference():
    day = datetime.datetime.now() - datetime.timedelta(days=1)
    milliseconds = int(time.mktime(day.timetuple())) * 1000

    # API 엔드포인트 URL을 생성합니다.
    url = f"https://blockchain.info/blocks/{milliseconds}?format=json"

    # API 요청을 보냅니다.
    response = requests.get(url)

    # 응답을 파싱합니다.
    blocks = json.loads(response.text)

    # 시간 정보만 추출해서 리스트 생성
    block_times = [block['time'] for block in blocks]

    # 리스트 내 값들의 차이 계산
    differences = [(block_times[i] - block_times[i+1]) for i in range(len(block_times)-1)]

    # 계산한 값으로 timedelta 객체 생성
    global avg_difference
    avg_difference = datetime.timedelta(seconds=sum(differences) / len(differences))

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Schedule the function to run once a day
scheduler.add_job(func=calculate_avg_difference, trigger='interval', days=1)

# Start the scheduler
scheduler.start()

# Call the function to calculate the initial value of avg_difference
calculate_avg_difference()

# Define the Flask route
@app.route('/')
def home():
    # timedelta에서 시, 분, 초 추출
    hours, remainder = divmod(avg_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 840,000번째 블록까지 남은 시간을 계산합니다.
    latest_block_response = requests.get('https://blockchain.info/latestblock')
    latest_block_hash = latest_block_response.json()['hash']

    # 최신 블록 정보를 가져오는 API를 호출합니다.
    latest_block_info_url = f"https://blockchain.info/rawblock/{latest_block_hash}"
    latest_block_info_response = requests.get(latest_block_info_url)

    # 최신 블록 생성 시간 정보를 추출합니다.
    latest_block_time = latest_block_info_response.json()['time']

    blocks_left = 840001 - latest_block_response.json()['height']
    time_left = datetime.timedelta(seconds=blocks_left * avg_difference.seconds)
    estimated_time = datetime.datetime.fromtimestamp(latest_block_time) + time_left


    current_time = datetime.datetime.now()
    time_left = datetime.timedelta(seconds=blocks_left * avg_difference.seconds)
    estimated_day = current_time + time_left
    

    return render_template('index.html', estimated_day= estimated_day, estimated_time=estimated_time, avg_difference=avg_difference, time_left=time_left, minutes=minutes, seconds=seconds)



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
