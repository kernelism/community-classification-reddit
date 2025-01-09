#!/bin/bash
cd ..

# Add the specific folders to the staging area
git add data/* graphs/*

# pull changes
git pull origin master

# Commit the changes with a message
git commit -m "Updated data and graphs folders"

# Push the changes to the remote repository
git push origin master
