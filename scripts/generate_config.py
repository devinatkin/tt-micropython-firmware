import os
import sys
import json
from github import Github
import shutil

def main():
    print('Generating config...')

    # Get the file list from command line arguments
    file_list = sys.argv[1:]
    g = Github(os.environ.get('GITHUB_TOKEN'))

    # A hacky way to ensure that the Github API rate limit is respected
    (requests_remaining, request_limit) = g.rate_limiting
    print(f'Github API rate limit: {requests_remaining}/{request_limit}')
    if (requests_remaining < 500 or request_limit < 500):
        raise ValueError('Github API rate limit is too low. Please wait a few minutes and try again.')
    
    # Get the directory of the script and the paths of the starting and modified config files
    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    starting_config = os.path.join(scripts_dir,"config_default.ini")
    modified_config = os.path.join(scripts_dir,"config.ini")
    
    # Create a copy of the starting config file
    shutil.copy(starting_config, modified_config)

    with open(modified_config, 'a') as config_file:
        # Process the file list
        for file in file_list:
            # If the file is not a json file, raise an error
            if not os.path.isfile(file) or not file.endswith('.json'):
                raise ValueError(f'File {file} is not a json file')
               
            # Open the file
            with open(file, 'r') as json_file:
                # Read the file
                data = json_file.read()
                # Load the json data
                json_data = json.loads(data)
                projects = json_data['projects']

                # Iterate over the projects looking for a config.ini file in any of the projects
                for project in projects:
                    splitRepo = project["repo"].split('/')
                    userName = splitRepo[-2]
                    repoName = splitRepo[-1]
                    print(f'{userName} {repoName}')
                    repo = g.get_repo(f'{userName}/{repoName}')
                    try:
                        contents = repo.get_contents('tb/commander')
                        while contents:
                            file_content = contents.pop(0)
                            if file_content.type == "dir":
                                contents.extend(repo.get_contents(file_content.path))
                            else:
                                if file_content.name == 'config.ini':
                                    print(f'Config found for {userName}/{repoName}')
                                    content = file_content.decoded_content.decode('utf-8')
                                    config_file.write(content)
                                    config_file.flush()
                    except:
                        print(f"No Test found for {userName}/{repoName}")

        
    print('Config generated!')

if __name__ == '__main__':
    main()