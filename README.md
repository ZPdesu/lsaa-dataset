## Large Scale Architectural Asset Dataset (LSAA)
![Python 3.7](https://img.shields.io/badge/python-3.7-green.svg?style=plastic)
![License CC](https://img.shields.io/badge/license-CC-green.svg?style=plastic)
![Photospheres 78K](https://img.shields.io/badge/photospheres-78K-green.svg?style=plastic)
![Facades 200K](https://img.shields.io/badge/facades-200K-green.svg?style=plastic)

![Dataset image](./facades_windows.png)

Large Scale Architectural Asset Dataset (LSAA) is  a dataset of architectural assets from a large-scale panoramic image collection:

> **Large Scale Architectural Asset Extraction from Panoramic Imagery**<br>
> Peihao Zhu (KAUST), Wamiq Reyaz Para (KAUST), Anna Fruehstueck (KAUST), John Femiani (Miami University in Oxford Ohio), Peter Wonka (KAUST)<br>
> https://arxiv.org/...


The dataset consists of 78,377 photospheres and 199,723 extracted facade images including the contained windows, doors, and balconies together with descriptive attributes.

For inquiries, please contact peihao.zhu@kaust.edu.sa

## Licenses
The dataset (including JSON, CSV metadata, download script, and documents) is made available under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). You can **use, redistribute, and adapt it for non-commercial purposes**, as long as you (a) give appropriate credit by **citing our paper**, (b) **indicate any changes** that you've made, and (c) distribute any derivative works **under the same license**.

* [https://creativecommons.org/licenses/by-nc-sa/4.0/](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Overview
Annotation files are hosted on Google Drive:

| Path | Size | Files | Format | Description
| :--- | :--: | ----: | :----: | :----------
| [annotations](https://drive.google.com/open?id=1hnMSMuA4fY28rqkI64asGmhUWKg_OMc5) | 860.2 MB | 13 | | Main folder
| &boxvr;&nbsp; [Properties200K.csv](https://drive.google.com/open?id=1XR5CNsQGg9803yJ_YYtcchgZlXizv_gx) | 77.1 MB | 1 | CSV | 
| &boxvr;&nbsp; [Properties23K.csv](https://drive.google.com/open?id=1ghPJjIHrao77-T8tvTlVn9cp9cKhZeLf) | 9.2 MB | 1 | CSV | 
| &boxvr;&nbsp; [panorama_rectification.json](https://drive.google.com/open?id=12cOD19PeknR8uD7ePpJ74fOkVszQnj0G) | 138.6 MB | 1 | JSON | 
| &boxvr;&nbsp; [facade_detection_result.json](https://drive.google.com/open?id=195uDy_l3dWbX8kVepHkcnpfKbq4ChiGF) | 85.2 MB | 1 | JSON | 
| &boxvr;&nbsp; [window](https://drive.google.com/open?id=1AAp8TrHhAHvjHC6_XXQtiMNtmE9rVyoa) | 419.1MB | 3 | | 
| &boxv;&nbsp; &boxvr;&nbsp; [window_all.csv](https://drive.google.com/open?id=1ZzU1K6J-V4fA1lFJQZvHxs1pAgeGvDzJ) | 147.0MB | 1 | CSV | 
| &boxv;&nbsp; &boxvr;&nbsp; [window_filtered.csv](https://drive.google.com/open?id=1B9VRjIjmjwinWSCtdasHkN5cIg5dr4Dd) | 44.4 MB | 1 | CSV | 
| &boxv;&nbsp; &boxur;&nbsp; [window_detection.json](https://drive.google.com/open?id=17BVv-83BZrKj6rMe8FJyzTBiI58sE35e) | 227.7 MB | 1 | JSON | 
| &boxvr;&nbsp; [door](https://drive.google.com/open?id=1Rojo5dhgLejOhznrHijUcnMcFqKofEeK) | 23.1MB | 3 | | 
| &boxv;&nbsp; &boxvr;&nbsp; [door_all.csv](https://drive.google.com/open?id=1pVBiEmKPDelo_ThiSMTeWgqOwUzcIyRL) | 8.0MB | 1 | CSV | 
| &boxv;&nbsp; &boxvr;&nbsp; [door_filtered.csv](https://drive.google.com/open?id=102pCJ9VczUHMfOGPXOhbMnql6KJ19paL) | 5.0 MB | 1 | CSV | 
| &boxv;&nbsp; &boxur;&nbsp; [door_detection.json](https://drive.google.com/open?id=1S48sCwfWYHX6-XkhMAvtkdRrNXJMA_xc) | 10.2 MB | 1 | JSON | 
| &boxur;&nbsp; [balcony](https://drive.google.com/open?id=13qt-1BPgDp7WBJFs9YCDWHTcZGtX2mXL) | 107.8MB | 3 | | 
| &ensp;&ensp; &boxvr;&nbsp; [balcony_all.csv](https://drive.google.com/open?id=1TqoKAbbriRoKrdm2I6ODk5MUfcmMtFw9)| 40.7MB | 1 | CSV | 
| &ensp;&ensp; &boxvr;&nbsp; [balcony_filtered.csv](https://drive.google.com/open?id=1aTpfpy7Nii3x8il4ieiBzZrI2fjgYkav)| 15.2MB | 1 | CSV | 
| &ensp;&ensp; &boxur;&nbsp; [balcony_detection.json](https://drive.google.com/open?id=1ymygF05ZbiJ4faMJQqDODZDefFVX-HjI) | 51.9 MB | 1 | JSON | 



