# cosmic_calibration_mapping
A project to map the observations that have gone through the COSMIC backend on the VLA based on the grade of the calibration.

Start out with the following:
- Packages and package versions:
  - astropy (5.1), json5 (0.9.6), matplotlib (3.7.0), numpy (1.23.5), pandas (1.5.3), seaborn (0.12.2), tqdm (4.64.1)
- Two .pickle files:
  - One with the calibration grade information and the file paths (file irl)
  - One with the observation information

Outputs:
- Figures:
  - One plot showing the coordinates of each of the observations. The data points will have varying hues and sizes depending on the grade of the calibration.
  - Three .pkl files
      - Same information as the calibration grade information .pickle file but with the irl string broken up to show the data set ID and the scan ID
      - Same information as the observation information .pickle file but with the metadata string broken up by the dictionary terms and put into indivudal columns
      - Matching the rows in the observation information .pickle file with the information in the calibration grade .pickle file so that the equatorial coordinates and the overall calibration grades for the same observation match
