from flask import Flask, render_template, request
import pyttsx3
import os
import wikipedia
import urllib.parse  
import requests
from dotenv import load_dotenv
from datetime import date , timedelta
import re
from werkzeug.utils import secure_filename
port = 2001


import socket

def get_local_ip():
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Add this to your app startup
print(f"Server running on: http://{get_local_ip()}:{port}")



# Initiate The app



app = Flask(__name__)
load_dotenv()
PAGES_DIR = os.path.join('static', 'pages')  
api_key = "spCCZfJobYiRlIpn6HxnABw4mKTgGHk6DMEVgtHT"
today = date.today().isoformat()
url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={api_key}"
url_mars_weather = f"https://api.nasa.gov/insight_weather/?api_key={api_key}&feedtype=json&ver=1.0"
url_apod = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
endpoints_DONKI = {
    "Solar Flares": "https://services.swpc.noaa.gov/json/flare_list.json",
    "Coronal Mass Ejections (CMEs)": "https://services.swpc.noaa.gov/json/cme_list.json",
    "Solar Energetic Particles": "https://services.swpc.noaa.gov/json/sep_list.json",
    "Solar Radio Bursts": "https://services.swpc.noaa.gov/json/srb_list.json",
    "Geomagnetic Storms (K-index)": "https://services.swpc.noaa.gov/json/planetary_k_index.json",
    "Solar Wind": "https://services.swpc.noaa.gov/json/solar_wind_list.json",
    "Space Weather Alerts": "https://services.swpc.noaa.gov/json/alerts.json",
    "Sunspot Data": "https://services.swpc.noaa.gov/json/sunspot_list.json"
}
params = {
    "start_date": today,
    "end_date": today,
    "api_key": api_key
}
url_space = "https://api.spaceflightnewsapi.net/v4/articles/?limit=5"

# Index App Route
@app.route("/Mathjax-Tutorial", methods=['GET', 'POST'])
def tutorial1():
    return render_template("Mathjax Tutorial.html")
@app.route("/Page-Creation-Tutorial", methods=['GET', 'POST'])
def tutorial2():
    return render_template("Page Creation Tutorial.html")
@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@app.route("/mainpage", methods=['GET', 'POST'])
def index():
    # Variables
    data = ""
    name = ""
    hazardous = ""
    diameter = ""
    speed = ""
    miss_distance = ""

    # Speech SAVE or MAKE
    if not os.path.exists("static/speech.mp3"):
        text = ("Hello from व्योमपाइडेया. This website fulfills your astronomy questions from user inputs and free Application Programming Interfaces. "
                "As of now, user input has not been added, but it is a priority. When you are ready to search, just click the Go to Search page.")
        engine = pyttsx3.init()
        engine.save_to_file(text, "static/speech.mp3")
        engine.runAndWait()
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for bad responses
        data = response.json()
        # Get Asteroid Data
        if 'near_earth_objects' in data and today in data['near_earth_objects']:
            asteroid = data['near_earth_objects'][today][0]
            name = f"Asteroid: {asteroid['name']}"
            hazardous = f"Is Hazardous: {asteroid['is_potentially_hazardous_asteroid']}"
            diameter = f"Estimated Diameter (meters): {round(asteroid['estimated_diameter']['meters']['estimated_diameter_max'], 2)}  meters"
            speed = f"Speed (km/h): {round(float(asteroid['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']), 2)} km/h"
            miss_distance = f"Miss Distance (km): {round(float(asteroid['close_approach_data'][0]['miss_distance']['kilometers']), 2)} km"
    except requests.exceptions.RequestException as e:
        name = "Error"
        hazardous = f"An error occurred: {e}"
        diameter = ""
        speed = ""
        miss_distance = ""
    try:
        response = requests.get(url_apod)
        data = response.json()
    except requests.exceptions.RequestException as e:
        data = f"An error occurred: {e}"
    return render_template("index.html", name_web=name, hazardous_web=hazardous, diameter_web=diameter, speed_web=speed, miss_distance_web=miss_distance, data=data)
    


# Search App Route

@app.route("/search", methods=['GET', 'POST'])
def search():
    wikipedia.set_user_agent(f"Mozilla/5.0 (compatible; AstropediaBot/1.0; +http://localhost:{port})")
    wiki = ""
    britannicalink = ""
    line = ""
    prompt_raw = ""

    # Planets and Dwarf Planets Lists
    planets = ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune"]
    dwarf_planets = ["pluto", "ceres", "eris", "haumea", "makemake"]

    if request.method == "POST":
        line = request.form["line_num"]
        prompt_raw = request.form["content"].strip()

        if not prompt_raw:
            wiki = "Please input something"
        else:
            prompt = prompt_raw  # ✅ FIXED: define prompt from prompt_raw

            # Clean prefixes
            for prefix in [
                "what is a", "what is an", "what is the", "what is",
                "who is", "who was", "what was", "what are", "what were",
                "tell me about", "explain", "define", "give information about",
                "i want to know about", "i want information on", "can you tell me about",
                "could you explain", "please explain", "do you know about", "what do you know about",
                "explanation of", "short note on", "details of", "something about", "anything about"
            ]:
                if prompt.lower().startswith(prefix):
                    prompt = prompt[len(prefix):].strip()
                    break

            original_prompt = prompt  # Keep for display/link purposes

            # Adjust for known astronomy terms
            if prompt.lower() in planets:
                prompt = prompt.capitalize() + " (planet)"
            elif prompt.lower() in dwarf_planets:
                prompt = prompt.capitalize() + " (dwarf planet)"

            # Generate Britannica URL (encoded)
            britannicalink = "https://www.britannica.com/search?query=" + urllib.parse.quote_plus(original_prompt)

            # Line count
            if not line.strip():
                line_count = 7
            else:
                line = int(line)
                line_count = 7 if line <= 1 else line

            # Get Wikipedia summary
            try:
                wiki = wikipedia.summary(prompt, sentences=line_count)
            except wikipedia.exceptions.DisambiguationError as e:
                wiki = f"The prompt '{prompt}' is ambiguous. Please be more specific. Options include: {', '.join(e.options[:10])}..."
            except wikipedia.exceptions.PageError:
                try:
                  search = wikipedia.search(prompt,  results = 5)
                  wiki = search
                  if search:
                      wiki = wikipedia.summary(search[0], sentences=line_count)
                  else:
                      wiki = f"No Wikipedia page found for '{prompt}'."

                except:
                  wiki =  f"Search failed"
            except requests.exceptions.RequestException as e:
                wiki = f"Connection error occurred: {e}. Please check your internet or firewall settings."
            except Exception as e:
                wiki = f"An unexpected error occurred: {e}"

    return render_template("search.html", ans=wiki, link=britannicalink)
    


# News App Route

@app.route("/news", methods=['GET', 'POST'])
def news():
   asteroid_data = []
   asteroid_info = {}
   sol_keys = []
   today_sol = ""
   mars_day = ""
   today_weather = ""
   max_temp = ""
   min_temp = ""
   donki_data = {}
   articles = []
   asteroid_info = {}
   today_news_date_obj = date.today()
   formatted_month_year = today_news_date_obj.strftime("%Y-%m")
   today_day = today_news_date_obj.strftime("%A")
   today_news_date = today_day + ", " + formatted_month_year 

   try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for bad responses
        data = response.json()
        # Get Asteroid Data
        if 'near_earth_objects' in data and today in data['near_earth_objects']:
            for asteroid in data['near_earth_objects'][today]:
                asteroid_info = {
                    "name": asteroid['name'],
                    "hazardous": asteroid['is_potentially_hazardous_asteroid'],
                    "diameter": round(asteroid['estimated_diameter']['meters']['estimated_diameter_max'], 2),
                    "speed": round(float(asteroid['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']), 2),
                    "miss_distance": round(float(asteroid['close_approach_data'][0]['miss_distance']['kilometers']), 2)
                }
                asteroid_data.append(asteroid_info)
   except requests.exceptions.RequestException as e:
            asteroid_data = "Error", f"An error occurred: {e}"
#    try:
#       response = requests.get(url_mars_weather)
#       data = response.json()
#       sol_keys = data['sol_keys']
#       today_sol = sol_keys[-1]
#       mars_day = F"Today's Sol on Mars (latest available): {today_sol}"
#       today_weather = data[today_sol]
#       min_temp = "Temperature (min):", today_weather['AT']['mn'], "°C"
#       max_temp = "Temperature (max):", today_weather['AT']['mx'], "°C"
#    except requests.exceptions.RequestException as e:
#         mars_day = "Error"
#         min_temp = f"An error occurred: {e}"
#         max_temp = ""

   start_date = (date.today() - timedelta(days=1)).isoformat()
   end_date = date.today().isoformat()
   donki_base = "https://api.nasa.gov/DONKI"
   endpoints_DONKI = {
        "Solar Flares": f"{donki_base}/FLR?startDate={start_date}&endDate={end_date}&api_key={api_key}",
        "Coronal Mass Ejections (CMEs)": f"{donki_base}/CME?startDate={start_date}&endDate={end_date}&api_key={api_key}",
        "Solar Energetic Particles": f"{donki_base}/SEP?startDate={start_date}&endDate={end_date}&api_key={api_key}",
        "Geomagnetic Storms": f"{donki_base}/GST?startDate={start_date}&endDate={end_date}&api_key={api_key}",
        "Interplanetary Shocks": f"{donki_base}/IPS?startDate={start_date}&endDate={end_date}&api_key={api_key}",
        "Magnetopause Crossings": f"{donki_base}/MPC?startDate={start_date}&endDate={end_date}&api_key={api_key}",
        "Radiation Belt Enhancements": f"{donki_base}/RBE?startDate={start_date}&endDate={end_date}&api_key={api_key}",
        "HSS (High Speed Streams)": f"{donki_base}/HSS?startDate={start_date}&endDate={end_date}&api_key={api_key}",
        "WSA+Enlil Simulations": f"{donki_base}/WSAEnlilSimulations?startDate={start_date}&endDate={end_date}&api_key={api_key}"
    }

   for event_type, event_url in endpoints_DONKI.items():
       try:
           response = requests.get(event_url)
           if response.status_code == 200:
                data = response.json()
                donki_data[event_type] = data[:3]
           else:
                donki_data[event_type] = [{"error": f"Failed to fetch data ({response.status_code})"}]
       except requests.exceptions.RequestException as e:
            donki_data[event_type] = [{"error": f"Exception occurred: {e}"}]
   response = requests.get(url_space)
   data = response.json()
   for article in data['results']:        
     try:
         response = requests.get(url_space, timeout=10)
         article_info = {
            "title": article['title'],
            "summary": article['summary'],
            "url": article['url'],
            "published": article['published_at']}
         articles.append(article_info)
     except requests.exceptions.RequestException as e:
         articles = [{"title" : "error","summary":str(e), "url": "", "published" : ""}]
     except requests.exceptions.ConnectionError as e:
          articles = [{"title" : "error","summary":str(e), "url": "", "published" : ""}]
     except requests.exceptions.ConnectionError as e:
         articles = [{"title" : "error","summary":str(e), "url": "", "published" : ""}]
         


  
       
   return render_template("news.html", asteroids=asteroid_data, mars_day_web=mars_day, min_temp_web = min_temp, max_temp_web = max_temp,  donki_web=donki_data, article_web=articles, today_web = today_news_date)

# Create page
@app.route("/create", methods = ["GET","POST"])
def create_page():
    title = ""
    html = ""
    if request.method == "POST":
        title = request.form.get("title", "").strip().title()
        content = request.form.get("article_content", "").strip()
        css = request.form.get("article_css", "").strip()


        if title:
            # Sanitize filename
            safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '', title)
            filepath = os.path.join(PAGES_DIR, f"{safe_title}.html")

            
            with open(filepath, "w", encoding="utf-8") as f:
                html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{safe_title}</title>
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
      <link rel="icon" href="static/A.ico" type="image/x-icon">
    <style>
        * {{
            font-family: Arial, Helvetica, sans-serif;
            padding: 0;
            margin: 0;
            text-decoration: none;
            box-sizing: border-box;
        }}
        #testbar {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: #1f1f1f;
            height: 80px;
            width: 100%;
            color: white;
            position: fixed;
            z-index: 1;
            top: 0;
            left: 0;
            border-bottom:2px solid #f26a4b;;
        }}
        .logo {{
            color: white;
            font-size: 35px;
            line-height: 80px;
            padding: 0 100px;
            font-weight: bold;
        }}
        #testbar ul {{
            float: right;
            margin-right: 20px;
            list-style: none;
            color: white;
        }}
        #testbar ul li {{
            display: inline-block;
            line-height: 80px;
            margin: 0 5px;
            padding-bottom: 20px;
        }}
        #testbar ul li a {{
            color: white;
            font-size: 17px;
            text-transform: uppercase;
            padding: 7px 13px;
            border-radius: 3px;
        }}
        a.active, a:hover {{
            background-color: #0044cc;
            transition: 0.5s;
        }}
        .checkbtn {{
            color: white;
            font-size: 30px;
            float: right;
            line-height: 80px;
            margin-right: 40px;
            cursor: pointer;
            display: none;
        }}
        #check {{
            display: none;
        }}
        @media (max-width:952px) {{
            label.logo {{
                font-size: 30px;
                padding-left: 50px;
            }}
            #testbar ul li a {{
                font-size: 16px;
            }}
        }}
        @media (max-width:858px) {{
            .checkbtn {{
                display: block;
            }}
            ul {{
                position: fixed;
                width: 100%;
                height: 100vh;
                background-color: #2c3e50;
                top: 80px;
                left: -100%;
                text-align: center;
                transition: all 0.5s;
            }}
            #testbar ul li {{
                display: block;
            }}
            #testbar ul li a {{
                font-size: 20px;
            }}
            #testbar ul li a:hover, a.active {{
                background: none;
                color: #0082e6;
            }}
            #check:checked ~ ul {{
                left: 0;
            }}
        }}

        body {{
            background-color: #f9f9f9;
            color: #333;
        }}

        /* Container div for page content with top padding so content is not hidden behind navbar */
        #page-content {{
            padding-top: 100px;
            
            max-width: 1000px;
            margin-left: auto;
            margin-right: auto;
        }}
    </style>
    {css}
</head>
<body>
      <nav id="testbar">
    <input type="checkbox" id="check" />
    <label for="check" class="checkbtn"><i class="fas fa-bars"></i></label>
    <label class="logo">Astropedia</label>
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/news">News</a></li>
      <li><a href="/usersearch" class="active">Search</a></li>
      <li><a href="/create">Create A Page</a></li>
      <li><a href="/edit">Edit A Page</a></li>
    </ul>
  </nav>

    <div id="page-content">
        {content}
    </div>

</body>
</html>
'''
                f.write(html)


        else:
            return "Title is required!", 400
        

    return render_template("create.html", title=title)
@app.route("/createcode", methods = ["GET","POST"])
def create_page_code():
    title = ""
    html = ""
    if request.method == "POST":
        title = request.form.get("title", "").strip().title()
        content = request.form.get("article_content", "").strip()
        css = request.form.get("article_css", "").strip()


        if title:
            # Sanitize filename
            safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '', title)
            filepath = os.path.join(PAGES_DIR, f"{safe_title}.html")

            
            with open(filepath, "w", encoding="utf-8") as f:
                html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{safe_title}</title>
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
      <link rel="icon" href="static/A.ico" type="image/x-icon">
    <style>
        * {{
            font-family: Arial, Helvetica, sans-serif;
            padding: 0;
            margin: 0;
            text-decoration: none;
            box-sizing: border-box;
        }}
        #testbar {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: #1f1f1f;
            height: 80px;
            width: 100%;
            color: white;
            position: fixed;
            z-index: 1;
            top: 0;
            left: 0;
            border-bottom:2px solid #f26a4b;;
        }}
        .logo {{
            color: white;
            font-size: 35px;
            line-height: 80px;
            padding: 0 100px;
            font-weight: bold;
        }}
        #testbar ul {{
            float: right;
            margin-right: 20px;
            list-style: none;
            color: white;
        }}
        #testbar ul li {{
            display: inline-block;
            line-height: 80px;
            margin: 0 5px;
            padding-bottom: 20px;
        }}
        #testbar ul li a {{
            color: white;
            font-size: 17px;
            text-transform: uppercase;
            padding: 7px 13px;
            border-radius: 3px;
        }}
        a.active, a:hover {{
            background-color: #0044cc;
            transition: 0.5s;
        }}
        .checkbtn {{
            color: white;
            font-size: 30px;
            float: right;
            line-height: 80px;
            margin-right: 40px;
            cursor: pointer;
            display: none;
        }}
        #check {{
            display: none;
        }}
        @media (max-width:952px) {{
            label.logo {{
                font-size: 30px;
                padding-left: 50px;
            }}
            #testbar ul li a {{
                font-size: 16px;
            }}
        }}
        @media (max-width:858px) {{
            .checkbtn {{
                display: block;
            }}
            ul {{
                position: fixed;
                width: 100%;
                height: 100vh;
                background-color: #2c3e50;
                top: 80px;
                left: -100%;
                text-align: center;
                transition: all 0.5s;
            }}
            #testbar ul li {{
                display: block;
            }}
            #testbar ul li a {{
                font-size: 20px;
            }}
            #testbar ul li a:hover, a.active {{
                background: none;
                color: #0082e6;
            }}
            #check:checked ~ ul {{
                left: 0;
            }}
        }}

        body {{
            background-color: #f9f9f9;
            color: #333;
        }}

        /* Container div for page content with top padding so content is not hidden behind navbar */
        #page-content {{
            padding-top: 100px;
            
            max-width: 1000px;
            margin-left: auto;
            margin-right: auto;
        }}
    </style>
    {css}
</head>
<body>
      <nav id="testbar">
    <input type="checkbox" id="check" />
    <label for="check" class="checkbtn"><i class="fas fa-bars"></i></label>
    <label class="logo">Astropedia</label>
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/news">News</a></li>
      <li><a href="/usersearch" class="active">Search</a></li>
      <li><a href="/create">Create A Page</a></li>
      <li><a href="/edit">Edit A Page</a></li>
    </ul>
  </nav>

    <div id="page-content">
        {content}
    </div>

</body>
</html>
'''
                f.write(html)


        else:
            return "Title is required!", 400
        

    return render_template("createcode.html", title=title)
@app.route('/page/<title>')
def view_page(title):
    try:
        with open(os.path.join(PAGES_DIR, f"{title}.html"), encoding='utf-8') as f:
            content = f.read()
        return content  # Directly return HTML content
    except FileNotFoundError:
        return "Page not found", 404

@app.route("/usersearch", methods = ["GET","POST"])
def usersearch():

    query = request.args.get('q', '').lower()
    matches = []
    for prefix in [
                "what is a", "what is an", "what is the", "what is",
                "who is", "who was", "what was", "what are", "what were",
                "tell me about", "explain", "define", "give information about",
                "i want to know about", "i want information on", "can you tell me about",
                "could you explain", "please explain", "do you know about", "what do you know about",
                "explanation of", "short note on", "details of", "something about", "anything about"
            ]:
                if query.lower().startswith(prefix):
                    query = query[len(prefix):].strip()
                    break

    for filename in os.listdir(PAGES_DIR):
        if filename.endswith('.html'):
            filepath = os.path.join(PAGES_DIR, filename)
            with open(filepath, encoding='utf-8') as f:
                content = f.read().lower()
            if query in filename.lower() or query in content:
                matches.append(filename.replace('.html', ''))
    return render_template('usersearch.html', query=query, results=matches)
@app.route("/edit", methods=["GET", "POST"])
def edit():
    
    query = ""
    status = ""
    query = request.args.get('q', '').lower()
    content = ""
    matches = []
    filename = ""
            # Clean the query
    for prefix in [
            "what is a", "what is an", "what is the", "what is",
            "who is", "who was", "what was", "what are", "what were",
            "tell me about", "explain", "define", "give information about",
            "i want to know about", "i want information on", "can you tell me about",
            "could you explain", "please explain", "do you know about", "what do you know about",
            "explanation of", "short note on", "details of", "something about", "anything about"
        ]:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break

    if query:
            for fname in os.listdir(PAGES_DIR):
                if fname.endswith('.html'):
                    filepath = os.path.join(PAGES_DIR, fname)
                    filepath = filepath.strip()
                    with open(filepath, encoding='utf-8') as f:
                        file_content = f.read()
                        if query in fname.lower():
                            matches.append(fname.replace('.html', ''))
                            content += f"\n\n<!-- {fname} -->\n" + file_content
                            filename = fname
                              # Save first matching filename for editing


    if request.method == "POST":
        updated = request.form['article_edited_content']
        filename = request.form['filename'].strip()
        safe_title = re.sub(r'[<>:"/\\|?*\r\n]+', '', filename)  
        filepath = os.path.join(PAGES_DIR, safe_title)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)
        status = "File successfully updated"
        content = updated  # Show updated content

   

    return render_template("edit.html", query=query, content=content, status=status, filename=filename)
# Run the app
if __name__ == '__main__':
    app.run(port=port, host='0.0.0.0')