# load environment variables
printenv | sed 's/^\(.*\)$/export \1/g' | grep -E "^export PG" > /src/project_env.sh
echo "echo ENV variables are loaded" >> /src/project_env.sh
chmod 777 /src/project_env.sh
echo "ENV load file created"

