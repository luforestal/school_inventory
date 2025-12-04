## School Inventory – Interactive Tree Maps for Schools

This repository provides a lightweight Python tool to generate interactive web maps of school tree inventories from simple input datasets:

📊 Excel inventory files

🗺️ School boundary shapefiles

📷 Photographs of individual trees

The tool produces fully interactive maps that allow users to explore tree locations, species, size, canopy extent, and photographs directly from the map interface.

It is designed to be:

✅ Easy to use for non-technical users (via Google Colab)
✅ Replicable for any school campus
✅ Fully open-source and customizable
✅ Suitable for education, citizen science, and urban forestry outreach

## Features

- 📍 Tree locations plotted from GPS coordinates
- 🌳 Symbol shapes and colors by genus for visual identification
- 🌫 Canopy area visualization
- 🏫 School boundary overlay (shapefile)
- 📸 Photo pop-ups linked to individual trees by Tree Code
- 🌐 Export of shareable interactive HTML maps
- ☁️ Seamless execution in Google Colab with cloud-stored datasets
- 
## Typical Workflow

1. Prepare a ZIP package containing:
   - Excel tree inventory file
   - School boundary shapefile
   - Tree photographs
   - (Optional) school logo  

2. Upload the ZIP package to **Google Drive**.

3. Open the provided **Google Colab notebook** and run a single cell to:
   - Download the input data  
   - Automatically generate the interactive school tree map
