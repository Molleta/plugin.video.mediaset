import xbmc
import xbmcgui

def list_videos():
    # Example function to list videos
    videos = [
        {'title': 'Video 1', 'url': 'http://example.com/video1'},
        {'title': 'Video 2', 'url': 'http://example.com/video2'}
    ]
    return videos


def play_video(video_url):
    # Example function to play a video
    xbmc.Player().play(video_url)

if __name__ == '__main__':
    videos = list_videos()
    for video in videos:
        print(video['title'])