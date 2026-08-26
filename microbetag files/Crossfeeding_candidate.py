import json
import pandas as pd

#once I obtained the results from microbetag pipeline. The exchanged metabolite candidates were obtained 
#by the intersection of list of seeds from consumer and list of non-seed from producer

#Step 1 Load data
# Load ModelSEED compounds
compounds = pd.read_csv(
    "compounds.tsv",
    sep="\t",
    low_memory=False
)

# Keep only needed columns and rename
compounds = compounds[["id", "name"]]
compounds.columns = ["ID", "Metabolite Name"]

# Build lookup dictionary
compound_dict = dict(
    zip(compounds["ID"], compounds["Metabolite Name"])
)

#Load seed and non-seed sets
with open("/Results/seed_compl/seeds.json") as f:
    seeds = json.load(f)
with open("/Results/seed_compl/nonseeds.json") as f:
    nonseeds = json.load(f)

#Load competition/cooperation scores
scores = pd.read_csv("/Resultsseed_compl/seed_scores.tsv", sep="\t")

rows = []

for consumer, seed_set in seeds.items():
    seed_set = set(seed_set)

    for producer, nonseed_set in nonseeds.items():
        if consumer == producer:
            continue

        nonseed_set = set(nonseed_set)
        exchanged = seed_set.intersection(nonseed_set)

        for met in exchanged:
            rows.append({
                "Producer": producer,
                "Consumer": consumer,
                "Metabolite": met
            })

pc_table = pd.DataFrame(rows)

pc_table = pc_table.merge(
    compounds,
    left_on="Metabolite",
    right_on="ID",
    how="left"
)

def map_metabolite_name(met_id):
    if met_id.startswith("cpd"):
        return compound_dict.get(met_id, "Unknown")
    else:
        return "Unknown"

pc_table = pc_table.merge(
    scores,
    left_on=["Producer", "Consumer"],
    right_on=["nodeA", "nodeB"],
    how="left"
)

pc_table_final = (
    pc_table
    .groupby(
        ["Producer", "Consumer", "CooperationScore", "CompetitionScore"],
        as_index=False
    )
    .agg(
        Num_metabolites=("Metabolite", "nunique"),
        Metabolites=("Metabolite", lambda x: ";".join(x)),
        Metabolite_Names=(
            "Metabolite",
            lambda x: ";".join(map_metabolite_name(m) for m in x)
        )
    )
)

output_path = "/Results/seed_compl/CrossFeeding.xlsx"
pc_table_final.to_excel(output_path, index=False)
