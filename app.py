import psutil
from flask import Flask, render_template

app = Flask(__name__)

app.debug = True

@app.route("/")
def index():
    cpu_percent = psutil.cpu_percent(interval=2)
    mem_precent = psutil.virtual_memory().percent
    Message = None
    if cpu_percent > 80 or mem_precent > 80:
        Message = "High CPU or Memory Utilization detected. Please Scale up"
    return render_template("index.html", cpu_metric=cpu_percent,mem_metric=mem_precent,message=Message)

if __name__ == "__main__":
    
    app.run(host='0.0.0.0')
