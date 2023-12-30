PROJECT=`basename "$PWD"`

echo 1. Change the default name template_python to $PROJECT

to_replace='s/template_python/'$PROJECT'/g'
sed -i -e $to_replace *.*

echo 2. Delete .git/ folder

rm -r .git/

echo 3. Enter the new origin \(e.x.: git@github.com:my_user/my_repo.git\)

read new_remote
len_remote=${#new_remote}

if [ $len_remote -lt 8 ]; then
    echo "Skip: invalid name"
else
    git init
    git remote add origin $new_remote
    git add --all :!from_template_to_project.sh
    git commit -m "chore: Initial project files"
    git push origin HEAD
fi

echo 4. Delete this script
rm from_template_to_project.sh
