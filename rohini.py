from flask import Flask, render_template, request,render_template_string
import googlemaps
import requests
from flask import jsonify
import os
import math
import logging
app = Flask(__name__,static_folder='C:\\Users\\jsrir\\OneDrive\\Desktop\\Daata298A\\static')

FILE_PATH = "C:\\Users\\jsrir\\OneDrive\\Desktop\\Daata298A\\input_images\\steps.txt"
logging.basicConfig(level=logging.DEBUG)

def save_routes_to_file(routes, append=False):
    mode = "a" if append else "w"
    with open(FILE_PATH, mode) as f:
        for route in routes:
            for step in route:
                f.write(f"Start: {step['start_location']['lat']}, {step['start_location']['lng']} | End: {step['end_location']['lat']}, {step['end_location']['lng']}\n")
            f.write("---\n")


@app.route('/map', methods=['GET', 'POST'])
def map():
    logging.debug("Inside the /map route")
    source_address = ''
    destination_address = ''
    show_optimal = False
    school_selected=False
    new_image3 = url_for('static', filename='pop.png')
    gmaps = googlemaps.Client(key='AIzaSyCoEXReHmOkavW6VUzMM2Ams50GqV2lItU')
    geocode_result = gmaps.geocode(95192)
    location = geocode_result[0]['geometry']['location']
    lat = location['lat']
    lng = location['lng']
    lat_source = lat
    lng_source = lng
    lat_dest = lat
    lng_dest = lng

    if request.method == 'POST':
        source_address = request.form['source_address']
        destination_address = request.form['destination_address']
        #show_optimal = 'optimal-btn' in request.form
        school_selected = 'scenarios' in request.form and request.form['scenarios'] == 'School'
        logging.debug(f"POST request - updated show_optimal value: {show_optimal}")
        logging.debug(f"POST request - updated show_optimal value: {school_selected}")
        logging.debug(f"POST request form data: {request.form}")
        selected_route_index = request.form.get('route-selector', '0')  # By default, we'll select the first route


        if source_address:
            logging.debug(f"Source address: {source_address}")  # Log the source address
            geocode_result_source = gmaps.geocode(source_address)
            logging.debug(f"Geocode result: {geocode_result_source}")
            location_source = geocode_result_source[0]['geometry']['location']
            lat_source = location_source['lat']
            lng_source = location_source['lng']

        if destination_address:
            logging.debug(f"Destination address: {destination_address}")  # Log the destination address
            geocode_result_dest = gmaps.geocode(destination_address)
            logging.debug(f"Geocode result: {geocode_result_dest}")
            location_dest = geocode_result_dest[0]['geometry']['location']
            lat_dest = location_dest['lat']
            lng_dest = location_dest['lng']
        dropdown_html = f"""
        <select id="route-selector" name="route-selector">
            <option value="0" {'selected' if selected_route_index == '0' else ''}>1</option>
            <option value="1" {'selected' if selected_route_index == '1' else ''}>2</option>
            <option value="2" {'selected' if selected_route_index == '2' else ''}>3</option>
            <option value="0" {'selected' if selected_route_index == 'optimal' else ''}>optimal</option>
        </select>"""

    html_code = f"""
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #2e2e2e;
                color: white;
            }}
            #navbar {{
                background-color: #333;
                overflow: hidden;
                text-align: center;
            }}
            #navbar a {{
                display: inline-block;
                color: white;
                text-align: center;
                padding: 14px 25px;
                text-decoration: none;
                border-radius: 10px;
            }}
            #navbar a:hover {{
                background-color: rgba(255,255,255,0.2);
            }}
            #navbar .active {{
                color: #007BFF;
                border-bottom: 2px solid #007BFF;
            }}
            .icon-container {{
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }}
            .icon {{
                display: inline-block;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background-color: #007BFF;
                color: white;
                text-align: center;
                line-height: 24px;
                margin-right: 5px;
            }}
            input[type="text"] {{
                width: 80%;
                border-radius: 10px;
                padding: 5px;
            }}
            button, input[type="submit"] {{
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                cursor: pointer;
                display: block;
                margin: 10px auto;
            }}
            #optimal-btn {{
                font-size: 1.1em;
                padding: 10px 15px;
            }}

            button:hover, input[type="submit"]:hover {{
                background-color: #0056b3;
            }}
        .menu-option {{
                margin: 10px auto;  /* Centering it horizontally */
                padding: 5px 10px;
                cursor: pointer;
                position: relative;
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                width: 80%;
                text-align: center;
            }}
            .sub-option-list {{
                display: none;
                position: absolute;
                left: 100%;
                top: 0;
                background-color: white;
                border: 1px solid #007BFF;
                border-radius: 5px;
                width: 200px;
                z-index: 1000;
            }}
            .sub-option {{
                display: block;
                color: black;
                padding: 8px;
                cursor: pointer;
                position: relative;
            }}
            .tick-mark {{
                display: none;
                color: green;
                position: absolute;
                right: 5px;
                top: 50%;
                transform: translateY(-50%);
            }}
            .sub-option.selected .tick-mark {{
                display: inline-block;
            }}
            select {{
                width: 100%; /* Full width */
                padding: 5px; /* Padding for better appearance */
                border-radius: 5px; /* Rounded corners */
                border: 1px solid #007BFF; /* Blue border */
                background-color: #333; /* Dark background */
                color: white; /* Text color */
                margin-bottom: 10px; /* Spacing below the dropdown */
            }}

            select option {{
                background-color: #2e2e2e; /* Darker background for options */
                color: white; /* Text color for options */
            }}
        </style>

        <div id="navbar">
            <a class="active" href="/map">Maps</a>
            <a href="/trip">Trip</a>
            <a href="/carla">Carla</a>
        </div>

        <div style="display: flex; flex-direction: row;height: 100%;">
            <div style="width: 18%; padding: 10px;">
                <form method="POST" action="/pick">
                    <!-- New input for zip code -->
                    <div class="icon-container">
                        <div class="icon">Z</div>
                        <input type="text" id="zip_code" name="zip_code" placeholder="Enter zip code">
                    </div>
                    
                    <!-- New button to pick zip code -->
                    <input type="submit" id="pick-btn" name="pick-btn" value="Pick">
                </form>
                    <br><br>
                <form method="POST" action="/map">
                    <div class="icon-container">
                        <div class="icon">S</div>
                        <input type="text" id="source_address" name="source_address" value="{source_address}" placeholder="Enter source address">
                    </div>
                    <div class="icon-container">
                        <div class="icon">D</div>
                        <input type="text" id="destination_address" name="destination_address" value="{destination_address}" placeholder="Enter destination address">
                    </div>
        
                    <input type="submit" value="Show Routes">
                    <br><br>
                    <div class="icon-container">
                        <span class="icon">R</span>
                        {dropdown_html}
                    </div>
                    <button id="optimal-btn" name="optimal-btn" >Show selected Route</button>
                    <br><br>
                    <div class="menu-option" onclick="toggleSubOptions(this)">
                        Road
                        <div class="sub-option-list">
                            <div class="sub-option" onclick="toggleTick(event, this)">On Road Signs<span class="tick-mark">&#10003;</span></div>
                            <div class="sub-option" onclick="toggleTick(event, this)">Road Signs<span class="tick-mark">&#10003;</span></div>
                        </div>
                    </div>

                    <div class="menu-option" onclick="toggleSubOptions(this)">
                        Intersection
                        <div class="sub-option-list">
                            <div class="sub-option" onclick="toggleTick(event, this)">3 way<span class="tick-mark">&#10003;</span></div>
                            <div class="sub-option" onclick="toggleTick(event, this)">4 way<span class="tick-mark">&#10003;</span></div>
                        </div>
                    </div>

                    <div class="menu-option" onclick="toggleSubOptions(this)">
                        Scenarios
                        <div class="sub-option-list">
                            <div class="sub-option" onclick="toggleTick(event, this)">Hospital<span class="tick-mark">&#10003;</span></div>
                            <div class="sub-option" onclick="toggleTick(event, this)">
                                School
                                <input type="checkbox" name="scenarios" value="School" style="display: none;" />
                                <span class="tick-mark">&#10003;</span>
                            </div>
                            <div class="sub-option" onclick="toggleTick(event, this)">Parking<span class="tick-mark">&#10003;</span></div>
                        </div>
                    </div>
                    <input type="submit" id="show-on-map-btn" name="show-on-map" value="Show on Map" style="background-color: #007BFF; color: white; font-size: 1.1em; padding: 10px 15px; border-radius: 5px; cursor: pointer; display: block; margin: 10px auto;">

                    


                </form>
            </div>
            <div style="position: relative; width: 82%;height: 100%;">
                <div id="map" style="height: 100%;"></div>
            </div>
            
        </div>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            let routeRenderers = [];
            let routeCounter = 0;
            let schoolSelected = {'true' if school_selected else 'false'};
            let onlyFirstRoute = {'true' if show_optimal else 'false'};
            let lat_source = { lat_source };
            let lng_source = { lng_source };
            let lat_dest = { lat_dest };
            let lng_dest = { lng_dest };
            let isPostRequest = { 'true' if request.method == 'POST' else 'false' };
            let map;
            const fourWayIntersections = [
                {{lat: 37.333079, lng: -121.879642}},
                {{lat: 37.331538, lng: -121.882836}},    
                {{lat: 37.331022, lng: -121.883909}},
                {{lat: 37.332512, lng: -121.885007}},
                {{lat: 37.335315, lng: -121.887106}},
                {{lat: 37.337162, lng: -121.888477}},
                {{lat: 37.336678, lng: -121.889518}},
                {{lat: 37.336157, lng: -121.890604}},
                // ... add all other 4-way coordinates here
            ];

            const threeWayIntersections = [
                {{lat: 37.332554, lng: -121.880650}},
                {{lat: 37.332040, lng: -121.881754}},
                // ... add all other 3-way coordinates here
            ];

 
            function initMap() {{
                var directionsService = new google.maps.DirectionsService();
                var mapOptions = {{
                    zoom: 10,
                    center: {{ lat: {lat_source}, lng: {lng_source} }}  
                }};

                map = new google.maps.Map(document.getElementById("map"), mapOptions);

                // Use the show_optimal flag to decide how many routes to display
                let schoolSelected = {'true' if school_selected else 'false'};
                //schoolSelected = {str(school_selected).lower()};

                console.log(schoolSelected);
                if (isPostRequest) {{
                    calculateAndDisplayRoute(directionsService, map, {'true' if show_optimal else 'false'})              
            }}  }}

            function placeMarker(location, map) {{
                var marker = new google.maps.Marker({{
                    position: location,
                    map: map
                }});
                
            }}


            function placeIntersectionMarkers() {{
                // Place red markers for 4-way intersections
                fourWayIntersections.forEach(function(location, index) {{
                    var marker = new google.maps.Marker({{
                        position: location,
                        map: map,
                        icon: {{ url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png" }}
                    }});

                    // Create an InfoWindow for each marker
                    var infowindow = new google.maps.InfoWindow();

                    // Add click event listener for the marker
                    google.maps.event.addListener(marker, 'click', (function(marker, location) {{
                        return function() {{
                            var contentString = '<div id="content" style="font-family: Arial, sans-serif; color: black; font-size: 14px; padding: 5px; width: 300px;">' +
                                '<h3 style="color: #333; margin-bottom: 5px;">Checkpoint Details</h3>' +
                                '<img src="{new_image3}" style="width:100%; height: auto; margin-bottom: 5px;">' +
                                '<div style="border-bottom: 1px solid black; margin-bottom: 5px;"><b>Location address:</b> ' + location.lat + ', ' + location.lng + '</div>' +
                                '<div style="border-bottom: 1px solid black; margin-bottom: 5px;"><b>Intersection Type:</b> Four-Way intersection</div>' +
                                '<div style="border-bottom: 1px solid black; margin-bottom: 5px;"><b>Maneuver:</b> Straight</div>' +
                                '<div style="border-bottom: 1px solid black; margin-bottom: 5px;"><b>Checkpoint:</b> ' + (index + 3) + '</div>' +
                                '<button onclick="deleteCheckpoint()" style="background-color: #ff4444; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; margin-top: 5px; width: 100%;">Delete Checkpoint</button>' +
                                '</div>';

                            infowindow.setContent(contentString);
                            infowindow.open(map, marker);
                        }}
                    }})(marker, location));
                }});

                // Place blue markers for 3-way intersections
                threeWayIntersections.forEach(function(location, index) {{
                    var marker = new google.maps.Marker({{
                        position: location,
                        map: map,
                        icon: {{ url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png" }}
                    }});

                    // Create an InfoWindow for each marker
                    var infowindow = new google.maps.InfoWindow();

                    // Add click event listener for the marker
                    google.maps.event.addListener(marker, 'click', (function(marker, location) {{
                        return function() {{
                            var contentString = '<div id="content" style="min-width:200px;">' +
                                '<div><b>Location address:</b> ' + location.lat + ', ' + location.lng + '</div>' +
                                '<div><b>Intersection Type:</b> Three-Way intersection</div>' +
                                '<div><b>Maneuver:</b> TBD</div>' +  // Replace TBD with actual maneuver
                                '<div><b>Checkpoint:</b> ' + (index + 3) + '</div>' +
                                '<button onclick="deleteCheckpoint()" style="background-color: red; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer; margin-top: 5px;">Delete Checkpoint</button>' +
                                '</div>';

                            infowindow.setContent(contentString);
                            infowindow.open(map, marker);
                        }}
                    }})(marker, location));
                }});
            }}          

            document.getElementById('show-on-map-btn').addEventListener('click', function(e) {{
                e.preventDefault(); // Prevent form submission
                placeIntersectionMarkers();
            }});


            function toggleSubOptions(element) {{
                let sublist = element.querySelector('.sub-option-list');
                if (sublist.style.display === "block") {{
                    sublist.style.display = "none";
                }} else {{
                    sublist.style.display = "block";
                }}
            }}

            function toggleTick(event, subOption) {{
                event.stopPropagation();  // To prevent the parent's onclick from being triggered
                let tickMark = subOption.querySelector('.tick-mark');

                let checkbox = subOption.querySelector('input[type="checkbox"]');
                if (tickMark.style.display === "inline-block") {{
                    tickMark.style.display = "none";
                    checkbox.checked = false;
                    subOption.classList.remove("selected");
                }} else {{
                    tickMark.style.display = "inline-block";
                    checkbox.checked = true;
                    subOption.classList.add("selected");
                }}
            }}
        
            function saveRoutes(routes_data) {{
                const uniqueRoutes = [...new Set(routes_data.map(route => JSON.stringify(route)))].map(routeStr => JSON.parse(routeStr));
                const shouldAppend = routeCounter > 0;
                
                fetch('/save_routes', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        routes: uniqueRoutes,
                        append: shouldAppend
                    }})
                }});

                routeCounter++;
            }}

            function calculateAndDisplayRoute(directionsService, map, onlyFirstRoute, selectedRouteIndex={selected_route_index}) {{
                let routeRequest = {{
                    
                    origin: {{ lat: {lat_source}, lng: {lng_source} }},
                    destination: {{ lat: {lat_dest}, lng: {lng_dest} }},
                    travelMode: google.maps.TravelMode.DRIVING,

                    provideRouteAlternatives: true,
                }};
                console.log(routeRequest);

                if (schoolSelected) {{
                    // If the school option is selected, find a nearby school and add it as a waypoint
                    const midLat = ({lat_source} + {lat_dest}) / 2;
                    const midLng = ({lng_source} + {lng_dest}) / 2;

                    // Use the Places API to find a nearby school (you may need to modify this to integrate the Places API correctly)
                    const placesService = new google.maps.places.PlacesService(map);
                    placesService.nearbySearch({{
                        location: {{lat: midLat, lng: midLng}},
                        radius: 5000,
                        type: ['school']
                    }}, function(results, status) {{
                        if (status === google.maps.places.PlacesServiceStatus.OK) {{
                            routeRequest.waypoints = [{{location: results[0].geometry.location}}];
                            console.log(results);
                            routeRequest.provideRouteAlternatives = true;
                            directionsService.route(routeRequest, handleDirectionsResponse);
                        }}
                    }});
                }} else {{
                    directionsService.route(routeRequest, function(response, status) {{
                        handleDirectionsResponse(response, status, selectedRouteIndex);
                    }});
                }}
            }}

            function handleDirectionsResponse(response, status,selectedRouteIndex) {{
                if (status === "OK") {{
                    const routes_data = [];
                    const colors = ["red", "green", "blue"];
                    
                    // Clear any existing route renderers before drawing new ones
                    for (let renderer of routeRenderers) {{
                        renderer.setMap(null);
                    }}
                    routeRenderers = [];
                    
                            
                    const totalRoutes = onlyFirstRoute ? 1 : (selectedRouteIndex != null && selectedRouteIndex >= 0 ? selectedRouteIndex + 1 : response.routes.length);
                    let startRouteIndex = onlyFirstRoute ? 0 : (selectedRouteIndex != null && selectedRouteIndex >= 0 ? selectedRouteIndex : 0);
                    for (let i = selectedRouteIndex; i < totalRoutes; i++) {{
                        const route = response.routes[i];
                        
                        const renderer = new google.maps.DirectionsRenderer({{
                            map: map,
                            directions: response,
                            routeIndex: i,
                            polylineOptions: {{
                                strokeColor: colors[i % colors.length]
                            }}
                        }});
                        
                        // Store the renderer in our array
                        routeRenderers.push(renderer);
                        console.log(routeRenderers);
                    }};
                    setTimeout(function() {{
                        console.log("10 seconds have passed");
                        // You can add any code here that you want to execute after 10 seconds
                    }}, 10000);  // 10000 milliseconds = 10 seconds

                }} else {{
                    window.alert("Directions request failed due to " + status);
                }}
            }}
            function showOptimalRoute() {{
                var selectedRouteIndex = document.getElementById('route-selector').value;
                var directionsService = new google.maps.DirectionsService();

                // Clear existing routes
                for (let renderer of routeRenderers) {{
                    renderer.setMap(null);
                }}
                routeRenderers = [];

                // Call calculateAndDisplayRoute with the selected route index
                calculateAndDisplayRoute(directionsService, map, false, 2);
            }}



        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCoEXReHmOkavW6VUzMM2Ams50GqV2lItU&callback=initMap&libraries=places" async defer></script>
    """
    return html_code