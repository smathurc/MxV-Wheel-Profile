# Data

Put the approved partner data here. Git tracks only this README in `data/`.

In the private **-MxV-Wheel-Profile** Teams channel, open **Shared → Documents → Data**. Download the workbook, merged CSV and complete `Profiles` folder, and extract them into this folder. Keep the original names and folder structure. `INSTALL.md` shows the full layout.

The demo generates 560 synthetic rows in `notebooks/demo.ipynb` with seed
42. It uses 20 invented cars, two trucks per car, seven rail profiles, and
two axles per truck.

Our `.gitignore` keeps everything in this folder except this README out of GitHub. Check `git status` before committing.
