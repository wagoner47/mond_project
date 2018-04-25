.. _install:

.. role:: repo(file)

Installation
============

First, clone the repo from github::
        
        git clone https://github.com/wagoner47/mond_project.git
for HTTPS or::
        
        git clone git@github.com:wagoner47/mond_project.git
for SSH.

Now change to the root :repo:`mond_project` directory::
        
        cd mond_project

Finally, use the :file:`setup.py` script::
        
        python setup.py install
Standard command line options are available, such as :code:`--prefix=`. However, an additional option should also be given, :code:`--api-key=`, followed by the Illustris API key to use (you must first register with Illustris for this). This will create/modify a configuration file which is used by the code with the API key stored. This ensures that the user does not need to continually input the API key or have an environment variable which may be different on different operating systems.
