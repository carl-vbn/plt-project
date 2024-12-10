# Code Generation

## Team Members
* Carl von Bonin (cv2546)
* Adheesh Kadiresan (ak4907)

## Setup using Docker
### Running the code generation
1. `cd` into `code-generation` (this folder)
2. Either: 
   1. Run `./run.sh <input file name> <output directory name>`

3. Or: 
   1. Run `docker build -t code-generation .`
   2. Run `docker run -it --rm -v .:/app code-generation:latest <input file name> <output animation folder name>`
      1. For example, `docker run -it --rm -v .:/app code-generation:latest examples/test_full.minm full_anim`

### Visualizing the animation
1. Still in the `code-generation` folder, run `./server.sh`
2. Navigate to `http://localhost:8000/executor.html` in your browser
3. Type in the name of the output directory you specified in step 2 of the previous section
4. Click `Start Animation`

## Setup using Python
*This assumes Python is installed and on the PATH*

### Running the code generation
1. `cd` into this folder `code-generation`
2. Run `python main.py <input file name> <output animation folder name>` in this folder

### Visualizing the animation
1. `cd` into the `code-generation` folder
2. Run `python -m http.server 8000`
3. Navigate to `http://localhost:8000/executor.html` in your browser
4. Type in the name of the output directory you specified in step 2 of the previous section
5. Click `Start Animation`


### Video Link
https://youtu.be/3NUWdBl_uIc