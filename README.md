School Inventory – Interactive Tree Maps for Schools

This repository provides a lightweight Python tool to create interactive web maps of school tree inventories using:

Excel inventory files

School boundary shapefiles

Photographs of individual trees

The tool produces fully interactive maps where users can explore tree locations, species, tree size, canopy extent, and view photos directly on the map.

It is designed to be:

✅ Easy to use for non-technical users (via Google Colab)
✅ Replicable for any school campus
✅ Fully open-source and customizable
✅ Suitable for education, citizen science, and urban forestry outreach

Features

📍 Tree locations plotted using GPS coordinates

🌳 Shapes and colors by genus for visual identification

🌫 Canopy area visualization

🏫 School boundary overlay (shapefile)

📸 Tree photo pop-ups linked by Tree Code

🌐 Produces shareable interactive HTML maps

☁️ Works seamlessly in Google Colab with cloud-stored datasets

Typical Workflow

Prepare a ZIP package containing:

Excel tree inventory

Boundary shapefile

Tree photos

Optional school logo

Upload the ZIP file to Google Drive.

Open the provided Google Colab notebook and run a single cell to:

Download the data

Generate the interactive school tree map
