import Flatten from '@flatten-js/core';
import { MiniProgram, SearchRange } from './mini-solve';


const MOCK_TRIANGLE = (known: MiniProgram.Env) => {
    if (['X', 'Z'].every(k => known[k])) {
        let x = known['X'], z = known['Z'], d = x.distanceTo(z)[0],
            c1 = Flatten.circle(x, d),
            c2 = Flatten.circle(z, d);

        return new MiniProgram([
                [0, 'Y', _ => c1.intersect(c2)]
            ],
            _ => 0
        );
    }
    else throw new MiniProgram.MissingInputs();
}

const MOCK_SQUARE = (known: MiniProgram.Env) => {
    if (['A', 'B'].every(k => known[k])) {
        var a = known['A'], b = known['B'], dist = a.distanceTo(b)[0];
            
        return new MiniProgram([
                [1, 'C', env => 
                            SearchRange.circleAroundPoint_maybe(
                                Flatten.circle(env['B'], dist), env['C'])],
                [0, 'D', env =>
                            Flatten.circle(env['C'], dist)
                                .intersect(Flatten.circle(env['A'], dist))]
            ],
            env =>
                (env['D'].distanceTo(env['A'])[0] < 1 ? 10 : 0) + // penalty
                (env['D'].distanceTo(env['B'])[0] < 1 ? 10 : 0) + // penalty
                Math.abs(env['A'].distanceTo(env['C'])[0] - env['B'].distanceTo(env['D'])[0])
        );   
    }
    else throw new MiniProgram.MissingInputs();
}


export default {
    triangle: MOCK_TRIANGLE,
    square: MOCK_SQUARE
} as {[name: string]: MiniProgram.Expr<MiniProgram>}