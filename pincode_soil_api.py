from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

POSTALPINCODE_API_BASE_URL = "https://api.postalpincode.in/pincode/"

GEOAPIFY_API_KEY = "41a3079366734ec3866921b90fbdb160" 
GEOAPIFY_GEOCODING_BASE_URL = "https://api.geoapify.com/v1/geocode/search"

SOILGRIDS_API_BASE_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"

BHUVAN_API_SOIL_BASE_URL = "https://bhuvan-app1.nrsc.gov.in/api/soil_data" 

DB_CONFIG = {
    "host": "localhost",
    "database": "india_soil_db",  
    "user": "postgres",           
    "password": "your_pg_password" 
}

POSTGIS_TABLE_NAME = "india_soil_polygons" 
POSTGIS_SOIL_TYPE_COLUMN = "soil_type_name_from_your_data" 


STATE_SOIL_MAP = {
    "ANDHRA PRADESH": ["Red Soil", "Black Soil", "Laterite Soil"],
    "ARUNACHAL PRADESH": ["Forest and Mountain Soil"],
    "ASSAM": ["Alluvial Soil", "Forest and Mountain Soil", "Peat Soil"],
    "BIHAR": ["Alluvial Soil", "Peat Soil"],
    "CHHATTISGARH": ["Red Soil", "Yellow Soil", "Black Soil"],
    "GOA": ["Laterite Soil"],
    "GUJARAT": ["Black Soil", "Desert Soil", "Saline/Alkaline Soil"],
    "HARYANA": ["Alluvial Soil", "Desert Soil", "Saline/Alkaline Soil"],
    "HIMACHAL PRADESH": ["Forest and Mountain Soil"],
    "JAMMU AND KASHMIR": ["Forest and Mountain Soil"], 
    "JHARKHAND": ["Red Soil", "Laterite Soil"],
    "KARNATAKA": ["Black Soil", "Red Soil", "Laterite Soil"],
    "KERALA": ["Laterite Soil", "Peat Soil", "Red Soil"],
    "MADHYA PRADESH": ["Black Soil", "Red Soil", "Laterite Soil"],
    "MAHARASHTRA": ["Black Soil", "Laterite Soil", "Saline/Alkaline Soil"],
    "MANIPUR": ["Forest and Mountain Soil"],
    "MEGHALAYA": ["Forest and Mountain Soil", "Laterite Soil"],
    "MIZORAM": ["Forest and Mountain Soil"],
    "NAGALAND": ["Forest and Mountain Soil"],
    "ODISHA": ["Red Soil", "Laterite Soil", "Alluvial Soil", "Peat Soil"],
    "PUNJAB": ["Alluvial Soil", "Desert Soil", "Saline/Alkaline Soil"],
    "RAJASTHAN": ["Desert Soil", "Red Soil", "Saline/Alkaline Soil"],
    "SIKKIM": ["Forest and Mountain Soil"],
    "TAMIL NADU": ["Red Soil", "Black Soil", "Laterite Soil", "Saline/Alkaline Soil", "Peat Soil"],
    "TELANGANA": ["Red Soil", "Black Soil"],
    "TRIPURA": ["Forest and Mountain Soil", "Laterite Soil"],
    "UTTAR PRADESH": ["Alluvial Soil", "Saline/Alkaline Soil"],
    "UTTARAKHAND": ["Forest and Mountain Soil", "Peat Soil"],
    "WEST BENGAL": ["Alluvial Soil", "Peat Soil", "Red Soil"],
    "DELHI": ["Alluvial Soil"], # Delhi is predominantly Alluvial plains
    "PUDUCHERRY": ["Alluvial Soil"], 
    "CHANDIGARH": ["Alluvial Soil"],
    "ANDAMAN AND NICOBAR ISLANDS": ["Forest and Mountain Soil", "Red Soil"],
    "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": ["Laterite Soil", "Black Soil"] # Combined UT
}

# 5. General Properties for Each Major Soil Type (for display when SoilGrids fails)
GENERAL_SOIL_PROPERTIES_MAP = {
    "Alluvial Soil": {
        "description": "Formed by river deposits, highly fertile, rich in potash and lime. Ideal for various crops like rice, wheat, and sugarcane.",
        "key_characteristics": ["Highly fertile", "River-deposited", "Good for rice, wheat"]
    },
    "Black Soil": {
        "description": "Also known as Regur soil (black cotton soil). Known for high moisture retention, deep cracks when dry, and richness in iron, lime, and magnesium. Best suited for cotton.",
        "key_characteristics": ["High moisture retention", "Rich in iron", "Ideal for cotton"]
    },
    "Red Soil": {
        "description": "Develops on crystalline igneous rocks, red color due to iron oxides. Generally porous and friable. Suitable for millets, groundnuts, and pulses.",
        "key_characteristics": ["Reddish color (iron oxides)", "Porous", "Suitable for millets"]
    },
    "Yellow Soil": {
        "description": "Often found with red soils in low rainfall areas, turns yellow when hydrated. Similar properties to red soil, may be deficient in nitrogen and humus.",
        "key_characteristics": ["Yellow when hydrated", "Similar to red soil", "Can be deficient in nitrogen"]
    },
    "Laterite Soil": {
        "description": "Formed under high temperature and heavy rainfall through intense leaching. Rich in iron and aluminum oxides, often acidic. Good for plantation crops like tea, coffee, and cashew.",
        "key_characteristics": ["Leached and acidic", "Rich in iron/aluminum", "Good for tea, coffee, cashew"]
    },
    "Desert Soil": {
        "description": "Sandy to gravelly texture, saline in nature, low in organic matter and moisture. Suitable for drought-resistant and salt-tolerant crops.",
        "key_characteristics": ["Sandy and saline", "Low moisture", "Drought-resistant crops"]
    },
    "Forest and Mountain Soil": {
        "description": "Varies with mountain environment; loamy and silty in valleys, coarse-grained on upper slopes. Often acidic with variable humus content.",
        "key_characteristics": ["Varied texture", "Acidic", "Found in hilly/forest areas"]
    },
    "Peat Soil": {
        "description": "Formed from accumulation of organic matter in humid regions. Heavy, black, and highly acidic with high water-holding capacity. Found in marshy areas.",
        "key_characteristics": ["High organic matter", "Heavy and black", "Acidic, marshy areas"]
    },
    "Saline/Alkaline Soil": {
        "description": "High salt content (sodium, magnesium, potassium), making it infertile for most crops. Found in arid/semi-arid regions and coastal areas.",
        "key_characteristics": ["High salt content", "Infertile", "Coastal/arid regions"]
    }
}


def get_geolocation_from_geoapify(address):
    """
    Fetches latitude and longitude for a given address using Geoapify Geocoding API.

    Arguments:
        address (str): The full address string to geocode.

    Returns:
        tuple: (latitude, longitude) or (None, None) if geocoding fails.
    """
    if GEOAPIFY_API_KEY == "YOUR_GEOAPIFY_API_KEY" or not GEOAPIFY_API_KEY:
        print("Warning: Geoapify API key not set. Geolocation will be None. Please get a key from geoapify.com.")
        return None, None

    params = {
        "text": address,
        "apiKey": GEOAPIFY_API_KEY,
        "limit": 1 
    }

    try:
        geo_response = requests.get(GEOAPIFY_GEOCODING_BASE_URL, params=params)
        geo_response.raise_for_status() 
        geo_data = geo_response.json()

        if geo_data and geo_data.get('features'):
            coordinates = geo_data['features'][0]['geometry']['coordinates']
            longitude = coordinates[0]
            latitude = coordinates[1]
            return float(latitude), float(longitude)
        else:
            if 'error' in geo_data:
                error_details = geo_data['error'].get('message', 'Unknown Geoapify error.')
                print(f"Geoapify Error for address '{address}': {error_details}")
            else:
                print(f"Geoapify: No features found for address '{address}'. Full Geoapify response: {geo_data}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Geoapify API request failed for address '{address}': Network or HTTP error: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during Geoapify geocoding for address '{address}': {e}")
        return None, None

def get_soil_properties_from_soilgrids(latitude, longitude):
    """
    Fetches various soil properties from SoilGrids by ISRIC API for a given lat/long.
    Only includes properties in the output if data is available.

    Arguments:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: A dictionary of available soil properties from SoilGrids, or an empty dict
              if data cannot be fetched, along with status notes.
    """
    if latitude is None or longitude is None:
        return {
            "note": "Soil data from SoilGrids could not be fetched due to missing or failed geolocation."
        }

    soil_properties_from_soilgrids = {}
    
    properties_to_fetch = [
        ("clay", "clay_content", 10, "g/100g (%)"),
        ("sand", "sand_content", 10, "g/100g (%)"),
        ("silt", "silt_content", 10, "g/100g (%)"),
        ("phh2o", "pH", 10, "pH"),
        ("soc", "organic_carbon_content", 10, "g/kg"),
        ("nitrogen", "nitrogen_content", 100, "g/kg")
    ]

    depth_interval = "0-5cm" 
    value_type = "mean"      

    all_texture_data_available = True
    any_soil_data_fetched = False

    for prop_id, display_name, conversion_factor, unit in properties_to_fetch:
        params = {
            "lon": longitude,
            "lat": latitude,
            "property": prop_id,
            "depth": depth_interval,
            "value": value_type
        }

        try:
            soil_response = requests.get(SOILGRIDS_API_BASE_URL, params=params)
            soil_response.raise_for_status()
            soil_data = soil_response.json()

            if soil_data and soil_data.get('properties') and soil_data['properties'].get('mean') is not None:
                raw_value = soil_data['properties']['mean']['values'][0]
                converted_value = round(raw_value / conversion_factor, 2)
                soil_properties_from_soilgrids[display_name] = f"{converted_value} {unit}"
                any_soil_data_fetched = True
            else:
                if prop_id in ["clay", "sand", "silt"]:
                    all_texture_data_available = False
        except requests.exceptions.RequestException as e:
            if prop_id in ["clay", "sand", "silt"]:
                all_texture_data_available = False
        except Exception as e:
            if prop_id in ["clay", "sand", "silt"]:
                all_texture_data_available = False
            
    if all_texture_data_available and all(p in soil_properties_from_soilgrids for p in ["clay_content", "sand_content", "silt_content"]):
        try:
            clay_val = float(str(soil_properties_from_soilgrids["clay_content"]).split(' ')[0])
            sand_val = float(str(soil_properties_from_soilgrids["sand_content"]).split(' ')[0])
            silt_val = float(str(soil_properties_from_soilgrids["silt_content"]).split(' ')[0])
            
            if clay_val >= 40:
                soil_type_derived = "Clay"
            elif sand_val >= 70:
                soil_type_derived = "Sandy"
            elif silt_val >= 60:
                soil_type_derived = "Silty"
            elif sand_val > 50 and clay_val < 20:
                soil_type_derived = "Sandy Loam"
            elif clay_val >= 20 and sand_val < 50 and silt_val < 50:
                soil_type_derived = "Clay Loam"
            else:
                soil_type_derived = "Loamy"
            
            soil_properties_from_soilgrids["soil_type_derived_from_soilgrids"] = soil_type_derived
        except ValueError:
            soil_properties_from_soilgrids["soil_type_derived_from_soilgrids"] = "Cannot derive (parsing error)"
        except KeyError:
            soil_properties_from_soilgrids["soil_type_derived_from_soilgrids"] = "Cannot derive (missing data fields)"
    else:
        soil_properties_from_soilgrids["soil_type_derived_from_soilgrids"] = "Not derived (texture data unavailable from SoilGrids)"

    if not any_soil_data_fetched:
        soil_properties_from_soilgrids["general_note_soilgrids_data_status"] = "Detailed soil property data from SoilGrids was not available for this location."

    return soil_properties_from_soilgrids

def get_soil_from_bhuvan_api(latitude, longitude):
    """
    Attempts to get soil data from a hypothetical Bhuvan API endpoint.
    This is highly experimental and relies on guessing the API structure.
    """
    bhuvan_soil_data = {"status": "Not Attempted"}

    if latitude is None or longitude is None:
        bhuvan_soil_data["status"] = "Failed (Missing lat/lon)"
        return bhuvan_soil_data

    
    params = {
        "lat": latitude,
        "lon": longitude,
        
    }

    try:
        
        response = requests.get(BHUVAN_API_SOIL_BASE_URL, params=params, timeout=10)
        response.raise_for_status() 
        
        bhuvan_response_json = response.json()
        
        bhuvan_soil_data = {
            "status": "Attempted",
            "response_status_code": response.status_code,
            "raw_response": bhuvan_response_json,
            "note": "Raw response from hypothetical Bhuvan API. Structure and content unknown without documentation."
        }
        

    except requests.exceptions.Timeout:
        bhuvan_soil_data["status"] = "Failed (Request Timeout)"
        bhuvan_soil_data["error_message"] = "Bhuvan API request timed out."
    except requests.exceptions.RequestException as e:
        bhuvan_soil_data["status"] = "Failed (Network/HTTP Error)"
        bhuvan_soil_data["error_message"] = f"Bhuvan API request failed: {e}"
        if response is not None:
            bhuvan_soil_data["response_status_code"] = response.status_code
            try:
                bhuvan_soil_data["raw_response"] = response.json() 
            except ValueError:
                bhuvan_soil_data["raw_response"] = response.text 
    except Exception as e:
        bhuvan_soil_data["status"] = "Failed (Unexpected Error)"
        bhuvan_soil_data["error_message"] = f"An unexpected error occurred with Bhuvan API: {e}"

    return bhuvan_soil_data

def get_soil_type_from_postgis(latitude, longitude):
    """
    Queries a local PostGIS database for soil type at a given lat/long.
    Returns the soil type string or None if not found/error.
    """
    
    import psycopg2 

    if latitude is None or longitude is None:
        return None, "Missing latitude or longitude for PostGIS query."

    conn = None
    soil_type = None
    error_message = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        
        cur.execute(f"SELECT to_regclass('{POSTGIS_TABLE_NAME}');")
        if not cur.fetchone()[0]:
            return None, f"PostGIS table '{POSTGIS_TABLE_NAME}' does not exist."
        
        cur.execute(f"SELECT '{POSTGIS_SOIL_TYPE_COLUMN}' FROM {POSTGIS_TABLE_NAME} LIMIT 1;")
    
    
        query = f"""
        SELECT {POSTGIS_SOIL_TYPE_COLUMN}
        FROM {POSTGIS_TABLE_NAME}
        WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
        """
        cur.execute(query, (longitude, latitude))
        result = cur.fetchone()

        if result:
            soil_type = result[0] 
        else:
            error_message = f"No soil data found in local PostGIS DB for {latitude}, {longitude}."

        cur.close()

    except psycopg2.Error as e:
        error_message = f"PostGIS database error: {e}"
        print(f"PostGIS Error: {e}")
    except Exception as e:
        error_message = f"An unexpected error occurred during PostGIS query: {e}"
        print(f"Unexpected PostGIS Query Error: {e}")
    finally:
        if conn:
            conn.close()
    
    return soil_type, error_message


@app.route('/pincode/<int:pin_code>', methods=['GET'])
def get_pincode_details(pin_code):
    """
    API endpoint to retrieve address details, geolocation, and soil properties for a given Indian PIN code.
    It combines data from 'postalpincode.in' (for address), 'Geoapify' (for geolocation),
    a hypothetical Bhuvan API (experimental), 'SoilGrids by ISRIC' (for soil properties),
    and a local PostGIS DB (if set up), with a fallback for general soil type by state.

    Arguments:
        pin_code (int): A 6-digit Indian Postal Index Number (PIN code).

    Returns:
        JSON response containing address details, geolocation, and soil properties.
        - Success (200 OK): If details are found.
        - Bad Request (400): If the PIN code format is invalid or Geoapify API key is missing.
        - Not Found (404): If no postal address details found.
        - Internal Server Error (500): For API connection issues or unexpected errors.
    """
    
    if not (100000 <= pin_code <= 999999):
        return jsonify({
            "status": "Error",
            "message": "Invalid PIN code format. PIN code must be a 6-digit number."
        }), 400


    postal_api_url = f"{POSTALPINCODE_API_BASE_URL}{pin_code}"
    address_details_list = []
    status_message = ""
    state_from_pincode = None

    try:
        postal_response = requests.get(postal_api_url)
        postal_response.raise_for_status()
        postal_data = postal_response.json()

        if postal_data and isinstance(postal_data, list) and postal_data[0].get("Status") == "Success":
            address_details_list = postal_data[0].get("PostOffice", [])
            status_message = f"Details found for PIN code {pin_code}."
            if address_details_list:
                state_from_pincode = address_details_list[0].get('State', '').upper()
        else:
            status_message = postal_data[0].get("Message", f"No address details found for PIN code {pin_code}.") \
                            if postal_data and isinstance(postal_data, list) else "Unexpected response from postalpincode.in."

    except requests.exceptions.RequestException as e:
        status_message = f"Failed to fetch address from postalpincode.in: {e}"
        print(f"Error fetching address from postalpincode.in: {e}")
    except Exception as e:
        status_message = f"An unexpected error occurred with postalpincode.in data: {e}"
        print(f"Unexpected error (postalpincode.in): {e}")

    #Fetch Geolocation from Geoapify (tiered approach for robustness)
    latitude, longitude = None, None
    geolocation_note = "Geolocation attempted via Geoapify."

    if address_details_list:
        first_po = address_details_list[0]
        current_pincode_in_address = str(pin_code)

        # Tiered address construction for Geoapify
        address_tiers = [
            f"{first_po.get('Name', '')}, {first_po.get('Block', '')}, {first_po.get('District', '')}, {first_po.get('State', '')} {current_pincode_in_address}, India",
            f"{first_po.get('District', '')}, {first_po.get('State', '')} {current_pincode_in_address}, India",
            f"{current_pincode_in_address}, India"
        ]
        
        for address_str in address_tiers:
            
            cleaned_address_parts = [part.strip() for part in address_str.split(',') if part.strip()]
            cleaned_address_str = ", ".join(cleaned_address_parts)
            
            if cleaned_address_str:
                print(f"Attempting Geoapify for: '{cleaned_address_str}'")
                latitude, longitude = get_geolocation_from_geoapify(cleaned_address_str)
                if latitude is not None and longitude is not None:
                    geolocation_note = f"Geolocation successfully obtained from Geoapify using '{cleaned_address_str}'."
                    break 
            else:
                print(f"Skipping empty or malformed address string: '{address_str}'")
    
    if latitude is None and longitude is None:
        geolocation_note = "Geolocation could not be determined by Geoapify after multiple attempts or missing postal data."
        print(f"Final Geoapify status: {geolocation_note}")
    
    # Fetch Soil Data: Prioritize Bhuvan API (experimental), then PostGIS, then SoilGrids, then Fallback
    final_soil_info = {
        "data_source_priority": "1. Bhuvan API (experimental) -> 2. Local PostGIS (most granular) -> 3. SoilGrids (global detailed) -> 4. General by State (broadest fallback)",
        "bhuvan_api_attempt": {}, # New field for Bhuvan API response
        "postgis_local_soil_type": "Not available (PostGIS not queried or no data)",
        "detailed_from_soilgrids": {},
        "general_by_state": {}
    }

    
    if latitude is not None and longitude is not None:
        bhuvan_response = get_soil_from_bhuvan_api(latitude, longitude)
        final_soil_info["bhuvan_api_attempt"] = bhuvan_response
    else:
        final_soil_info["bhuvan_api_attempt"]["note"] = "Bhuvan API not attempted due to missing or failed geolocation."


    
    if latitude is not None and longitude is not None:
        
        if DB_CONFIG["password"] != "your_pg_password" and DB_CONFIG["user"] != "your_pg_user" and POSTGIS_SOIL_TYPE_COLUMN != "soil_type_name_from_your_data":
            postgis_soil_type, postgis_error = get_soil_type_from_postgis(latitude, longitude)
            if postgis_soil_type:
                final_soil_info["postgis_local_soil_type"] = postgis_soil_type
            else:
                final_soil_info["postgis_local_soil_type"] = "Not available or error: " + (postgis_error if postgis_error else "No data found.")
        else:
            final_soil_info["postgis_local_soil_type"] = "Not attempted (PostGIS configuration incomplete in app.py)"
    else:
        final_soil_info["postgis_local_soil_type"] = "Not attempted (Geolocation failed, so PostGIS not queried)."


    
    if latitude is not None and longitude is not None:
        soil_properties_from_apis = get_soil_properties_from_soilgrids(latitude, longitude)
        if soil_properties_from_apis:
            final_soil_info["detailed_from_soilgrids"] = soil_properties_from_apis
        else:
            final_soil_info["detailed_from_soilgrids"]["note"] = "Soil data from SoilGrids could not be fetched for this location."
    else:
        final_soil_info["detailed_from_soilgrids"]["note"] = "Soil data from SoilGrids could not be fetched due to missing or failed geolocation."


    general_soil_types_list = []
    if state_from_pincode:
        general_soil_types_list = STATE_SOIL_MAP.get(state_from_pincode, [])
    
    general_soil_properties_summary = {}
    if general_soil_types_list:
        for soil_type_name in general_soil_types_list:
            cleaned_soil_type_name = soil_type_name.strip()
            if cleaned_soil_type_name in GENERAL_SOIL_PROPERTIES_MAP:
                general_soil_properties_summary[cleaned_soil_type_name] = GENERAL_SOIL_PROPERTIES_MAP[cleaned_soil_type_name]["key_characteristics"]
            else:
                general_soil_properties_summary[cleaned_soil_type_name] = ["Properties not defined in map or not available"]
    else:
        general_soil_properties_summary["note"] = "No general soil types defined for this state or state not found."

    final_soil_info["general_by_state"] = {
        "main_types": ", ".join(general_soil_types_list) if general_soil_types_list else "Not available",
        "properties_summary": general_soil_properties_summary
    }


    
    if address_details_list:
        results = []
        for po in address_details_list:
            results.append({
                "address_details": {
                    "name": po.get("Name"),
                    "branch_type": po.get("BranchType"),
                    "delivery_status": po.get("DeliveryStatus"),
                    "circle": po.get("Circle"),
                    "district": po.get("District"),
                    "division": po.get("Division"),
                    "region": po.get("Region"),
                    "state": po.get("State"),
                    "country": po.get("Country"),
                    "pincode": po.get("PINCode")
                },
                "geolocation": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "note": geolocation_note
                },
                "soil_information": final_soil_info,
                "note": "Address details from postalpincode.in; Geolocation from Geoapify; Soil information prioritized from Bhuvan API (experimental), then local PostGIS, then SoilGrids, then general state soil data."
            })
        
        return jsonify({
            "status": "Success",
            "message": status_message,
            "data": results
        }), 200
    else:
        return jsonify({
            "status": "Error",
            "message": status_message,
            "data": [{
                "address_details": "No postal address details found for this PIN code from primary API.",
                "geolocation": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "note": geolocation_note
                },
                "soil_information": final_soil_info,
                "note": "Geolocation from Geoapify; Soil information prioritized from Bhuvan API (experimental), then local PostGIS, then SoilGrids, then general state soil data. If lat/long/soil are None/empty, data might not be available or API had an issue."
            }]
        }), 404

# This block ensures the Flask development server runs when the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
