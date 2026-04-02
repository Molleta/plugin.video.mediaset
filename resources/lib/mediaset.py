"""
Mediaset Scraper Module
Handles scraping of Mediaset live channels and on-demand content
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

class MediasetScraper:
    def __init__(self):
        self.base_url = 'https://mediasetinfinity.mediaset.it'
        self.api_url = 'https://api.mediasetinfinity.mediaset.it'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
    
    def get_live_channels(self):
        """Fetch live TV channels"""
        try:
            url = f'{self.api_url}/catalog/live'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            channels = []
            if 'channels' in data:
                for channel in data['channels']:
                    ch = {
                        'id': channel.get('id'),
                        'title': channel.get('name', 'Unknown'),
                        'url': channel.get('stream_url'),
                        'icon': channel.get('logo_url'),
                        'description': channel.get('description', '')
                    }
                    channels.append(ch)
            
            logger.info(f"Found {len(channels)} live channels")
            return channels
        
        except requests.RequestException as e:
            logger.error(f"Error fetching live channels: {e}")
            return []
    
    def get_on_demand(self):
        """Fetch on-demand content"""
        try:
            url = f'{self.api_url}/catalog/vod'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            if 'videos' in data:
                for video in data['videos']:
                    v = {
                        'id': video.get('id'),
                        'title': video.get('title', 'Unknown'),
                        'description': video.get('description', ''),
                        'icon': video.get('thumbnail'),
                        'url': video.get('url'),
                        'duration': video.get('duration'),
                        'release_date': video.get('release_date')
                    }
                    videos.append(v)
            
            logger.info(f"Found {len(videos)} videos")
            return videos
        
        except requests.RequestException as e:
            logger.error(f"Error fetching on-demand content: {e}")
            return []
    
    def get_series(self):
        """Fetch TV series"""
        try:
            url = f'{self.api_url}/catalog/series'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            series = []
            if 'series' in data:
                for s in data['series']:
                    serie = {
                        'id': s.get('id'),
                        'title': s.get('title', 'Unknown'),
                        'description': s.get('description', ''),
                        'icon': s.get('poster_url'),
                        'seasons': s.get('seasons', 0)
                    }
                    series.append(serie)
            
            logger.info(f"Found {len(series)} series")
            return series
        
        except requests.RequestException as e:
            logger.error(f"Error fetching series: {e}")
            return []
    
    def get_series_episodes(self, series_id):
        """Get episodes for a specific series"""
        try:
            url = f'{self.api_url}/catalog/series/{series_id}/episodes'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            episodes = []
            if 'episodes' in data:
                for episode in data['episodes']:
                    ep = {
                        'id': episode.get('id'),
                        'title': episode.get('title', 'Unknown'),
                        'season': episode.get('season'),
                        'episode': episode.get('episode'),
                        'url': episode.get('url'),
                        'duration': episode.get('duration')
                    }
                    episodes.append(ep)
            
            logger.info(f"Found {len(episodes)} episodes")
            return episodes
        
        except requests.RequestException as e:
            logger.error(f"Error fetching episodes: {e}")
            return []
