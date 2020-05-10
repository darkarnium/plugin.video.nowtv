''' Provides functions for formatting data ready for rendering. '''


def guidedata(schedule, plugin_uri='', aspect='16-9', image_size='400'):
    '''
    Attempts to transform the input schedule data from the Sky EPG into a
    format compatible with uEPG guidedata elements.

    Args:
        schedule (dict): A dictionary of schedule data from the NOW TV client.
        plugin_uri (string): The base URI for the generated playback URLs.
        aspect (string): The aspect ratio for thumbnails (default: '19-6')
        image_size (string): The width of thumbnails (default: '1000')

    Returns:
        A Python dictionary of uEPG guidedata.
    '''
    guidedata = []

    for show in schedule[0]['events']:
        # Thumbnails may be blank, so ensure they're handled appropriately.
        thumbnail = None
        if show['programmeImageUrlTemplate']:
            thumbnail = show['programmeImageUrlTemplate'].format(
                type='16-9',
                size='1000',
            )

        # TODO: Fallback for titles with no image(s):
        # https://nowtv.uk.imageservice.sky.com/pixel/selector/pcms/
        # Object 9df5ee80-a731-11e6-b70c-9b06f522d7ab

        # Render down the uEPG compatible guidedata, and append to the guide.
        definition = '[HD]' if show['isHD'] else ''
        guidedata.append(
            {
                'url': '{0}?playback=True&service_key={1}'.format(
                    plugin_uri,
                    schedule[0]['serviceKey']
                ),
                'starttime': show['startTimeEpoch'],
                'endtime': show['startTimeEpoch'] + show['durationInSeconds'],
                'runtime': show['durationInSeconds'],
                'rating': show['parentalRatingCode'],
                'plot': show['description'],
                'isnew': show['isNewShow'],
                'label': show['title'],
                'label2': definition,
                'art': {
                    'thumb': thumbnail,
                },
                'streamdetails': {
                    'video': '',
                },
                'raw': show,
            }
        )

    # Ready to go!
    return guidedata


def channeldata(channel, logo_width=75, logo_height=75):
    '''
    Attempts to transform the input channel data from the Sky EPG into a format
    compatible with uEPG channeldata elements.

    Args:
        channel (dict): A dictionary of Channel data from the NOW TV client.
        logo_width (int): The horizontal size of the logo to render in pixels.
        logo_height (int): The vertical size of the logo to render in pixels.

    Returns:
        A Python dictionary of uEPG channeldata.
    '''
    # Extract and construct the logo URI.
    logo = None
    for entry in channel['logo']:
        if entry['type'] == 'Dark':
            # Render the template out
            logo = entry['template'].format(
                key=entry['key'],
                width=logo_width,
                height=logo_height,
            )

    # Render down the uEPG compatible channeldata.
    return {
        'isHD': True if channel['formatType'] == 'HD' else False,
        'channelname': channel['channelName'],
        'channelnumber': channel['serviceKey'],
        'channellogo': logo,
        'isfavourite': False,
        'guidedata': [],
    }
