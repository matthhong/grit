# GRIT: A Graphical Route Inspection Tool for the Perseverance Rover.

Mars Rover Planners are studying the potential for AutoNav Monte Carlo simulations to help them assess the risks of extended automatic navigation over challenging topography. GRIT summarizes thousands of simulated AutoNav runs for Rover Planners to investigate and understand potential failure cases.

## Setting Up the Local Environment

### Installing Node.js with `n`

We will use the Node version manager `n` to install the required node version:

1. On Linux and Mac OS, install the `n` package manager:
    ```bash
    curl -L https://bit.ly/n-install | bash
    ```
2. Install and use the specific Node.js version required (18.17.1) by running:
    ```bash
    n 18.17.1
    ```
3. Verify that the correct version of Node.js is installed:
    ```bash
    node --version
    ```
    The output should be `v18.17.1`.

### Installing Dependencies

To install project dependencies, run the following commands in the root directory:
```bash
npm install
npm install --save node-releases
```

These steps will install dependencies locally into a `node_modules` directory.

## Running the Application

The frontend code is written using the Svelte framework. Run the following command in the root directory to compile the Svelte code into JavaScript code:

```bash
npm run build
```

To start the application, run the following command:

```bash
npm run dev
```

and finally, navigate to the following URL: 

http://localhost:5173/?data=aug20-1

## Contributors

- [Matt-Huen Hong](https://www.mattheun.com/), UNC Chapel Hill
- [Racquel Fygenson](https://www.racquelfygenson.com/), Northeastern University
- Isabel Li, Art Center College of Design
- [Kristopher Wehage](https://robotics.jpl.nasa.gov/who-we-are/people/kristopher_wehage/), Jet Propulsion Laboratory, California Institute of Technology
- [Scott Davidoff](https://scottdavidoff.com/), Jet Propulsion Laboratory, California Institute of Technology
- Maggie Hendrie, Art Center College of Design
- [Hillary Mushkin](https://www.hillarymushkin.com/), California Institute of Technology
- [Santiago Lombeyda](https://www.lombeyda.com/), California Institute of Technology

This application was developed as part of the [Caltech/JPL/ArtCenter Data to Discovery (D2D) Summer Data Visualization Program](https://datavis.caltech.edu/). In the 10-week D2D program, visualization faculty at Caltech, JPL and Art Center College of Design work with talented design and computer science student interns in collaboration with Caltech and JPL research groups. Together, teams develop custom-built interactive data visualization tools for science and engineering research projects using the state-of-the-art techniques. Read about [past projects, program structure, and funding available](http://datavis.caltech.edu/)

## License
   
   Copyright (c) 2023-24 California Institute of Technology ("Caltech"). U.S. Government sponsorship acknowledged.

   All rights reserved.

   Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

   - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
   - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
   - Neither the name of Caltech nor its operating division, the Jet Propulsion Laboratory, nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTER- RUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
