# Gets run when the container is created
# Remove bashrc, bash_aliases, and bash_functions if they exist
rm -f /root/.bashrc
rm -f /root/.bash_aliases
rm -f /root/.bash_functions

ln -s /root/workspace/.devcontainer/.bashrc /root/.bashrc
ln -s /root/workspace/.devcontainer/.bash_aliases /root/.bash_aliases
ln -s /root/workspace/.devcontainer/.bash_functions /root/.bash_functions