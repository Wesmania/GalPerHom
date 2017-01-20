Galaxy classification with the use of persistent homologies
===========================================================

Installation
------------

We use Python3, OpenCV, matplotlib and or-tools::

   pip3 install -r requirements.txt

Usage
-----

#. Create a directory *kaggle/*
   in the project directory and place unzipped files from Kaggle inside it:
   *images_training_rev1/* and  *training_solutions_rev1.csv*.
   Download them from https://www.kaggle.com/c/galaxy-zoo-the-galaxy-challenge/data

#. Choose some number of galaxies to classify. We will classify them as
   *smooth* vs. *having features/disk*, we discard the third Galaxy Zoo main class, ie. *star/artifact*.::

    python3 src/choose_galaxies.py

#. Use the generated file with chosen galaxies' ids to copy them into the *train* directory::

    python3 src/prepare_images.py

#. Then generate the persistence diagram. You may use the *radial*, *brightness* or *level* filtration,
   but the first one is most efficient. This may take some time::
     
    src/make_diagrams.sh radial

#. Now you can check how well a kNN classification using the generated diagrams performs::

    python3 src/test_classify.py

#. All Python scripts listed above have adjustable parameters, which are not discussed here.
   One may learn about them calling the scripts with an *-h* flag.

#. Our result for the best parameters set can be found in *results.txt*.
   These parameters are set as default in the scripts.
    
