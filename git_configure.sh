#!/usr/bin/env zsh

#cat > gitconfig <<EOM
#[filter "strip-notebook-output"]
#	clean = "jupyter nbconvert --clear-output --to=notebook --stdin --stdout --log-level=INFO"
#EOM

git config --local include.path ../.gitconfig

