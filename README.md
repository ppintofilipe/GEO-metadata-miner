# GEO-metadata-miner
Captures metadata from a list of GEO series provided in an excel file.

## Install
Create a python virtual environment and install dependencies in the `requirements.txt` file.

## Run
Paste the relevant GEO series in the `relevant_samples.xlsx` file. The script takes it to know which metadata to look for.

A new file `available_categories.xlsx` is created to allow the user to congregate metadata categories. (this line is commented in the code, to allow the usage of our current example)

A new excel file is produced after running the script containing the congregated classes, and relevant information.
