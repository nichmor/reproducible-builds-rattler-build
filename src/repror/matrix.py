

import json
from repror import conf


if __name__ == "__main__":
    # Prepare the matrix
    matrix = {'include': []}

    config = conf.load_config()

    # Parse repositories and local paths
    for repo in config.get('repositories', []):
        url = repo['url']
        branch = repo['branch']
        for recipe in repo.get('recipes', []):
            path = recipe['path']
            matrix['include'].append({
                'url': url,
                'branch': branch,
                'recipe': path
            })

    for local in config.get('local', []):
        path = local['path']
        matrix['include'].append({
            'url': 'local',
            'branch': 'local',
            'recipe': path
        })

    # Convert the matrix to JSON
    matrix_json = json.dumps(matrix)
    print(matrix_json)