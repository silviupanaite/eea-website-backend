#!/usr/bin/env python3
import json
host = "https://www.eea.europa.eu/indicators"
real_host = "https://www.eea.europa.eu/en/analysis/indicators"
datafigure_host = "https://www.eea.europa.eu/api/SITE"

types_to_replace = {"ims_folder": "landing_page"}


def replace_host(data_string, the_host):
    data_string = data_string.replace('"@id": "https://www.eea.europa.eu/ims', f'"@id": "{the_host}')
    data_string = data_string.replace('https://www.eea.europa.eu/ims', f'{real_host}')
    return data_string

def replace_datafigure_host(data_string, the_host):
    data_string = data_string.replace("https://www.eea.europa.eu/api/SITE", the_host)
    return data_string


def replace_type(item, types):
    for type in types:
        if item["@type"] == type:
            item["@type"] = types[type]


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


# Opening JSON file
f = open("./ims.json")

data = f.read()
data = replace_host(data, host)
data = replace_datafigure_host(data, datafigure_host)
data = json.loads(data)

for item_index, item in enumerate(data):
    replace_type(item, types_to_replace)
    
    if "blocks" in item:
        blocks = item["blocks"]
        summary_parent = item["blocks"]
        summary = get_summary_block(blocks, [])

        if summary and summary[0] and summary[1]:
            for index, sid in enumerate(summary[0]):
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

            # Update title block to hide some metadata
            summary_parent["data"]["blocks"]["ddde07aa-4e48-4475-94bd-e1a517d26eab"].update({
                "hideContentType": True,
                "hideCreationDate": True,
                "hideModificationDate": True,
                "hideDownloadButton": True
            })

    if "exportimport.versions" in item:
        versions = item['exportimport.versions']
        for version_index in versions:
            version = versions[version_index]

            replace_type(version, types_to_replace)

            if "blocks" in version:
                blocks = version["blocks"]
                summary_parent = version["blocks"]
                
                summary = get_summary_block(blocks, [])


                if summary and summary[0] and summary[1]:
                    for index, sid in enumerate(summary[0]):
                        if sid in blocks:
                            summary_parent = blocks[sid]
                        else:
                            summary_parent = summary_parent["data"]["blocks"][sid]
                    slate_id = summary_parent["data"]["blocks"][summary[1]]["data"]["blocks_layout"]["items"][0]
                    slate_value = summary_parent["data"]["blocks"][summary[1]]["data"]["blocks"][slate_id]['value']
                    summary_parent["data"]["blocks"]["1c31c956-5086-476a-8694-9936cfa6c240"] = {
                        "@type": "description",
                        "value": slate_value,
                    }
                    summary_parent["data"]["blocks_layout"]["items"].append("1c31c956-5086-476a-8694-9936cfa6c240")

with open("./output.json", "w") as outfile:
    json.dump(data, outfile, indent = 2)

# Closing JSON file
f.close()
