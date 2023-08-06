# Gets run when the container is created
ln -s ~/workspace/.devcontainer/.bashrc ~/.bashrc
ln -s ~/workspace/.devcontainer/.bash_aliases ~/.bash_aliases
ln -s ~/workspace/.devcontainer/.bash_functions ~/.bash_functions

chmod +x ~/workspace/.devcontainer/.bashrc

cd ~/workspace
npm i
