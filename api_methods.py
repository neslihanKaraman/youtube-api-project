import pandas as pd

def collect_video_ids(youtube, playlist_id):
    """
    Get list of video IDs of all videos in the given playlist
    
    Params:
    
    youtube: the build object from googleapiclient.discovery
    playlist_id: playlist ID of the channel
    
    Returns:
    List of video IDs of all videos in the playlist
    
    """

    video_ids = []

    request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
    response = request.execute()

    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])

    next_page_token = response.get('nextPageToken')
    
    while next_page_token is not None:
        request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')    

        
    return video_ids


def collect_video_details(youtube, video_ids):
    """
    Get video statistics of all videos with given IDs
    
    Params:
    
    youtube: the build object from googleapiclient.discovery
    video_ids: list of video IDs
    
    Returns:
    Dataframe with statistics of videos, i.e.:
        'channelTitle', 'title', 'description', 'tags', 'publishedAt'
        'viewCount', 'likeCount', 'favoriteCount', 'commentCount'
        'duration', 'definition', 'caption'
    """
        
    all_video_info = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute() 

        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']
                            }
            video_info = {}
            video_info['video_id'] = video['id']

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None

            all_video_info.append(video_info)
            
    return pd.DataFrame(all_video_info)

def collect_channel_stats(youtube, channel_ids):
    
    """
    Get channel statistics: title, subscriber count, view count, video count, upload playlist

    Params:

    youtube: the build object from googleapiclient.discovery
    channels_ids: list of channel IDs
    
    Returns:
    Dataframe containing the channel statistics for all channels in the provided list: title, subscriber count, view count, video count, upload playlist
    
    """

    all_data = []
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=",".join(channel_ids)
    )

    response = request.execute()

    # loop through items in response
    for item in response["items"]:
        data = {'channelName': item['snippet']['title'],
                'subscribers': item['statistics']['subscriberCount'],
                'views': item['statistics']['viewCount'],
                'totalVideos': item['statistics']['videoCount'],
                'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
        }
        all_data.append(data)
    
    return pd.DataFrame(all_data)



def get_all_channel_comments(youtube, video_id):
    """
    Get all comments along with usernames for a specific video.

    This function retrieves all comments along with the usernames for the specified video by utilizing pagination
    (if available) to fetch all comments.

    Args:
        youtube: The build object from googleapiclient.discovery.
        video_id: The ID of the video for which comments will be retrieved.

    Returns:
        comments: A list of dictionaries containing 'Comment' (the comment text) and 'User Name' (the username).
    """
    comments = []
    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            comment_info = {
                'Comment': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                'User Name': item['snippet']['topLevelComment']['snippet']['authorDisplayName']  # Kullanıcı adını ekleyin
            }
            comments.append(comment_info)

        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    return comments



def get_comment_length(comments):

    """Returns a list of calculated comment lengths.

    This function calculates the length of each comment in the provided list of comments and returns a list of comment lengths.

    Args:
        comments: A list containing comments. Each comment should be a dictionary with the key 'Comment'.

    Returns:
        comment_lengths: A list containing the length of comments.
    """
    comment_lengths = []

    for comment in comments:
       comment_length = len(comment['Comment'])  # calculated comment lengths
       comment_lengths.append(comment_length)  # adds the calculated length to the list

    return comment_lengths



def get_all_comments_statistics(youtube, video_id):
    """
    Returns a dictionary containing the count of unique comments made by each user for a specific video.

    It calculates the count of unique comments made by each user and stores this information in a dictionary.

    Args:
        youtube: The build object from googleapiclient.discovery.
        video_id: ID of the video for which comments will be retrieved.

    Returns:
        comments_statistics: A dictionary where keys are usernames and values are counts of unique comments made by each user.
    """
    comments_statistics = {}
    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            if username in comments_statistics:
                comments_statistics[username] += 1
            else:
                comments_statistics[username] = 1

        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break
        
    return comments_statistics
