# quickattach

A very simple plugin for the zim personal wiki ([https://zim-wiki.org/]) to add attachments from the command line. I use it in a cron job to add automatically jots taken on a tablet to my daily notes in zim. 

The usage is quite simple, here some examples:
```
zim --plugin quickattach --attachments=/a/b                                            adds the attachments in the given directory to the first notebook found, at the today page from the journal
zim --plugin quickattach --attachments=/a/b --remove                                   adds the attachments in the given directory to the first notebook found, at the today page from the journal. Deletes the attachments from the origin directory
zim --plugin quickattach --attachments=/a/b --notebook=MyNotebook                      adds the attachments in the given directory to the notebook MyNotebook, at the today page from the journal
zim --plugin quickattach --attachments=/a/b --basename='node1:node2' --name='node3'    adds the attachments in the given directory to the first notebook found, at the page node3 referenced by node1:node2:node3
```

Please notice that if a page is missing for your zim notebook, it will be created with a default name. 

To install this plugin to your linux based zim installation, add the python file to ~/.local/share/zim/plugins on linux. Restart your zim desktop, the plugin should be automatically added to your install. You don't need to activate it, thus activating it won't harm either. (Windows will follow soon)

