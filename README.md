# Setup

1. Install [miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. Create and activate new conda environment

   ```
   conda create -n chiara_gesture python=3.8
   conda activate chiara_gesture
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Configure awscli
   ```
   aws configure
   ```
5. Set environment variables

   Create `.env` file with same variables as defined in [.env.example](.env.example) and fill them with your own values.

   Additionally, you can override [configuration](src/config.py) default values defining each corresponding environment variable name.

   For example, adding `LOCAL_DATA_PATH=/path/to/your/data` to `.env` file will override `config.LOCAL_DATA_PATH`, allowing choosing different path to data.
6. Install recommended extensions defined in [extensions.json](.vscode/extensions.json) file.

# Develop

## Run gesture_manager.py cli

To view all actions available:
```
python gesture_manager.py -h
```

To view specific options for given action, e.g. `rename_original_videos`
```
python gesture_manager.py rename_original_videos -h
```

To run and debug specific actions and its options, you can use existing launch configurations defined in [lanunch.json](.vscode/launch.json) file or create new ones.

## Run web server

1. In vscode, press [run and debug](https://code.visualstudio.com/docs/editor/debugging#_run-and-debug-view) view, choose `Web Server` launch configuration (defined in [lanunch.json](.vscode/launch.json) file) and press `init debugger` (F5 key or green triangle).
1. Check server working ok going to http://127.0.0.1:5000/ in browser.

## Code styling

We follow [PEP-8](https://peps.python.org/pep-0008/) style guide conventions, and we use [autopep8](https://code.visualstudio.com/docs/python/editing#_formatting) as vscode formatter.

### Commit messages

All commits messages follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format.