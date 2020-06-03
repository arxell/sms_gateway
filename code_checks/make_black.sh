#!/bin/bash
echo "Running black..."

highlight() {
  (
    set +e
    tput bold
    echo -n $1
    tput sgr0
    exit 0
  ) 2> /dev/null # ignore tput warnings in case if TERM is undefined
}

BLACK=black
BLACK_CHECK_OPTION='--check'
while getopts "fb:" opt; do
  case $opt in
    b) BLACK="$OPTARG"
      shift
    ;;
    f) BLACK_CHECK_OPTION=' '
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

  echo "No files to black provided. Running for changes in your branch ($(highlight $num_files_found) files)"

  if [[ ! $FILES_ARG ]]; then
    echo "No python files changed in your branch 😶"
    exit
  fi
fi

${BLACK} $BLACK_CHECK_OPTION --config pyproject.toml $FILES_ARG;
