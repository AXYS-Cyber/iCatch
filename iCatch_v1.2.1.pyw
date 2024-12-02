import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Toplevel
import sqlite3
import base64
import pandas as pd
from io import BytesIO
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import simplekml
import zipfile
import math
import hashlib
from datetime import datetime, timedelta
import os

 
#Creates horizontal accuracy radius/circle    
def create_circle(lat, lon, radius, num_segments=12):  # Default to 12 segments, limited to reduce size of file.
    coords = []
    for i in range(num_segments):
        angle = math.radians(float(i) / num_segments * 360)
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        
        d_lat = dy / 111320  # Latitude degrees per meter
        d_lon = dx / (111320 * math.cos(math.radians(lat)))  # Longitude degrees per meter (adjusted by latitude)
        
        point_lat = lat + d_lat
        point_lon = lon + d_lon
        
        coords.append((point_lon, point_lat))

    return coords

image_base64 = """
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
"""

# Function to hash files (md5, sha1)
def hash_file(file_path):
    md5_hash = hashlib.md5()
    sha1_hash = hashlib.sha1()

    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
            sha1_hash.update(byte_block)

    return md5_hash.hexdigest(), sha1_hash.hexdigest()

# Main function to query database and generate CSV, KMZ, and Log
def generate_outputs():
    org = org_var.get()
    examiner = examiner_var.get()
    case_num = case_num_var.get()
    device_info = device_var.get()
    db_path = db_var.get()
    output_folder = output_var.get()
    icon_color = cache_color_var.get()

     
    if not all([org, examiner, case_num, device_info, db_path, output_folder]):
        messagebox.showerror("Error", "Please fill all fields.")
        return

    if date_filter_var.get():
        start_dt = start_date_var.get() + " " + start_time_var.get()
        end_dt = end_date_var.get() + " " + end_time_var.get()

        # Convert start and end to datetime objects for validation
        try:
            start_datetime = datetime.strptime(start_dt, '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(end_dt, '%Y-%m-%d %H:%M:%S')

            if end_datetime < start_datetime:
                messagebox.showerror("Error", "End date/time cannot be earlier than start date/time.")
                return
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date/time format: {e}")
            return

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(output_folder, f'iCatch Results {timestamp}')
    os.makedirs(output_dir, exist_ok=True)

    # Base SQLite query
    query = """
    SELECT 
        ZRTCLLOCATIONMO.Z_PK AS 'Record ID',
        DATETIME(978307200 + CAST(ZTIMESTAMP AS REAL), 'unixepoch') || '.' || 
        SUBSTR(CAST((ZTIMESTAMP - CAST(ZTIMESTAMP AS INTEGER)) * 1000 AS INTEGER) + 1000, 2, 3) AS 'Timestamp',
        PRINTF('%.6f', ZRTCLLOCATIONMO.ZLATITUDE) AS 'Latitude',
        PRINTF('%.6f', ZRTCLLOCATIONMO.ZLONGITUDE) AS 'Longitude',
        PRINTF('%.2f', ZRTCLLOCATIONMO.ZHORIZONTALACCURACY) AS 'Horizontal Accuracy (M)'
    """

    # Add Speed and Course columns if checkbox is selected
    if speed_course_var.get():
        query += """,
        CASE 
            WHEN ZSPEED < 0 THEN 'Invalid/No Speed'
            ELSE PRINTF('%.1f', ZSPEED * 2.23694)
        END AS "Speed (MPH)",
        CASE 
            WHEN ZCOURSE < 0 THEN 'Invalid/No Course'
            ELSE 
                CASE
                    WHEN ZCOURSE >= 348.75 OR ZCOURSE < 11.25 THEN 'N'
                    WHEN ZCOURSE >= 11.25 AND ZCOURSE < 33.75 THEN 'NNE'
                    WHEN ZCOURSE >= 33.75 AND ZCOURSE < 56.25 THEN 'NE'
                    WHEN ZCOURSE >= 56.25 AND ZCOURSE < 78.75 THEN 'ENE'
                    WHEN ZCOURSE >= 78.75 AND ZCOURSE < 101.25 THEN 'E'
                    WHEN ZCOURSE >= 101.25 AND ZCOURSE < 123.75 THEN 'ESE'
                    WHEN ZCOURSE >= 123.75 AND ZCOURSE < 146.25 THEN 'SE'
                    WHEN ZCOURSE >= 146.25 AND ZCOURSE < 168.75 THEN 'SSE'
                    WHEN ZCOURSE >= 168.75 AND ZCOURSE < 191.25 THEN 'S'
                    WHEN ZCOURSE >= 191.25 AND ZCOURSE < 213.75 THEN 'SSW'
                    WHEN ZCOURSE >= 213.75 AND ZCOURSE < 236.25 THEN 'SW'
                    WHEN ZCOURSE >= 236.25 AND ZCOURSE < 258.75 THEN 'WSW'
                    WHEN ZCOURSE >= 258.75 AND ZCOURSE < 281.25 THEN 'W'
                    WHEN ZCOURSE >= 281.25 AND ZCOURSE < 303.75 THEN 'WNW'
                    WHEN ZCOURSE >= 303.75 AND ZCOURSE < 326.25 THEN 'NW'
                    WHEN ZCOURSE >= 326.25 AND ZCOURSE < 348.75 THEN 'NNW'
                END || ' - ' || PRINTF('%.1f', ZCOURSE) || ' degrees'
        END AS "Course Direction"
        """

    # Add date filter if selected
    if date_filter_var.get():
        query += f"""
        FROM ZRTCLLOCATIONMO
        WHERE ZRTCLLOCATIONMO.ZTIMESTAMP >= strftime('%s', '{start_dt}') - strftime('%s', '2001-01-01 00:00:00')
        AND ZRTCLLOCATIONMO.ZTIMESTAMP <= strftime('%s', '{end_dt}') - strftime('%s', '2001-01-01 00:00:00')
        """
    else:
        query += " FROM ZRTCLLOCATIONMO "

    query += "ORDER BY ZRTCLLOCATIONMO.ZTIMESTAMP ASC;"

    # Run SQLite query and save results as CSV
    try:
        df = pd.read_sql_query(query, conn)
        if speed_course_var.get():
            if "Speed (MPH)" not in df.columns or "Course Direction" not in df.columns:
                messagebox.showerror("Error", "Speed and Course columns are missing from the query results.")
                return
        
        # Convert columns to numeric after query
        df['Horizontal Accuracy (M)'] = pd.to_numeric(df['Horizontal Accuracy (M)'], errors='coerce')
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

        csv_file = os.path.join(output_dir, f"{case_num}_{datetime.now().strftime('%Y%m%d_%H%M')}_output.csv")
        df.to_csv(csv_file, index=False)
    finally:
        conn.close()
    
    # Get the selected accuracy limit from the dropdown
    accuracy_limit_selection = accuracy_limit_var.get()
    if accuracy_limit_selection == "No Limit":
        accuracy_limit = float('inf')  # No limit
    else:
        accuracy_limit = float(accuracy_limit_selection)

    # Add a column to indicate whether the record was included in the KMZ
    df['Included in KMZ'] = df['Horizontal Accuracy (M)'] <= accuracy_limit

    csv_file = os.path.join(output_dir, f"{case_num}_{datetime.now().strftime('%Y%m%d_%H%M')}_output.csv")
    df.to_csv(csv_file, index=False)
    
    
    # Split records into batches of 10,000 for KMZ files to reduce size of final file
    num_records = len(df)
    batch_size = 10000
    for batch_num in range(0, num_records, batch_size):
        batch_df = df.iloc[batch_num:batch_num+batch_size]

        # Filter batch based on horizontal accuracy
        batch_df_kmz = batch_df[batch_df['Horizontal Accuracy (M)'] <= accuracy_limit]

        kmz_file = os.path.join(output_dir, f"{case_num}_{datetime.now().strftime('%Y%m%d_%H%M')}_part{batch_num // batch_size + 1}.kmz")

        # Create KMZ file for each batch
        create_kmz(batch_df_kmz, kmz_file, org, examiner, case_num, device_info)

    # Hash the input (database) file
    db_md5, db_sha1 = hash_file(db_path)
    
    # Generate log and hash values for CSV and KMZ files
    log_file = os.path.join(output_dir, f"{case_num}_{datetime.now().strftime('%Y%m%d_%H%M')}_log.txt")
    with open(log_file, 'w') as log:
        log.write(f"***********************************************************************\n***********************************************************************\n** iCatch - iOS Cache Analysis for Tracking Coordinates History v1.1 **\n** Created by: \tAaron Willmarth, CFCE,\t\t\t\t\t\t\t\t **\n**\t\t\t\tAXYS Cyber Solutions\t\t\t\t\t\t\t\t **\n**\t\t\t\thttps://github.com/AXYS-Cyber/iCatch\t\t\t\t **\n***********************************************************************\n***********************************************************************\n\n\n")

        log.write(f"Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        log.write(f"Target File: {db_var.get()}\n")
        log.write(f"Target File Hashes: MD5: {db_md5} / SHA1: {db_sha1}\n\n")
        log.write(f"Output directory: {output_folder}\n\n")
        log.write(f"*****CASE INFORMATION*****\n")
        log.write(f"Organization: {org}\nExaminer: {examiner}\nCase #: {case_num}\nDevice Info: {device_info}\n**************************\n\n")
        # Log output options
        log.write(f"******OUTPUT OPTIONS******\n")
        if date_filter_var.get():
            start_dt = start_date_var.get() + " " + start_time_var.get()
            end_dt = end_date_var.get() + " " + end_time_var.get()
            log.write(f"Date filter options:\n")
            log.write(f"\tStart Date/Time: {start_dt}\n")
            log.write(f"\tEnd Date/Time: {end_dt}\n")
        else:
            log.write(f"No date filter applied\n")
            
        if accuracy_limit_selection == "No Limit":
            log.write(f"Accuracy filter selection: No limit selected\n")
        else:
            log.write(f"Accuracy filter selection: {accuracy_limit_selection} meters or less\n")
        log.write(f"Icon Color: {icon_color}\n")
        log.write(f"****************************\n\n")
        log.write(f"Output Files:\n")
        
        if speed_course_var.get(): 
            log.write(f"Speed and course direction included.\n")
        else:
            log.write(f"Speed and course direction not included.\n")
        
        # Loop through all files in the output directory, hash, and log them
        for root, dirs, files in os.walk(output_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name != os.path.basename(log_file):  # Exclude log file from hashing
                    log.write(f"File: {file_name}\n")  
                    
                    # Calculate and log file hashes
                    file_md5, file_sha1 = hash_file(file_path)  
                    log.write(f"\tFile hashes: MD5: {file_md5} / SHA1: {file_sha1}\n\n")
                else:
                    log.write(f"File: {file_name} (Log file, not hashed)\n\n")
                
        # After writing the log file and generating the KMZs
        if messagebox.askyesno("Success", "Outputs generated successfully. Do you want to open the directory?"):
            open_directory(output_dir)

def open_directory(path):
    """Open the directory using the default file explorer."""
    try:
        if os.name == 'nt':  # For Windows
            os.startfile(path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open directory: {e}")
        

# Function to create KMZ files
def create_kmz(df, kmz_file, org, examiner, case_num, device_info):
    kml = simplekml.Kml()
    
    # Get the selected color from the dropdown
    selected_color = cache_color_var.get()

    # Define a mapping of colors to KML icon URLs and styles
    color_map = {
        "Red": ('http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png', simplekml.Color.red),
        "Green": ('http://maps.google.com/mapfiles/kml/pushpin/grn-pushpin.png', simplekml.Color.green),
        "Blue": ('http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png', simplekml.Color.blue),
        "Yellow": ('http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png', simplekml.Color.yellow),
        "Purple": ('http://maps.google.com/mapfiles/kml/pushpin/purple-pushpin.png', simplekml.Color.purple),
    }
    
    # Default values if color is not found
    icon_href, pin_color = color_map.get(selected_color, 
                                          ('http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png', simplekml.Color.red))

    
    # Create a KML layer with case_num and device_info in the name
    folder = kml.newfolder(name=f"{case_num} - {device_info} Points")
    folder.visibility = 0  # Set visibility to 0 to hide initially

  
    for _, row in df.iterrows():
        record_number = row['Record ID']
        lat = row['Latitude'] 
        lon = row['Longitude']
        start_time = pd.to_datetime(row['Timestamp']).strftime("%Y-%m-%dT%H:%M:%S.") + f"{pd.to_datetime(row['Timestamp']).microsecond // 1000:03d}Z"
        accuracy = row['Horizontal Accuracy (M)']
        
        if speed_course_var.get():
            speed = row['Speed (MPH)']
            direction = row['Course Direction']
            
        # Create placemark and description
        pnt = folder.newpoint(name=f"{record_number}", coords=[(lon, lat)])  # Add to folder, not KML directly
        pnt.timestamp.when = start_time

        # Static text (organized in a table for two columns)
        static_text = f"""
        <table>
            <tr>
                <td style="vertical-align:top; padding-right:10px;">
                    <img src="data:image/png;base64,{image_base64}" alt="Logo" width="88" height="118">
                </td>
                <td style="vertical-align:top;">
                    <b style='font-size: 16px;'>{org},</b><br>
                    {examiner}, <br>
                    {case_num}, <br>
                    {device_info}
                </td>
            </tr>
        </table>
        """

       # Full description with side-by-side layout
        description = (
            f"{static_text}<br><br>"
            f"Timestamp (UTC):<br> {start_time}<br><br>"
            f"Lat: {lat}, Long: {lon}<br>"
            f"Accuracy: {accuracy} meters<br>"
        )

        # Conditional part for speed and direction
        if speed_course_var.get():
            description += (
                f"Speed: {speed} MPH,<br>"
                f"Direction: {direction}"
            )

        pnt.description = description


        # Style the pin (transparency and color based on selection)
        pnt.style.iconstyle.icon.href = icon_href
        pnt.style.iconstyle.color = simplekml.Color.changealpha('96', pin_color)  # 60% transparency
        pnt.style.iconstyle.scale = 1.0  # Standard size for pin
        pnt.style.visibility = 0

        # Add a circular polygon to represent the horizontal accuracy
        accuracy_circle = folder.newpolygon(name=f"Accuracy for Record {record_number}")  # Add to folder
        accuracy_circle.outerboundaryis = create_circle(lat, lon, radius=accuracy)

        # Set the same timestamp for the polygon (to sync with the placemark)
        accuracy_circle.timestamp.when = start_time

        # Style the circle (color based on selection)
        accuracy_circle.style.polystyle.color = simplekml.Color.changealpha('96', pin_color)  # 60% transparency
        accuracy_circle.style.polystyle.outline = 1  # Add outline for better visibility
        accuracy_circle.style.linestyle.color = pin_color  # Set outline color
        accuracy_circle.visibility = 0

    # Save KML and KMZ
    kml.save("temp.kml")
    with zipfile.ZipFile(kmz_file, 'w') as kmz:
        kmz.write("temp.kml")
    os.remove("temp.kml")

###############
## GUI Setup ##
###############
window = tk.Tk()
window.title("iCatch - iOS Cache Analysis for Tracking Coordinates History, v1.2")

#Sets the initial size of the window
initial_width = 700
initial_height = 325
window.geometry(f'{initial_width}x{initial_height}')

# Center the window on the screen
window.update_idletasks()  # Ensure window dimensions are calculated
width = window.winfo_width()
height = window.winfo_height()
x = (window.winfo_screenwidth() // 2) - (width // 2)
y = (window.winfo_screenheight() // 2) - (height // 2)
window.geometry('{}x{}+{}+{}'.format(width, height, x, y))



# Decode the base64 string and create an image
image_data = base64.b64decode(image_base64)
image = Image.open(BytesIO(image_data))
photo = ImageTk.PhotoImage(image)

# Decode the Base64 string to bytes
icon_data = base64.b64decode(image_base64)

# Create an image from the decoded bytes
icon_image = Image.open(BytesIO(icon_data))
icon_photo = ImageTk.PhotoImage(icon_image)

# Set the icon using the PhotoImage object
window.iconphoto(False, icon_photo)

# Create image label
image_label = tk.Label(window, image=photo)
image_label.grid(row=0, column=8, rowspan=16, padx=2, pady=2)

def show_about():
    # Create a new window for the "About" section
    about_window = Toplevel(window)
    about_window.title("About")
    
    # Center the window on the screen
    about_window.update_idletasks()  # Ensure window dimensions are calculated
    width = about_window.winfo_width()
    height = about_window.winfo_height()
    x = (about_window.winfo_screenwidth() // 2) - (width // 2)
    y = (about_window.winfo_screenheight() // 2) - (height // 2)
    about_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # Set size and center the window
    about_window.geometry("600x400")
    about_window.resizable(False, False)
    
    # Add text to the "About" window
    about_text = """iCatch - iOS Cache Analysis for Tracking Coordinates History, v1.2
    Created by: Aaron Willmarth, CFCE,
                        AXYS Cyber Solutions
        See https://github.com/AXYS-Cyber/iCatch for license information.
    This utility allows you to export GPS data from the iOS Cache.SQLite database, 
    generate CSV and KMZ files, and log details for analysis.
    
    How to use:
    1.	Input case information.
    2.	Select path of Cache.sqlite database which is found at: 
            private/var/mobile/Library/Caches/com.apple.routined/Cache.sqlite
    3.	Select desired color for pin and accuracy ring.
    4.	Select radius filter to limit the maximum radius of horizontal accuracy.
    5.	Select Date/Time filter options. This option is enabled by default. 
        a.	It is highly recommended to use this option as the database contains tens 
            of thousands of points, and can have thousands of points in a short timeframe.
    
    *************
    All times are reported in Coordinated Universal Time (UTC-0)
    Due to their size, multiple KMZ files may be generated and are limited to 10,000 records each.
    *************
    
    For more information about this, including speed artifacts, check out the amazing work by
    Scott Koenig at:
    https://theforensicscooter.com/2021/09/22/iphone-device-speeds-in-cache-sqlite-zrtcllocationmo/
    """
    
    # Add a Label widget with the text
    tk.Label(about_window, text=about_text, justify="left", padx=10, pady=10).pack()

def triage_dates():
    db_path = db_var.get()

    if not db_path:
        messagebox.showerror("Error", "Please select Cache.Sqlite database path.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT 
        date(datetime('2001-01-01', ZRTCLLOCATIONMO.ZTIMESTAMP || ' seconds')) AS 'Date',
        COUNT(*) AS 'Count'
    FROM ZRTCLLOCATIONMO
    GROUP BY Date
    ORDER BY Date DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()

    if not results:
        messagebox.showinfo("No Data", "No records found.")
        return

    # Create a pop-up window to display the results
    result_window = tk.Toplevel()
    result_window.title("Counts by Date")
    
     # Center the window on the screen
    result_window.update_idletasks()  # Ensure window dimensions are calculated
    width = result_window.winfo_width()
    height = result_window.winfo_height()
    x = (result_window.winfo_screenwidth() // 2) - (width // 2)
    y = (result_window.winfo_screenheight() // 2) - (height // 2)
    result_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # Padding at the top before records
    top_padding_label = tk.Label(result_window, text="")
    top_padding_label.pack(pady=(10, 0))  # 20px padding at the top

    # Display the date counts in the pop-up
    for i, (date, count) in enumerate(results):
        result_label = tk.Label(result_window, text=f"{date}: {count} records")
        result_label.pack()

    # Display the total number of records at the bottom
    total_records = sum(count for _, count in results)
    total_label = tk.Label(result_window, text=f"Total records: {total_records}")
    total_label.pack(pady=(10, 20))  # 10px padding above, 20px padding below (bottom of window)

    # Adjust the height after packing all content
    result_window.update_idletasks()
    result_window.geometry(f"275x{result_window.winfo_reqheight()+35}")  # Adjust the height

    # Button to close the result window
    close_button = tk.Button(result_window, text="Close", command=result_window.destroy)
    close_button.pack()


# Organization, Examiner, Case, and Device Info Inputs
org_var = tk.StringVar()
examiner_var = tk.StringVar()
case_num_var = tk.StringVar()
device_var = tk.StringVar()
db_var = tk.StringVar()
output_var = tk.StringVar()
cache_color_var = tk.StringVar()
accuracy_limit_var = tk.StringVar(value="No Limit")
speed_course_var= tk.BooleanVar()
speed_course_var.set(False)

tk.Label(window, text="Organization").grid(row=0, column=0)
tk.Entry(window, textvariable=org_var).grid(row=0, column=1)

tk.Label(window, text="Examiner").grid(row=0, column=3)
tk.Entry(window, textvariable=examiner_var).grid(row=0, column=4)

tk.Label(window, text="Case #").grid(row=2, column=0)
tk.Entry(window, textvariable=case_num_var).grid(row=2, column=1)

tk.Label(window, text="Device Info").grid(row=2, column=3)
tk.Entry(window, textvariable=device_var).grid(row=2, column=4)

tk.Label(window, text="Database Path").grid(row=4, column=0)
db_entry = tk.Entry(window, textvariable=db_var)
db_entry.grid(row=4, column=1)
tk.Button(window, text="Browse", command=lambda: db_var.set(filedialog.askopenfilename(filetypes=[("SQLite Files", "*.sqlite")]))).grid(row=4, column=2)


tk.Label(window, text="Output Location").grid(row=4, column=3)
tk.Entry(window, textvariable=output_var).grid(row=4, column=4)
tk.Button(window, text="Browse", command=lambda: output_var.set(filedialog.askdirectory())).grid(row=4, column=5)

tk.Button(window, text="Triage Dates", command=triage_dates).grid(row=5, column=1)####ADDEDED#######

# Output options frame with border
output_options_frame = tk.LabelFrame(window, text="Output Options", bd=2, relief="solid")

output_options_frame.grid(row=6, column=0, columnspan=8, padx=4, pady=4)

# List of colors for the drop-down menu
color_options = ["Red", "Green", "Blue", "Yellow", "Purple"]

# Drop-down list (Combobox) for selecting a color for cache icons
tk.Label(output_options_frame, text="Select Icon Color").grid(row=0, column=0)
color_combobox = ttk.Combobox(output_options_frame, textvariable=cache_color_var, values=color_options, state="readonly")
color_combobox.grid(row=0, column=1)
color_combobox.current(0)  # Set the default selection (first color in the list)

tk.Label(output_options_frame, text="Accuracy Limit (M):").grid(row=0, column=3)
accuracy_options = ["No Limit", "10", "25", "50", "100", "200", "500"]  
tk.OptionMenu(output_options_frame, accuracy_limit_var, *accuracy_options).grid(row=0, column=4)

tk.Checkbutton(output_options_frame, text="Include Speed and Direction", variable=speed_course_var).grid(row=1, column=0, columnspan=2)

# Date Filter Options
date_filter_var = tk.BooleanVar()
date_filter_var.set(True)
start_date_var = tk.StringVar()
start_time_var = tk.StringVar(value="00:00:00")
end_date_var = tk.StringVar()
end_time_var = tk.StringVar(value="23:59:59")

# Options frame with border
cache_options_frame = tk.LabelFrame(window, text="Date/Time Filter Options (all outputs in UTC-0)", bd=2, relief="solid")

cache_options_frame.grid(row=8, column=0, columnspan=8, padx=4, pady=4)

tk.Checkbutton(cache_options_frame, text="Use Date/Time Filter", variable=date_filter_var).grid(row=0, column=0, columnspan=2)

tk.Label(cache_options_frame, text="Start Date:").grid(row=2, column=0)
start_date_picker = DateEntry(cache_options_frame, textvariable=start_date_var, date_pattern='yyyy-mm-dd')
start_date_picker.grid(row=2, column=1)

tk.Label(cache_options_frame, text="Start Time (HH:MM:SS)").grid(row=2, column=3)
tk.Entry(cache_options_frame, textvariable=start_time_var).grid(row=2, column=4)


tk.Label(cache_options_frame, text="End Date:").grid(row=4, column=0)
end_date_picker = DateEntry(cache_options_frame, textvariable=end_date_var, date_pattern='yyyy-mm-dd')
end_date_picker.grid(row=4, column=1)

tk.Label(cache_options_frame, text="End Time (HH:MM:SS)").grid(row=4, column=3)
tk.Entry(cache_options_frame, textvariable=end_time_var).grid(row=4, column=4)

# Button to generate CSV, KMZ, and log
tk.Button(window, text="Generate Outputs", command=generate_outputs).grid(row=21, column=8, columnspan=3, pady=20)

tk.Button(window, text="About", command=show_about).grid(row=21, column=0, columnspan=3, pady=20)



window.mainloop()