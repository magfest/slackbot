for d in */; do
    cd $d
    git fetch
    git pull
    cd ..
done
