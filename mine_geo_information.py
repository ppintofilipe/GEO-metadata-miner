#!/usr/bin/env python

"""
This script retrieves metadata from GEO (Gene Expression Omnibus) datasets and saves it in Excel files.

Author: Pedro Matos Filipe
License: GPL
Version: 1.0.1
Email: pedro.filipe@anaxomics.com
Status: Production
"""

import pandas as pd
import GEOparse
import os
from datetime import datetime
import math

# Function to access GEO sample metadata
def access_geo_sample(GSE):
    """
    Accesses the metadata of a GEO sample.

    Parameters:
    - GSE (str): GEO accession number of the sample.

    Returns:
    - global_samples (dict): Dictionary containing the sample metadata.
    """
    gse = GEOparse.get_GEO(geo=GSE, destdir="./", silent=True, how='brief')
    
    gse_file = GSE + '.txt'
    with open(gse_file, 'r', encoding="utf8") as gse_meta:
        gse_meta = gse_meta.readlines()
    
    global_samples = {}
    curr_gsm = None
    for i in gse_meta:
        if i.startswith('^'):
            ids = i.split(' = ')
            curr_gsm = ids[1].strip()
        else:
            if curr_gsm:
                if i.startswith('!Sample_title'):
                    title = i.split(' = ')
                    title = title[1].strip()
                    
                    if curr_gsm in global_samples:
                        global_samples[curr_gsm].append(['Title', title])
                    else:
                        global_samples[curr_gsm] = [['Title', title]]
                        
                if i.startswith('!Sample_source_name_ch1'):
                    source = i.split(' = ')
                    source = source[1]
                    
                    if curr_gsm in global_samples:
                        global_samples[curr_gsm].append(['Source', source])
                    else:
                        global_samples[curr_gsm] = [['Source', source]]
                        
                if i.startswith('!Sample_scan_protocol'):
                    scan = i.split(' = ')
                    scan = source[1]
                    
                    if curr_gsm in global_samples:
                        global_samples[curr_gsm].append(['Scan', scan])
                    else:
                        global_samples[curr_gsm] = [['Scan', scan]]
                
                if i.startswith('!Sample_organism_ch1'):
                    org = i.split(' = ')
                    org = org[1]
                    
                    if curr_gsm in global_samples:
                        global_samples[curr_gsm].append(['Organism', org])
                    else:
                        global_samples[curr_gsm] = [['Organism', org]]
                
                if i.startswith('!Sample_characteristics_ch'):
                    char = i.split(' = ')
                    char = char[1].split(': ')
                    
                    if curr_gsm in global_samples:
                        global_samples[curr_gsm].append([char[0], char[1]])
                    else:
                        global_samples[curr_gsm] = [[char[0], char[1]]]

    os.remove(gse_file)
    
    return global_samples


# Function to read relevant samples from an Excel file
def read_relevant_samples(axfile):
    """
    Reads the relevant samples from an Excel file.

    Parameters:
    - axfile (str): Path to the Excel file.

    Returns:
    - axsamples (list): List of relevant samples.
    """
    axsamples = pd.read_excel(axfile)
    axsamples = axsamples['Dataset'].to_list()
    
    return axsamples


# Function to get AX dataset metadata
def get_ax_dataset_metadata(axfile):
    """
    Retrieves the metadata of datasets.

    Parameters:
    - axfile (str): Path to the Excel file containing the dataset information.

    Returns:
    - ax_meta (dict): Dictionary containing the dataset metadata.
    """
    axsamples = read_relevant_samples(axfile)
    
    ax_meta = {}
    for i in axsamples:
        ax_meta[i] = access_geo_sample(i)
    
    return ax_meta


if __name__ == "__main__": # check if the script being executed is the main module
    
    axfilemeta = get_ax_dataset_metadata('relevant_samples.xlsx')

    all_available_categories = []

    for i in axfilemeta.keys():
        for j in axfilemeta[i].keys():
            for k in axfilemeta[i][j]:
                if k[0] not in all_available_categories:
                    all_available_categories.append(k[0])
                    
    curr_date = datetime.now().strftime("%Y-%m-%d")
    
    '''
    This file is created the first time the script is executed. 
    All the classes in the geo samples are saved in this file.
    The user can aggregate the classes in the 'UNIFIED_CATEGORIES' column, and simplify the metadata file.
    
    (!)
    The file is commented, so you can use the prefilled file 'available_categories.xlsx' to simplify the metadata file.
    '''
    # result = pd.DataFrame({'AVAILABLE_CATEGORIES': all_available_categories}).to_excel(f'{curr_date}_available_categories.xlsx', index=False)

    categories_dictionary = pd.read_excel('available_categories.xlsx')
    variables_to_save = categories_dictionary['UNIFIED_CATEGORIES'].to_list()
    variables_to_save = list(set([i for i in variables_to_save if str(i) != 'nan']))

    final_dataframe = {'GSE': [], 'GSM': [], 'Title': [], 'Organism': [], 'Source': [], 'Scan protocol': []}

    for experiment_id in axfilemeta.keys():
        experiment = axfilemeta[experiment_id]
        
        for patient_id in experiment.keys():
            patient = experiment[patient_id]
            title = [x[1].strip('\n') for x in patient if x[0] == 'Title'][0]
            organism = [x[1].strip('\n') for x in patient if x[0] == 'Organism'][0]
            source = [x[1].strip('\n') for x in patient if x[0] == 'Source'][0]
            scan = [x[1].strip('\n') for x in patient if x[0] == 'Scan']
            if len(scan) > 0:
                scan = scan[0]
            else:
                scan = math.nan
            
            
            final_dataframe['GSE'].append(experiment_id)
            final_dataframe['GSM'].append(patient_id)
            
            final_dataframe['Title'].append(title)
            final_dataframe['Organism'].append(organism)
            final_dataframe['Source'].append(source)
            final_dataframe['Scan protocol'].append(scan)
            
            for idx_category in variables_to_save:
                save_variables = categories_dictionary[categories_dictionary['UNIFIED_CATEGORIES'] == idx_category]['AVAILABLE_CATEGORIES'].to_list()
                
                relevant_var = [x[1].strip('\n') for x in patient if x[0] in save_variables]
                
                if len(relevant_var) == 0:
                    relevant_var = math.nan
                else:
                    relevant_var = relevant_var[0]
                
                if idx_category in final_dataframe.keys():
                    final_dataframe[idx_category].append(relevant_var)
                else:
                    final_dataframe[idx_category] = [relevant_var]

    final_dataframe = pd.DataFrame(final_dataframe)

    final_dataframe.to_excel(f'{curr_date}_NAFLD_experimentsmetadata.xlsx', index=False)