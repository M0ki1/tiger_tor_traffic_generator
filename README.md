# TIGER: Tor Traffic Generator for Realistic Experiments
This repository presents the code for the functional prototype for Workshop on Privacy in the Eletronic Society (WPES) 2023.

* * **Paper available at:** [https://dl.acm.org/doi/pdf/10.1145/3603216.3624960](https://dl.acm.org/doi/pdf/10.1145/3603216.3624960)

* **Presentation at WPES'23:** ./TIGER_Tor_Traffic Generator_for_Realistic_Experiments.pptx


# If you make use of our work please cite our WPES'23 paper:
Daniela Lopes, Daniel Castro, Diogo Barradas, and Nuno Santos. 2023. TIGER: Tor Traffic Generator for Realistic Experiments. In Proceedings of the 22nd Workshop on Privacy in the Electronic Society (WPES '23). Association for Computing Machinery, New York, NY, USA, 147–152. https://doi.org/10.1145/3603216.3624960



## Some of the datasets produced by this framework were used in:
**SUMo: Flow Correlation Attacks on Tor Onion Sessions using Sliding Subset Sum:**
* Github repository: https://github.com/danielaLopes/sumo
* Paper: https://www.ndss-symposium.org/wp-content/uploads/2024-337-paper.pdf


## Project structure
* dataset_analysis/: Produces the results for the WPES '23 paper.
* framework/: Contains all the code to automate the production of datasets comprising real world Tor traffic with our custom clients and onion services. This framework is a working prototype implementing many aspects described on the paper.


## Setup
* Download Tor onion services mirrored pages from (onion_pages.tar.gz replaces onion_pages.tzst for compatibility): 