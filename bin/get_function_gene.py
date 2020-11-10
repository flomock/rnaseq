import pandas as pd
import sys
import requests
from bs4 import BeautifulSoup
import urllib.parse
import urllib.request

csv_input_file = str(sys.argv[1])
species = str(sys.argv[2])
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

df = pd.read_csv(csv_input_file)
gene_functions = []
uniprot = []
url = 'https://www.uniprot.org/uploadlists/'

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
# uniprot_pre = [i.split("\t") for i in uniprot_pre]

# remove duplicates in first line
ensemble_old = ""
uniprot_post = {}
for i in uniprot_pre:
    ensemble_i, uniprot_i = i.split("\t")
    uniprot_entries = uniprot_post.get(ensemble_i,[])
    uniprot_entries.append(uniprot_i)
    uniprot_post.update({ensemble_i:uniprot_entries})
# uniprot_post = []
# for i in uniprot_pre:
#     ensemble_i, uniprot_i = i.split("\t")
#     # if ensemble_i =="From":
#     #     continue
#     # else:
#     if ensemble_old == ensemble_i:
#         continue
#     else:
#         uniprot_post.append([ensemble_i,uniprot_i])
#         ensemble_old = ensemble_i

# i = 0
for ensemble_id in df['ensemblID']:
    # ensemble_i, uniprot_i = uniprot_post[i]

    # if ensemble_i == ensemble_id:
    uniprot_entries = uniprot_post.get(ensemble_id,[])
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

    # gene_function_i = None
    # uniprot_i = None
    # previous_link_ncbi = False # needed to only use correct uniprot link
    # response = requests.get(url_prefix + ensemble_id)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # links = soup.find_all('a')
    # for ensemble_id in links:
    #     url_i = ensemble_id.attrs.get('href', False)
    #     if url_i and url_i.startswith("http://www.uniprot.org") and previous_link_ncbi:
    #         uniprot_i = url_i[len("http://www.uniprot.org/uniprot/"):]
    #         response = requests.get(url_i)
    #         soup = BeautifulSoup(response.text, 'xml')
    #         description_tag = soup.find('meta', {'name': "description"})
    #         gene_function_i = description_tag.attrs.get("content", None)
    #         print(gene_function_i)
    #         break

        # elif url_i and url_i.startswith("http://www.ncbi"):
        #     previous_link_ncbi = True
        # else:
        #     previous_link_ncbi = False


    uniprot.append(uniprot_i)
    gene_functions.append(gene_function_i)

df["uniprot"] = uniprot
df["function"] = gene_functions
df.to_csv(csv_input_file)
# df.to_csv(csv_input_file.strip(".csv") + "_2.csv")
