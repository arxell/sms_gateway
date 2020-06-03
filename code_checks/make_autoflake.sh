#!/bin/bash
echo "Running autoflake..."

highlight() {
  (
    set +e
    tput bold
    echo -n $1
    tput sgr0
    exit 0
  ) 2> /dev/null # ignore tput warnings in case if TERM is undefined
}

AUTOFLAKE=autoflake
AUTOFLAKE_CHECK_OPTION='--check'
while getopts "fb:" opt; do
  case $opt in
    b) AUTOFLAKE="$OPTARG"
      shift
    ;;
    f) AUTOFLAKE_CHECK_OPTION=' '
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
    ) | grep '.py$' | grep -v 'src/api/users/views.py\|src/api/users/views_sportcast.py\|src/api/staff/views.py\|src/api/agents/views.py'
  )
  num_files_found=$(echo $FILES_ARG | wc -w | tr -d ' ')

  echo "No files to autoflake provided. Running for changes in your branch ($(highlight $num_files_found) files)"

  if [[ ! $FILES_ARG ]]; then
    echo "No python files changed in your branch 😶"
    exit
  fi
fi

if ${AUTOFLAKE} -i $AUTOFLAKE_CHECK_OPTION --ignore-init-module-imports --remove-all-unused-imports --remove-unused-variables --exclude *proto*,src/conf,src/api/users/views.py,src/api/users/views_sportcast.py,src/api/staff/views.py,src/api/agents/views.py -r $FILES_ARG; then
  highlight "Autoflake says: "
  echo " ❆ ❄️  ❆"
else
  exit
fi
