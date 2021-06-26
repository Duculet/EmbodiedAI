import csv, os

from experiments.covid.config import config
from itertools import product

current_path = config["screen"]["current_path"]

output_path = current_path + "combined/"

parameters = list(product(config["environment"]["masks"],
                          config["environment"]["lockdowns"],
                          config["environment"]["p_vaccinations"]))

if not os.path.exists(output_path):
    os.mkdir(output_path)

for mask, lockdown, p_vax in parameters:
    m, l, v = str(mask), str(lockdown), str(p_vax)
    results_path = current_path + '%s-%s-%s/' % (m, l, v)
    scenario_path = output_path + '%s-%s-%s/' % (m, l, v)
    if not os.path.exists(scenario_path):
        os.mkdir(scenario_path)
    out_dict = {"Infection rate:": [], "Infection ATH:": [], "Hospitalization rate:": [], 
                "Hospitalization ATH:": [], "Death rate:": [], "Vaccinated ratio:": []}
    with open(scenario_path + 'results.csv', 'w', encoding="utf-8", newline='') as n:
        # create the csv writer
        writer = csv.writer(n)
        # write a row to the csv file
        headers = ['Infection rate:', 'Infection ATH:', 'Hospitalization rate:', 
                    'Hospitalization ATH:', 'Death rate:', 'Vaccinated ratio:']
        writer.writerow(headers)
        with open(results_path + 'results.csv', 'r', encoding="utf-8", newline='') as r:
            # create the csv reader
            reader = csv.reader(r)
            for m_c, l_c, v_c in reader:
                if m_c in headers:
                    out_dict[m_c].append(l_c)

        values = [comb for comb in zip(out_dict[headers[0]], out_dict[headers[1]], out_dict[headers[2]], out_dict[headers[3]], out_dict[headers[4]])]
        for c in values:
            writer.writerow(c)
                

            
            
    