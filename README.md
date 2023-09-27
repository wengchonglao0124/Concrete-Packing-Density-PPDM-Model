# Concrete-Packing-Density-PPDM-Model

This project is my individual project that is developed for my thesis project in my civil engineering degree.

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


## Usage

This project aims to develop a 2D dry binary packing model for spheres in order to study for
the loosening, wedging and wall effects. Computational model for these experiments are developed and conducted to
understand the effect that packing density of the binary particles is depended on the size and
volume ratios of the particles in random packing.

A great understanding and knowledge of the particle packing is important and
useful to the concrete industries. A good packing of concrete ingredients can improve the strength,
durability and workability of the concrete member directly, which cannot be achieved by purely adjusting the water and cement ratio.


## Visuals
### Comprehensive Procedures:
<br/>

Menu control section for user's input
<img width="1526" alt="Screenshot 2022-11-04 at 1 10 50 am" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/5e39a9e2-5414-4f09-b8e2-437784adac92">

The PPDM in status (1)
<img width="1526" alt="Screenshot 2022-11-04 at 2 33 14 pm" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/ee62a3cb-834a-4bca-ba9e-1ef6a6ea7f21">

The PPDM in status (2)
<img width="1526" alt="Screenshot 2022-11-04 at 2 33 19 pm" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/7cccb05d-9fbc-4159-8eac-11b6d0b1ea88">

The PPDM in status (3) – (4)
<img width="1526" alt="Screenshot 2022-11-04 at 2 33 28 pm" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/01c1f802-7984-4bb0-b377-407d3f85b7f4">

The PPDM after status (4)
<img width="1526" alt="Screenshot 2022-11-04 at 2 33 34 pm" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/338551c8-c9bc-412a-bd92-cab463fefafc">

The PPDM in status (5) – (6)
<img width="1526" alt="Screenshot 2022-11-04 at 2 33 39 pm" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/ad312966-5889-4c5f-92b1-5f49322e14f8">

The PPDM in status (7)
<img width="1526" alt="Screenshot 2022-11-04 at 2 34 55 pm" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/15501110-355e-41ba-b0f3-86c0f08b1b11">

The PPDM after status (8)
<img width="1526" alt="Screenshot 2022-11-04 at 2 34 58 pm" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/c6037d12-3d49-4fb4-8ee1-4425842b5e59">

The PPDM in status (9) – (10)
<img width="1526" alt="Screenshot 2022-11-04 at 2 35 01 pm" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/4ad04f2b-4edb-4023-942b-ab354b7583b8">

The results will be printed in the Python programming console as well as being saved into the database .csv file for later analysis
<img width="323" alt="Screenshot 2022-11-04 at 1 41 09 am" src="https://github.com/wengchonglao0124/Concrete-Packing-Density-PPDM-Model/assets/85862169/66d3a686-6e51-4a0c-bb0f-a0cb91b71921">


## License
Developer: Weng Chong LAO

Project Name: Pygame Packing Density Model (PPDM)

<br/>
The University of Queensland

Faculty of Engineering, Architecture and Information Technology

Bachelor of Engineering (Honours)

Civil Engineering

<br/>
Thesis Project

CIVL4584 2022 Semester 2

Concrete Packing Density Experiment

Big Particle Dominated Case
