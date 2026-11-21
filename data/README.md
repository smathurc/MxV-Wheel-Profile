# Data

Every notebook reads its inputs from this folder. We keep the partner data out of GitHub, so only this README is in the repository. Download the data separately and put it here.

In the private **-MxV-Wheel-Profile** Teams channel, open **Shared → Documents → Data**. Download the workbook, merged CSV and complete `Profiles` folder, and extract them into this folder. Keep the original names and folder structure. `INSTALL.md` shows the full layout.

The demo does not use this folder. We generate its example data in `notebooks/demo.ipynb` with random seed 42, so there is nothing to download for it. The example has 20 made-up cars, two trucks per car, seven rail profiles, and two axles for each truck/rail combination. That gives us 560 rows. They are not measurements from real equipment.

Our `.gitignore` keeps everything in this folder except this README out of GitHub. Check `git status` before committing.
