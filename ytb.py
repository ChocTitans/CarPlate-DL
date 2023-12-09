from pytube import YouTube

# Replace 'youtube_video_url' with the URL of the video you want to download
video_url = 'https://www.youtube.com/watch?v=jvExiX2yMBc'

# Create a YouTube object
yt = YouTube(video_url)

# Filter for the highest resolution stream (1080p)
video_stream = yt.streams.filter(res='1080p').first()

# Download the video
if video_stream:
    video_stream.download()
    print("Video downloaded successfully!")
else:
    print("Couldn't find a 1080p resolution for this video.")
