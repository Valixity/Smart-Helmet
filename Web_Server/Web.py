import serial
import time
from flask import Flask, render_template_string

app = Flask(__name__)
ser = serial.Serial('COM3', 115200, timeout=1)

# Track eyes closed duration
eyes_closed_since = None
sleeping = False  # You can set this externally when needed

page_template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Smart Helmet Status</title>
  <meta http-equiv="refresh" content="0.5">
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #121212;
      color: #e0e0e0;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      height: 100vh;
      margin: 0;
    }
    h1 {
      color: #ffffff;
      margin-bottom: 20px;
      text-align: center;
    }
    .engine-status {
      font-size: 40px;
      font-weight: bold;
      padding: 20px 40px;
      border-radius: 10px;
      margin-bottom: 30px;
    }
    .engine-on {
      background-color: #1a3d1a;
      color: #90ee90;
    }
    .engine-off {
      background-color: #5c1a1a;
      color: #ffb3b3;
    }
    table {
      margin: 0 auto;
      border-collapse: collapse;
      width: 700px;
      background-color: #1e1e1e;
      border-radius: 8px;
      overflow: hidden;
    }
    th, td {
      border: 1px solid #333;
      padding: 18px;
      text-align: center;
      font-size: 20px;
      position: relative;
    }
    th {
      background-color: #2c2c2c;
      color: #ffffff;
    }
    td {
      background-color: #1a1a1a;
    }
    .alert {
      background-color: #5c1a1a; /* red shade */
      color: #ffb3b3;
      font-weight: bold;
    }
    /* Eyes progressive fill */
    .eyes-progress::before {
      content: "";
      position: absolute;
      top: 0; left: 0; bottom: 0;
      width: var(--fill, 0%);
      background-color: #5c1a1a;
      z-index: 0;
    }
    .eyes-progress span {
      position: relative;
      z-index: 1;
    }
  </style>
</head>
<body>
  <h1>Smart Helmet Data</h1>
  <div class="engine-status {{ engine_class }}">
    Engine: {{ engine }}
  </div>
  <table>
    <tr><th>Helmet</th><td class="{{ helmet_class }}">{{ helmet }}</td></tr>
    <tr><th>Eyes</th>
        <td class="eyes-progress" style="--fill: {{ fill_percent }}%">
          <span>{{ eyes }}</span>
        </td>
    </tr>
    <tr><th>Alcohol</th><td class="{{ alcohol_class }}">{{ alcohol }}</td></tr>
    <tr><th>Alcohol Value</th><td>{{ value }}</td></tr>
  </table>
</body>
</html>
"""

@app.route('/')
def index():
    global eyes_closed_since, sleeping
    helmet, eyes, alcohol, value, engine = "?", "?", "?", "?", "?"
    while ser.in_waiting:
        line = ser.readline().decode(errors='ignore').strip()
        if line.startswith("Helmet:"):
            helmet = line.split(":")[1].strip()
        elif line.startswith("Eyes:"):
            eyes = line.split(":")[1].strip()
        elif line.startswith("Alcohol:") and "Value" not in line:
            alcohol = line.split(":")[1].strip()
        elif line.startswith("Alcohol Value:"):
            value = line.split(":")[1].strip()
        elif line.startswith("Engine:"):
            engine = line.split(":")[1].strip()

    # Track eyes closed duration
    if eyes.lower() == "closed":
        if eyes_closed_since is None:
            eyes_closed_since = time.time()
        elapsed = int(time.time() - eyes_closed_since)
        fill_percent = min(elapsed * 20, 100)  # 5 seconds → full
    else:
        eyes_closed_since = None
        fill_percent = 0

    if sleeping:
        fill_percent = 100

    # Conditional classes
    helmet_class = "alert" if helmet.lower() == "not worn" else ""
    alcohol_class = "alert" if alcohol.lower() == "detected" else ""
    engine_class = "engine-off" if engine.lower() == "off" else "engine-on"

    return render_template_string(page_template,
                                  helmet=helmet,
                                  eyes=eyes,
                                  alcohol=alcohol,
                                  value=value,
                                  engine=engine,
                                  helmet_class=helmet_class,
                                  alcohol_class=alcohol_class,
                                  engine_class=engine_class,
                                  fill_percent=fill_percent)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
