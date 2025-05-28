import os, json, requests

PLUGIN_DIR = "plugins/"

def download_plugin_list(json_url):
    try:
        r = requests.get(json_url)
        r.raise_for_status()
        return r.json()  # should be a list of plugins
    except Exception as e:
        return {"error": str(e)}

def install_plugin(plugin):
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    try:
        response = requests.get(plugin["url"])
        filename = os.path.join(PLUGIN_DIR, plugin["name"] + ".py")
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        return False
