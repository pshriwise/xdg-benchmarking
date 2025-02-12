set -ex

git clone git@github.com:pshriwise/xdg-benchmarking --branch gh-pages --single-branch gh-pages
cd gh-pages

# Copy the new files
cp -r ../index.html ../dashboards/ .

# Add and commit
git add index.html dashboards/
git commit -m "Update the dashboard"
git push origin gh-pages

cd ..

rm -rfi gh-pages