# Automated Geometry Solver

The automated geometry solver produces 2D diagrams from a set of geometric constraints.

The engine is implemented in Python and uses the Soufflé Datalog engine for deductive
inference. It then employs SciPy and SymPy for the numerical optimization problem.

### Prerequisites

 * Python 3.9
   * pyparsing
   * scipy
   * sympy
   * shapely
   * flask
 * Node.js 16.x
   * (+ NPM)
 * Soufflé
   * (as a binary called `souffle`, in your path)

For serving on the Web:
 * uWSGI
   * Usually requires pcre and libssl, so first `apt install libpcre3 libpcre3-dev libssl-dev`
   * `pip install uwsgi`

### Setup Instructions

```
cd WebApp/UI
npm i
npm run build
```
