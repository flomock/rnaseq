import pandas as pd
import sys
import requests
from bs4 import BeautifulSoup
import urllib.parse
import urllib.request

csv_input_file = str(sys.argv[1])
species = str(sys.argv[2])

# check which species
if species == "eco":
    url_prefix = 'https://bacteria.ensembl.org/Escherichia_coli_k_12/Gene/Summary?g='
elif species == "hsa":
    url_prefix = 'https://ensembl.org/Homo_sapiens/Gene/Summary?g='
elif species == "mmu":
    url_prefix = 'https://ensembl.org/Mus_musculus/Gene/Summary?g='
else:
    print(f"species: {species} not supported")
    print("therefore no function casting available")
    exit()

# load file and setup some variables
df = pd.read_csv(csv_input_file)
gene_functions = []
uniprot = []
url = 'https://www.uniprot.org/uploadlists/'

# get the uniprot ids for all ensembleids
query = " ".join(df['ensemblID'])
params = {
'from': 'ENSEMBL_ID',
'to': 'ACC',
'format': 'tab',
'query': query
}

data = urllib.parse.urlencode(params)
data = data.encode('utf-8')
req = urllib.request.Request(url, data)
with urllib.request.urlopen(req) as f:
   response = f.read()
uniprot_pre = response.decode('utf-8').strip()
uniprot_pre = uniprot_pre.split("\n")[1:]

# create dict (handy for multi-matches with sometime no function)
ensemble_old = ""
uniprot_post = {}
for i in uniprot_pre:
    ensemble_i, uniprot_i = i.split("\t")
    uniprot_entries = uniprot_post.get(ensemble_i,[])
    uniprot_entries.append(uniprot_i)
    uniprot_post.update({ensemble_i:uniprot_entries})

# go over all ensemble ids in inputfile
for ensemble_id in df['ensemblID']:
    uniprot_entries = uniprot_post.get(ensemble_id,[])

    # check for function
    if len(uniprot_entries) > 0:
        for uniprot_i in uniprot_entries:
            url_i = "http://www.uniprot.org/uniprot/"+uniprot_i
            response = requests.get(url_i)
            soup = BeautifulSoup(response.text, 'xml')
            description_tag = soup.find('meta', {'name': "description"})
            gene_function_i = description_tag.attrs.get("content", None)
            if gene_function_i != "":
                break
        print(gene_function_i[:80])
    else:
        uniprot_i = None
        gene_function_i = None


    uniprot.append(uniprot_i)
    gene_functions.append(gene_function_i)

# add uniprot ids and unction to table and save file
df["uniprot"] = uniprot
df["function"] = gene_functions
df.to_csv(csv_input_file)
