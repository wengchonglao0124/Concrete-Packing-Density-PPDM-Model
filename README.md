# Concrete-Packing-Density-PPDM-Model

This project is my individual project that is developed for my thesis project in my civil engineering degree.

This project aims to develop a 2D dry binary packing model for spheres in order to study for
the loosening, wedging and wall effects. Computational model for these experiments are developed and conducted to
understand the effect that packing density of the binary particles is depended on the size and
volume ratios of the particles in random packing.

Pygame Packing Density Model (PPDM) is a 2D computational model with a binary mixture of the larger grains and smaller grains,
it is a model for predicting the packing density in random particle packing.
The PPDM implements the game engine called Pygame in Python programming language,
it can simulate the collision and physical movements of the particles.

The environment of the PPDM is composed of a rigid container,
a binary mixture of the larger grains and smaller grains are generated randomly inside the container.
After a mixing process (vibration) and particle settlement, the packing density of the system,
number of larger grains and number of smaller grains can be measured as well as
the volumetric fractions of either the larger grains or the smaller grains.

<img width="1526" alt="Screenshot 2022-11-04 at 1 11 47 am" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/d6076c68-6650-4996-8644-26cb2b042ed7">

The PPDM has a systematic procedure to predict the packing density of the random particle packing.
There are ten different statuses used to define and control the process of the PPDM,
they are design for the larger grains dominated situation:
(1) Start; (2) Generate smaller grains; (3) Vibration1; (4) Vibration2; (5) Elimination1;
(6) Elimination2; (7) Generate smaller grains to fill for fully packed; (8) Elimination3; (9) Measurement; (10) End.


# Usage

A great understanding and knowledge of the particle packing is important and
useful to the concrete industries. A good packing of concrete ingredients can improve the strength,
durability and workability of the concrete member directly, which cannot be achieved by purely adjusting the water and cement ratio.


# About The Project
