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


confirm() {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [y/N]} " response
    case "$response" in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}

confirm "Do you want to delete the gh-pages directory?" && rm -rf gh-pages