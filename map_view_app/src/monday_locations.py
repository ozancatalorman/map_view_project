from helpers.monday_api_connection import get_monday_api_key
import requests
import pandas as pd

def get_monday_locations(board_id):
    key = get_monday_api_key()
    headers = {"Authorization": key, "API-Version": "2024-04"}

    # Prepare query to get name, stage, latitude and longitude values
    query = ('query($board_id: ID!, $cursor: String) {boards(ids: [$board_id]) {items_page(limit: 500, cursor: $cursor) {cursor items {name status_column: column_values(ids:["status"]){text}location_column: column_values(ids:["location"]){... on LocationValue{lat lng}}}}}}')

    # Board id is not specified in case the related board changes into new one
    variables = {'board_id': board_id, 'cursor': None}
    post_data = {'query': query, 'variables': variables}
    # Execute initial HTTP request
    request = requests.post(url='https://api.monday.com/v2', json=post_data, headers=headers)
    response = request.json()

    if not response['data']['boards']:
        # If board is not found or permissoned
        print(f'Board with ID {board_id} not found or not correctly permissioned.')
        return pd.DataFrame()

    board_data = response['data']['boards'][0]
    cursor = board_data['items_page']['cursor']
    items = board_data['items_page']['items']

    # Pagination with 500 items each time
    while cursor is not None:
        variables['cursor'] = cursor
        post_data = {'query':query, 'variables':variables}
        request = requests.post(url='https://api.monday.com/v2', json=post_data, headers=headers)
        response = request.json()
        items.extend(response['data']['boards'][0]['items_page']['items'])
        cursor = response['data']['boards'][0]['items_page']['cursor']

    # Extracting and separating the values from the response data
    item_names, item_stages, item_lats, item_lngs = zip(*[
        (item['name'], item['status_column'][0]['text'], item['location_column'][0]['lat'], item['location_column'][0]['lng'])
        for item in items
    ])


    item_names = [stage + ":" + name for stage, name in zip(item_stages, item_names)]

    # Structuring it as a data frame
    item_df = pd.DataFrame({
        'name': item_names,
        'stage': item_stages,
        'lat': item_lats,
        'lng': item_lngs
    })

    return item_df

