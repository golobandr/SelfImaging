
# Self Imaging
TbtCalc is a Python script for simulating grating diffraction by grating.


## Description of files/directory structure 

The source code folder `FresnelDiffraction` consists of a collection of python files (`*.py`-files), an accompanying input data files (provided as `.xlsx` files) are in `input_examples` folder.

The source code files are further described below. 

### Scripts of core functionalities located in the `FresnelDiffraction` folder: 

- `TbtCalc.py`: main script, that provides core functionality steps: data reading, calculation, visualization and saving output data.  
  - `DataStructures.py`: support file, where all data structures are described.
  - `Calculate.py`: support function file, with specific calculations used withing data reading procedure or during data processing.
- `ReadData.py`: function, used for reading input data files and forming input data structures, that are used as input parameters for simulations. This script is used to read Excel-based spreadsheet (examples are present in `inputs_example` folder).  
- `ProcessData.py`: main program function, where program parameters are provided as inputs along with several supporting functions. Can be used separately by providing correct input data structures with command `result = ProcessData.fromStructure(input)`. Note, data processing is done in parallel on the basis of system device number of cores, and input structures are divided to contain all needed data within one dataline: this would allow parallelization process.    
- `VisualizeData.py`: python function, used for output data visualization.  
  - `DisplayData.py`: support file, where all data used graphs are described.
- `SaveData.py`: python function, used for output data saving. Note, output structure is dumped in `result.dat` separately within main program `TbtCalc.py`. 

**Structure description `OutputData`:**  
* `is_ok` used to mark out that all mandatory data present (`boolean`)  
* `message` field used to store error message, must be empty at start of calculation (`string`)  
* `io` structure contains following fields  
  * `date`: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ calculation date/time (`string`) 
  * `filedir`:  $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ path to output file (`string`)  
  * `workdir`:  $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ path to output folder, can be different form `filedir`, if <br /> $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ several files are opened (`string`)
  * `filename`:  $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ data file name (`string`)  
  * `outputfile`:  $~~~~~~~~~~~~~~~~~~~~~~~~~~$ full path to the output data file (`string`)
* `copy_data` structure prepared to process data (`CopyData`)  
* `copy_beam` indicates if all data lines use the same beam parameters (`boolean`)
* `copy_beam_band` indicates if all data lines use the same beam band parameters (`boolean`)
* `copy_grating` indicates if all data lines use the same grating parameters (`boolean`)
* `data` data line array of structures (`OutputDataLine`)  
  * `is_ok` used to mark out that all mandatory data present (`boolean`)  
  * `message` field used to store error message, must be empty at start of calculation (`string`)  
  * `grating` structure contains following fields  
    * `slit`: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ grating slit description (`string` with three mandatory words) <br /> $~~$ 1. grating form factor: $~~~~~$ `1D` or `2D` <br /> $~~$ 2. grating transmission: $~~$ `amplitude` or `phase` <br /> $~~$ 3. pit structure: $~~~~~~~~~~~~~~~$ `square` - binary grating, <br /> $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ `cos` - cosine-like grating, <br /> $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ `lens` - used to simulate Shack-Hartmann wavefront sensor 
    * `period`:  $~~~~~~~~~~~~~~~~~~~~~~~~~~~$ period of the grating (`number`)  
    * `duty_factor`:  $~~~~~~~~~~~~~~~~~~~$ grating duty factor (`number`)
    * `depth`:  $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ slit depth to be used for _phase_ grating (`number`)  
    * `index`:  $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ material index of refraction ([`number`, `number`] where value with <br /> $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ index 1 is used in case of achromatic illumiation)
    * `phase_depth`: $~~~~~~~~~~~~~~~~~~~$ phase depth calculated on the basis index of refraction and <br /> $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ illumination wavelength (`number`)
    * `coefficients`: $~~~~~~~~~~~~~~~~~$ field reserved for fourier coefficients (`None`)
  * `beam` structure contains following fields  
    * `wavelength`: $~~~~~~~~~~~~~~~~~~~~~$ beam wavelength (`number`) 
    * `intensity`: $~~~~~~~~~~~~~~~~~~~~~~~$ beam intensity, used for output data visualization (`number`)  
    * `angle`: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ incidence angle (2D structure: `number`.`x`, `number`.`y`)  
    * `curvature`: $~~~~~~~~~~~~~~~~~~~~~~~$ wavefront curvature (2D structure: `number`.`x`, `number`.`y`)
    * `waist`: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ gaussian beam inverted radius <br /> $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$  (2D structure: `number`.`x`, `number`.`y`)
    * `aperture`: $~~~~~~~~~~~~~~~~~~~~~~~~~$ beam inverted aperture (2D structure: `number`.`x`, `number`.`y`)
    * `band`: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ beam bandwidth (`number`)
    * `aberration`: $~~~~~~~~~~~~~~~~~~~~~~$ <font color="red">!not implemented!</font> aberrations <br /> $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ (2D structure: `number`.`x`, `number`.`y`)
    * `coefficients`: $~~~~~~~~~~~~~~~~~~~$ <font color="red">!not implemented!</font> field reserved for fourier coefficients (`None`)
  * `psd` structure contains following fields  
    * `distance`: $~~~~~~~~~~~~~~~~~~~~~~~~~$ grating to PSD distance (`number`)  
    * `aperture`: $~~~~~~~~~~~~~~~~~~~~~~~~~$ measurement aperture of PSD (`number`)
    * `step`: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ lateral coordinate separation (`number`)
    * `div_factor`: $~~~~~~~~~~~~~~~~~~~~~~$ division parameter used to simulate result averaging by <br /> $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ the measurement system (`number`)  
  * `add` structure contains following fields  
    * `accuracy`: $~~~~~~~~~~~~~~~~~~~~~~~~~$ accuracy value for fourier analysis (`number`)  
    * `dependency`: $~~~~~~~~~~~~~~~~~~~~~~$ planed for a future usage (`number`)
    * `debug`: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ indicator used to save internal data (`boolean`)
    * `save`: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$  indicator used to save generated figures (`boolean`)
  * `dependencies` planed for a future usage (`None`)
  * `start` calculation start time (`None`)
  * `end` calculation finish time (`None`)
* `dependencies` list of dependencies for visualization (`boolean`)

### Installation instructions 

Included Python scripts do not require any installation, just copy to the working folder.


### Program execution

To set up a simulation, an input `TbtCalc` script must be started which allows to enter input data via GUI. The execution is started in automatic regime if folder `data_inputs` is in `FresnelDiffraction` folder. The input parameters are read from the “Grating”, “Beam”, “Beam.X”, “Beam.Y”, “Psd”, “Add” and "Dependencies" tabs of the Excel file and are organized structlike columns on the basis of `OutputData` structure. At the start of program execution, the input data file `<filename>.xlsx` is copied into the otput folder where calculation result will be saved as `result.dat` file also.


### Example of input data files

`input_examples\1.xlsx`: Basic file used to estimate division parameter sys.dsdp  
`input_examples\2.xlsx`: Files used to simulate grating to sample distance effect on the far-field patterns  
`input_examples\3.xlsx`: Files used to simulate pump to probe ratio effect on far-field patterns formation

