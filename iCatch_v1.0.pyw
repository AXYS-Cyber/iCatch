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
def create_circle(lat, lon, radius, num_segments=12):  # Limited to 12 segments to reduce size of KMZ output file.
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


# Base64 encoded image string
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

     
    if not all([org, examiner, case_num, device_info, db_path, output_folder]):
        messagebox.showerror("Error", "Please fill all fields.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(output_folder, f'Cache_GPS and KMZ Results {timestamp}')
    os.makedirs(output_dir, exist_ok=True)

    # Base SQLite query
    query = """
    SELECT 
        ZRTCLLOCATIONMO.Z_PK AS 'Record ID',
        datetime('2001-01-01', ZRTCLLOCATIONMO.ZTIMESTAMP || ' seconds') AS 'Timestamp',
        ZRTCLLOCATIONMO.ZLATITUDE AS 'Latitude',
        ZRTCLLOCATIONMO.ZLONGITUDE AS 'Longitude',
        ZRTCLLOCATIONMO.ZHORIZONTALACCURACY AS 'Horizontal Accuracy (M)'
    FROM ZRTCLLOCATIONMO
    """

    # Add date filter if selected
    if date_filter_var.get():
        start_dt = start_date_var.get() + " " + start_time_var.get()
        end_dt = end_date_var.get() + " " + end_time_var.get()
        query += f"""
        WHERE ZRTCLLOCATIONMO.ZTIMESTAMP >= strftime('%s', '{start_dt}') - strftime('%s', '2001-01-01 00:00:00')
        AND ZRTCLLOCATIONMO.ZTIMESTAMP <= strftime('%s', '{end_dt}') - strftime('%s', '2001-01-01 00:00:00')
        """

    query += "ORDER BY ZRTCLLOCATIONMO.Z_PK ASC;"

    # Run SQLitequery and save results as CSV
    df = pd.read_sql_query(query, conn)
    csv_file = os.path.join(output_dir, f"{case_num}_{datetime.now().strftime('%Y%m%d_%H%M')}_output.csv")
    df.to_csv(csv_file, index=False)
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

    # Generate log and hash values for CSV and KMZ files
    log_file = os.path.join(output_dir, f"{case_num}_{datetime.now().strftime('%Y%m%d_%H%M')}_log.txt")
    with open(log_file, 'w') as log:
        log.write(f"***********************************************************************\n***********************************************************************\n** iCATCH - iOS Cache Analysis for Tracking Coordinates History v1.0 **\n** Created by: \tAaron Willmarth, CFCE,\t\t\t\t\t\t\t\t **\n**\t\t\t\tAXYS Cyber Solutions\t\t\t\t\t\t\t\t **\n***********************************************************************\n***********************************************************************\n\n\n")

        log.write(f"Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        log.write(f"Target File: {db_var.get()}\n")
        log.write(f"Output directory: {output_folder}\n\n")
        log.write(f"*****CASE INFORMATION*****\n")
        log.write(f"Organization: {org}\nExaminer: {examiner}\nCase #: {case_num}\nDevice Info: {device_info}\n**********************\n\n")
        log.write(f"Output Files: ")
        
        log.write(f"CSV File: {csv_file}\n")
        csv_md5, csv_sha1 = hash_file(csv_file)
        log.write(f"CSV files hashes: MD5: {csv_md5} / CSV SHA1: {csv_sha1}\n")
        
        for batch_num in range(0, num_records, batch_size):
            kmz_file = os.path.join(output_dir, f"{case_num}_{datetime.now().strftime('%Y%m%d_%H%M')}_part{batch_num // batch_size + 1}.kmz")
            kmz_md5, kmz_sha1 = hash_file(kmz_file)
            log.write(f"KMZ file hashes:{batch_num // batch_size + 1} MD5: {kmz_md5} / SHA1: {kmz_sha1}\n")

        # After writing the log file and generating the KMZs
        if messagebox.askyesno("Success", "CSV, KMZ, and Log generated successfully. Do you want to open the directory?"):
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
        start_time = pd.to_datetime(row['Timestamp']).strftime("%Y-%m-%dT%H:%M:%SZ")
        accuracy = row['Horizontal Accuracy (M)']

        # Create placemark and description
        pnt = folder.newpoint(name=f"{record_number}", coords=[(lon, lat)])  # Add to folder, not KML directly
        pnt.timestamp.when = start_time

        static_text = f"<b style='font-size: 16px;'>{org},</b><br>{examiner}, <br>{case_num}, <br>{device_info}"
        pnt.description = (
            f"<img src='data:image/png;base64,{image_base64}' alt='Logo' width='112' height='104'><br>"
            f"{static_text}<br><br>"
            f"Start Time (UTC): {start_time}<br><br>"
            f"Latitude: {lat}<br>"
            f"Longitude: {lon}<br>"
            f"Accuracy: {accuracy} meters<br>"
        )

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
window.title("iCATCH - iOS Cache Analysis for Tracking Coordinates History, v1.0")

#Sets the initial size of the window
initial_width = 700
initial_height = 300
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
    about_text = """iCATCH - iOS Cache Analysis for Tracking Coordinates History
    Version 1.0
    Created by: Aaron Willmarth, CFCE,
                        AXYS Cyber Solutions
    
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
            of thousands of points and can have thousands of points in a short timeframe.
    
    *************
    All times are in Coordinated Universal Time (UTC-0)
    Due to their size, multiple KMZ files may be generated and are limited to 10,000 records each.
    *************
    
    For more information about this, including speed artifacts, check ou the amazing work by
    Scott Koenig at:
    https://theforensicscooter.com/2021/09/22/iphone-device-speeds-in-cache-sqlite-zrtcllocationmo/
    """
    
    # Add a Label widget with the text
    tk.Label(about_window, text=about_text, justify="left", padx=10, pady=10).pack()



# Organization, Examiner, Case, and Device Info Inputs
org_var = tk.StringVar()
examiner_var = tk.StringVar()
case_num_var = tk.StringVar()
device_var = tk.StringVar()
db_var = tk.StringVar()
output_var = tk.StringVar()
cache_color_var = tk.StringVar()
accuracy_limit_var = tk.StringVar(value="No Limit")

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
