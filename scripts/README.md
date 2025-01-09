# How to run the scripts

## 0. Setup
- If this is the first time you're pushing to git, then run these following commands
    
    ```bash
    git config --global user.name "Your Name"
    git config --global user.email "your_email@example.com"
    ```
- Give execution permissions to the scripts
    - Windows (Open Powershell as administrator)
        ```bash
        Set-ExecutionPolicy RemoteSigned
        ```
    - Unix
        ```bash
        chmod +x *.sh
        ```
- Download chromedriver and add it to your `.env` file. A sample of the `.env` file is available as `sample.env`

- Include the list of subreddits to scrape in `subreddits.txt` file

- Install the dependencies in `requirements.txt`
    ### [Optional] Create a virtual environment
    ```bash
    python -m venv venv
    ```
    ### Activate the virtual environment
    - Windows
        ```bash
        venv\Scripts\activate
        ```
    - Unix
        ```bash
        source venv/bin/activate
        ```
```bash
pip install -r requirements.txt
```

## 4. Run the scripts

```bash
cd scripts/
python main.py -d month 

# or
python create_graphs.py -p <input_path> -ts day -o <output_path>
```

The options for `main.py` are:
```
-d --duration: The duration for which the posts should be scraped. The options are: hour, day, week, month, year, all
-ng --no-graphs: If this flag is set, then the graphs will not be generated
```

The options for `create_graphs.py` are:
```
-p --path: The path to the folder containing the data
-ts --time-slice: The time scale for which the graphs should be generated. The options are: hour, day, week, month, year, all
-o --output: The path to the folder where the graphs should be saved
```

## 2. Check the results

There should be folders for each subreddit in `data/` and `graphs/` or the output path specified in the command line arguments.

## 3. Check if its pushed to the repo

```bash
git log
```

## Final notes
- Run it on headless mode initially
- If it the amount of posts are too low in number, then try running it without headless mode (can be removed from options in `constants.py`).
