#!/usr/bin/env python3
""" Usage:

    python3 ims_migrate.py <input_file> <output_file>

"""
import json
import sys
from uuid import uuid4

debug_instance = "http://10.120.10.133:63954/www/SITE"
host = "https://www.eea.europa.eu/indicators"
real_host = "https://www.eea.europa.eu/en/analysis/indicators"
datafigure_host = "https://www.eea.europa.eu/api/SITE"

types_to_replace = {
    "ims_folder": "landing_page"
}

topics_to_replace = {
#   "default": "",
    "agriculture": "term1",                 # "Agriculture and food",
    "air": "term2",                         # "Air pollution",
    "7ngc5c6ofw": "term3",                  # "Bathing water quality",
    "biodiversity": "term4",                # "Biodiversity",
    "vr0t7tafrf": "term5",                  # "Bioeconomy",
    "m6sjg6oyuk": "term6",                  # "Buildings and construction",
    "6icr2anmn4": "term7",                  # "Chemicals",
    "qh5021piy3": "term8",                  # "Circular economy",
    "climate-change-adaptation": "term10",  # "Climate change adaptation",
    "climate": "term11",                    # "Climate change mitigation",
    "6vjrx6dm1j": "term13",                 # "Electric vehicles",
    "energy": "term14",                     # "Energy",
    "lod55xq213": "term15",                 # "Energy efficiency",
    "human": "term16",                      # "Environmental health impacts",
    "vr8719ygoe": "term17",                 # "Environmental inequalities",
    "8n6i7qsodf": "term18",                 # "Extreme weather",
    "02sx2jjmd4": "term19",                 # "Fisheries and aquaculture",
    "esbbbjatw8": "term20",                 # "Forests and forestry",
    "industry": "term22",                   # "Industry",
    "landuse": "term23",                    # "Land use",
    "oyiadbllt7": "term27",                 # "Noise",
    "7j3ao9vwh6": "term25",                 # "Nature protection and restoration",
    "sustainability-transitions": "term39", # "Sustainability solutions",
    "aabl5pvdgv": "term26",                 # "Nature-based solutions",
    "i87b2jno0c": "term28",                 # "Plastics",
    "07723e8f6t": "term29",                 # "Pollution",
    "ifrjqph5cn": "term30",                 # "Production and consumption",
    "ker3sp99hj": "term31",                 # "Renewable energy",
    "gcqeu4of1f": "term32",                 # "Resource use and materials",
    "l3fwryepgj": "term33",                 # "Road transport",
    "4otlq9kt9v": "term34",                 # "Seas and coasts",
    "soil": "term35",                       # "Soil",
    "x5o5fkk4xy": "term38",                 # "Sustainability challenges",
    "4g6nof0mwk": "term40",                 # "Sustainable finance",
    "gvnhkc6kx7": "term41",                 # "Textiles",
    "transport": "term42",                  # "Transport and mobility",
    "himvkjl0ok": "term43",                 # "Urban sustainability",
    "waste": "term44",                      # "Waste and recycling",
    "water": "term45",                      # "Water",
}

def cleanup(data_string):
    data_string = data_string.replace(debug_instance, "https://www.eea.europa.eu")
    data_string = data_string.replace('"ims"', '"indicators"')
    data_string = data_string.replace("customSummaryVariationId", "default")
    data_string = data_string.replace('"@id": "https://www.eea.europa.eu/ims', f'"@id": "{host}')
    data_string = data_string.replace('"id": "taxonomy_themes"', '"id": "topics"')
    data_string = data_string.replace('"i": "taxonomy_themes"', '"i": "topics"')
    data_string = data_string.replace('https://www.eea.europa.eu/ims', f'{real_host}')
    data_string = data_string.replace('/api/SITE', '')
    data_string = data_string.replace('"url": "/ims/station.jpeg"', '"url": "/en/analysis/indicators/station.jpeg"')
    data_string = data_string.replace('"/data-and-maps/', '"https://www.eea.europa.eu/data-and-maps/')
    data_string = data_string.replace(datafigure_host, "https://www.eea.europa.eu")
    return data_string

def replace_type(item):
    """ Replace type """
    for type in types_to_replace:
        if item["@type"] == type:
            item["@type"] = types_to_replace[type]

def replace_topics(item):
    """ Replace taxonomy_themes to topics """
    item['topics'] = []
    if item.get('taxonomy_themes', None) is None:
        return
    for theme in item['taxonomy_themes']:
        # Unkown themes are not migrated
        if theme in ["default", "natural"]:
            continue
        item['topics'].append(topics_to_replace[theme])
    del item['taxonomy_themes']

def remove_obsolete_fields(item):
    """ Remove obsolete fields: institutional_mandate and data_provenance
    """
    if item['@type'] != 'ims_indicator':
        return

    del item['institutional_mandate']
    del item['data_provenance']

    for block in item.get("blocks", {}).values():
        if block.get("@type", None) != "accordion":
            continue

        fields = block.get(
            "data", {}).get(
            "blocks", {}).get(
            "546a7c35-9188-4d23-94ee-005d97c26f2b", {}).get(
            "blocks", {}).get(
            "b5381428-5cae-4199-9ca8-b2e5fa4677d9", {}).get(
            "fields", [])

        for idx, field in enumerate(fields):
            if field.get('field', {}).get("id", None) == 'institutional_mandate':
                fields.pop(idx)
                break

            # Also handle data_provenance
            if field.get('field', {}).get("id", None) == 'data_provenance':
                field['field']['widget'] = 'data_provenance'

def get_summary_block(blocks, parents=[]):
    summary_block = None
    for block_id in blocks:
        block = blocks[block_id]
        if "title" in block and block["title"] == "Summary":
            summary_block = [parents, block_id]
            break
        if not summary_block and "data" in block and "blocks" in block["data"]:
            parents.append(block_id)
            summary_block = get_summary_block(
                blocks[block_id]["data"]["blocks"], parents
            )
    return summary_block

def fix_landing_page(item):
    if item['@type'] != 'ims_folder':
        return

    for block in item['blocks'].values():
        if block['@type'] != 'accordion':
            continue

        for pane in block['data']['blocks'].values():
            if pane['@type'] != 'accordionPanel':
                continue

            for listing in pane['blocks'].values():
                if listing['@type'] != 'listing':
                    continue

                for q in listing['query']:
                    if q["i"] in ['portal_type', 'review_state']:
                        q['o'] = "plone.app.querystring.operation.selection.any"
                        continue

                    if q["i"] != 'topics':
                        continue

                    v = []
                    for k in q['v']:
                        v.append(topics_to_replace[k])
                    q['v'] = v

                for q in listing['querystring']['query']:
                    if q["i"] in ['portal_type', 'review_state']:
                        q['o'] = "plone.app.querystring.operation.selection.any"
                        continue

                    if q["i"] != 'topics':
                        continue

                    v = []
                    for k in q['v']:
                        v.append(topics_to_replace[k])
                    q['v'] = v

def fix_summary_and_title(item):
    """ Fix summary and title blocks
    """
    if 'blocks' not in item:
        return

    blocks = item["blocks"]
    summary_parent = item["blocks"]
    summary = get_summary_block(blocks, [])

    if summary and summary[0] and summary[1]:
        for sid in summary[0]:
            if sid in blocks:
                summary_parent = blocks[sid]
            else:
                summary_parent = summary_parent["data"]["blocks"][sid]

        slate_id = summary_parent["data"]["blocks"][summary[1]]["data"]["blocks_layout"]["items"][0]
        slate_value = summary_parent["data"]["blocks"][summary[1]]["data"]["blocks"][slate_id]['value']
        slate_description = summary_parent["data"]["blocks"][summary[1]]["data"]["blocks"][slate_id]['plaintext']
        summary_parent["data"]["blocks"]["1c31c956-5086-476a-8694-9936cfa6c240"] = {
            "@type": "description",
            "value": slate_value,
        }
        summary_parent["data"]["blocks_layout"]["items"].append("1c31c956-5086-476a-8694-9936cfa6c240")
        item["description"] = slate_description

        # Drop obsolete blocks
        # Splitter
        del summary_parent["data"]["blocks"]['9f452ca7-172a-42e0-a699-8df0714c89f8']
        summary_parent["data"]["blocks_layout"]["items"].remove('9f452ca7-172a-42e0-a699-8df0714c89f8')

        # Old Summary
        del summary_parent["data"]["blocks"]["ca212ba0-859e-4e67-b610-debe0d498b74"]
        summary_parent["data"]["blocks_layout"]["items"].remove("ca212ba0-859e-4e67-b610-debe0d498b74")

        # Update title block to hide some metadata
        summary_parent["data"]["blocks"]["ddde07aa-4e48-4475-94bd-e1a517d26eab"].update({
            "hideContentType": True,
            "hideCreationDate": True,
            "hideModificationDate": True,
            "hideDownloadButton": True
        })

def fix_version_id(item, version):
    oid = item['@id']
    short_id = item['id']
    # Refs https://taskman.eionet.europa.eu/issues/253799#note-12
    # Fix version id and @id
    vid = version['@id']
    if vid != oid:
        version['@id'] = oid
    ver_id = version['id']
    if ver_id != short_id:
        version['id'] = short_id

def fix_data_provenance(item):
    if 'blocks' not in item:
        return

    for section in item.get('blocks').values():
        for block in section.get('data', {}).get('blocks', {}).values():
            if block.get('@type') != 'dataFigure':
                continue

            existing = set([])
            data_provenance = {"data": []}
            metadata = block.get('metadata', {})
            dataSources = metadata.get('dataSources', {}).get("value", [])

            for child in dataSources:
                items = child.get("children", [])
                for item in items:
                    link = item.get("data", {}).get("link", {}).get("external", {}).get("external_link", "")
                    if not link:
                        continue
                    link = link.strip("/").strip("/view")
                    if link in existing:
                        continue

                    existing.add(link)
                    text  = item.get("children", [])
                    title = ""
                    for t in text:
                        title = t.get("text", "")
                        if title:
                            break
                    data_provenance["data"].append({
                        "@id": f"{uuid4()}",
                        "link": link,
                        "title": title,
                        "organization": "",
                    })

            if data_provenance["data"]:
                block["data_provenance"] = data_provenance

            # Clenup obsolete dataSources
            if "dataSources" in metadata:
                del metadata["dataSources"]

            # Cleanup also obsolte institutionalMandate
            if "institutionalMandate" in metadata:
                del metadata["institutionalMandate"]

def update(data):
    """ Migrate IMS data to Plone 6
    """
    for item in data:
        fix_landing_page(item)
        replace_type(item)
        replace_topics(item)
        remove_obsolete_fields(item)
        fix_summary_and_title(item)
        fix_data_provenance(item)

        for version in item.get('exportimport.versions', {}).values():
            fix_version_id(item, version)
            replace_type(version)
            replace_topics(version)
            remove_obsolete_fields(version)
            fix_summary_and_title(version)
            fix_data_provenance(version)

def main(inp, out):
    data = {}
    # Read input file
    with open(inp) as f:
        json_data = cleanup(f.read())
        data = json.loads(json_data)
        update(data)

    # Write output file
    with open(out, "w") as ofile:
        json.dump(data, ofile, indent=2)

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "./ims.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "./output.json"
    main(inp, out)
