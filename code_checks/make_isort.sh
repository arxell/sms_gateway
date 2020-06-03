#!/bin/bash
set -e
echo 'Running isort...'

highlight() {
  (
    set +e
    tput bold
    echo -n $1
    tput sgr0
    exit 0
  ) 2> /dev/null # ignore tput warnings in case if TERM is undefined
}


ISORT=isort
ISORT_FIX_OPTION='--check-only'
while getopts "fi:" opt; do
  case $opt in
    i) ISORT="$OPTARG"
      shift
    ;;
    f) ISORT_FIX_OPTION=''  # fix by default
      shift
    ;;
  esac
done

FILES_ARG=$*

if [[ ! $FILES_ARG ]]; then
  FILES_ARG=$(
    (
      git diff --name-only --diff-filter=d $(git merge-base HEAD origin/develop) HEAD;
      git diff --name-only --diff-filter=d;
      git diff --cached --name-only --diff-filter=d;
    ) | grep -vE '/(proto)/' | grep '.py$'
  )
  num_files_found=$(echo $FILES_ARG | wc -w | tr -d ' ')

  echo "No files to isort provided. Running for changes in your branch ($(highlight $num_files_found) files)"

  if [[ ! $FILES_ARG ]]; then
    echo "No python files changed in your branch 😶"
    exit
  fi

fi

if $ISORT --settings-path setup.cfg $ISORT_FIX_OPTION -rc $FILES_ARG; then
  highlight "Isort says: "
  echo "💞 🥰  💞"
else
  exit 1
fi
