# -*- coding: utf-8 -*-
import sys
import urllib.parse
import requests
import xbmc
import xbmcgui
import xbmcplugin

HANDLE = int(sys.argv[1])

TP_BASE = "https://data.entertainment.tv.theplatform.eu/entertainment/data"
PLAYER_BASE = "https://player.mitele.es/v2/video/"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
}

def build_url(query):
    return sys.argv[0] + '?' + urllib.parse.urlencode(query)

def http_json(url):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def add_dir(name, query, icon=""):
    url = build_url(query)
    li = xbmcgui.ListItem(label=name)
    if icon:
        li.setArt({"thumb": icon})
    xbmcplugin.addDirectoryItem(HANDLE, url, li, True)

def add_video(name, query, icon=""):
    url = build_url(query)
    li = xbmcgui.ListItem(label=name)
    if icon:
        li.setArt({"thumb": icon})
    li.setProperty("IsPlayable", "true")
    xbmcplugin.addDirectoryItem(HANDLE, url, li, False)

# -----------------------------
# ROOT
# -----------------------------
def root():
    add_dir("Series: La que se avecina", {"action": "serie", "seriesId": "MS000000111628"})
    add_dir("Directos", {"action": "directos"})
    xbmcplugin.endOfDirectory(HANDLE)

# -----------------------------
# SERIE → TEMPORADAS
# -----------------------------
def serie(seriesId):
    url = f"{TP_BASE}/Program?bySeriesId={seriesId}&schema=1.0&form=json"
    data = http_json(url)

    temporadas = {}

    for item in data.get("entries", []):
        season = item.get("tvSeasonNumber", 0)
        if season not in temporadas:
            temporadas[season] = []
        temporadas[season].append(item)

    for season in sorted(temporadas.keys()):
        add_dir(f"Temporada {season}", {"action": "temporada", "seriesId": seriesId, "season": season})

    xbmcplugin.endOfDirectory(HANDLE)

# -----------------------------
# TEMPORADA → EPISODIOS
# -----------------------------
def temporada(seriesId, season):
    url = f"{TP_BASE}/Program?bySeriesId={seriesId}&schema=1.0&form=json"
    data = http_json(url)

    for item in data.get("entries", []):
        if item.get("tvSeasonNumber") != int(season):
            continue

        title = item.get("title", "Episodio")
        guid = item.get("guid")
        thumb = item.get("thumbnails", {}).get("image_keyframe_poster", {}).get("url", "")

        add_video(title, {"action": "play", "video": guid}, thumb)

    xbmcplugin.endOfDirectory(HANDLE)

# -----------------------------
# DIRECTOS
# -----------------------------
def directos():
    url = f"{TP_BASE}/Program?byTags=Live&schema=1.0&form=json"
    data = http_json(url)

    for item in data.get("entries", []):
        title = item.get("title", "Directo")
        guid = item.get("guid")
        thumb = item.get("thumbnails", {}).get("image_keyframe_poster", {}).get("url", "")

        add_video(title, {"action": "play", "video": guid}, thumb)

    xbmcplugin.endOfDirectory(HANDLE)

# -----------------------------
# PLAYER / DRM
# -----------------------------
def play(video_id):
    url = f"{PLAYER_BASE}{video_id}"
    data = http_json(url)

    sources = data.get("sources", [])
    if not sources:
        xbmcgui.Dialog().notification("Mitele", "No hay stream disponible", xbmcgui.NOTIFICATION_ERROR)
        return

    source = sources[0]
    stream = source["src"]
    mime = source.get("type", "")
    drm = source.get("drm")

    li = xbmcgui.ListItem(path=stream)
    li.setProperty("inputstream", "inputstream.adaptive")

    if ".m3u8" in stream or "hls" in mime:
        li.setProperty("inputstream.adaptive.manifest_type", "hls")
    else:
        li.setProperty("inputstream.adaptive.manifest_type", "mpd")

    if drm:
        license_url = drm.get("licenseUrl", "")
        headers = drm.get("headers", {}) or {}
        auth = headers.get("Authorization", "")

        header_parts = []
        if auth:
            header_parts.append("Authorization=" + auth)
        header_parts.append("User-Agent=Kodi")
        header_str = "&".join(header_parts)

        li.setProperty("inputstream.adaptive.license_type", "com.widevine.alpha")
        li.setProperty("inputstream.adaptive.license_key", f"{license_url}|{header_str}|R{{SSM}}|")

    xbmcplugin.setResolvedUrl(HANDLE, True, li)

# -----------------------------
# ROUTER
# -----------------------------
if __name__ == "__main__":
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    action = params.get("action")

    if action is None:
        root()
    elif action == "serie":
        serie(params["seriesId"])
    elif action == "temporada":
        temporada(params["seriesId"], params["season"])
    elif action == "directos":
        directos()
    elif action == "play":
        play(params["video"])
