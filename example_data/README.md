# Example Data

We generate the example data in `notebooks/demo.ipynb`, so there is nothing to download here. We use random seed 42 to get the same example each time.

The example has 20 made-up cars, two trucks per car, seven rail profiles, and two axles for each truck/rail combination. That gives us 560 rows.

We use Car, Truck, Axle, and Rail_Profile to identify each row. Empty_Truck_Hunted is a true/false value, and the hunting-speed columns use mph. The wear measurements and Eq Con 3mm values are random numbers with the column names our modeling code needs. They are not measurements from real equipment.

Follow `INSTALL.md` and run all cells in the demo. Keep the real project data in your local `data/` folder and out of GitHub.
