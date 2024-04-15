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

## License
   
   Copyright (c) 2023-24 California Institute of Technology (“Caltech”). U.S. Government sponsorship acknowledged.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
